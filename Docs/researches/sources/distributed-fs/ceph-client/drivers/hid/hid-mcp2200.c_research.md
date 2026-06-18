# sources/distributed-fs/ceph-client/drivers/hid/hid-mcp2200.c

## Purpose

`hid-mcp2200.c` is the HID-side GPIO driver for Microchip MCP2200 USB-to-GPIO bridges. It binds the Microchip VID/PID, starts raw HID I/O without exposing a normal hid-input device, and registers an eight-line sleeping `gpio_chip`. GPIO reads are implemented through the device's `READ_ALL` command; GPIO writes and direction changes are implemented through raw output reports that match the MCP2200 HID application note.

## Important APIs, Types, and Functions

- `struct mcp2200` stores the HID device, serialization mutex, completion used to wait for command responses, cached GPIO direction/value/input state, cached baud/reset/alternate-pin configuration, a shared 16-byte report buffer, command status, and embedded `gpio_chip`.
- Packed command/response layouts (`mcp_set_clear_outputs`, `mcp_configure`, `mcp_read_all`, `mcp_read_all_resp`) model the device's fixed 16-byte HID reports.
- `mcp_cmd_read_all()` sends `READ_ALL`, waits up to four seconds for `raw_event`, and returns the parsed status.
- GPIO callbacks `mcp_get[_multiple]`, `mcp_set[_multiple]`, `mcp_get_direction`, `mcp_direction_input`, and `mcp_direction_output` adapt Linux gpiolib operations to MCP2200 reports.
- `mcp_set_direction()` issues `CONFIGURE`, preserving baud/reset/alternate-option bytes read from the device and clearing alternate pin functions when a pin is turned into GPIO.
- `mcp2200_raw_event()` receives interrupt input reports, updates cached state on `READ_ALL`, and completes waiters.
- `mcp2200_probe()` parses and opens HID hardware, initializes state, and registers the gpiochip; `mcp2200_remove()` closes/stops HID hardware.

## Control Flow

Probe allocates `struct mcp2200`, parses reports, starts and opens HID hardware, initializes the mutex/completion, stores driver data, copies `template_chip`, and registers the gpiochip with device-managed lifetime. The driver uses a single shared output buffer guarded by `mcp->lock`, while response completion happens asynchronously in `raw_event`.

Reads call `mcp_cmd_read_all()`, which reinitializes the completion, sends a `READ_ALL` output report, then waits. The raw-event path validates the first byte, copies input value and configuration fields into `mcp2200`, sets `status`, and completes. Writes compute a new output bitmap from the caller mask/bits and send `SET_CLEAR_OUTPUTS` with complementary set/clear masks, updating the cached output value only on a full-size transfer. Direction changes first refresh device configuration, then send `CONFIGURE`; because the configure command resets output levels, the driver replays cached output values afterward.

## State and Persistence Behavior

The persistent state is entirely per-device and held in `struct mcp2200`. `gpio_dir`, `gpio_val`, `gpio_inval`, baud bytes, reset output value, alternate-pin flags, and alternate options are cached from the last `READ_ALL`/`CONFIGURE`. The physical device persists GPIO direction/default configuration across the configure command; output state may be cleared by configure, so the driver explicitly restores it. There is no file-backed persistence.

## Dependencies and Integration Points

The driver integrates HID core (`hid_parse`, `hid_hw_start`, `hid_hw_open`, `hid_hw_output_report`, `raw_event`), gpiolib (`devm_gpiochip_add_data`, `gpiochip_get_data`), completions, mutexes, and Microchip identifiers from `hid-ids.h`. `gc.can_sleep = true` advertises that GPIO operations can block on USB/HID response latency.

## Risks and Edge Cases

- `mcp_get()` ignores the return value of `mcp_get_multiple()`, so timeout or I/O failure is reported as a low value to simple single-line callers.
- `mcp_set_direction()` sends `sizeof(struct mcp_set_clear_outputs)` for a `struct mcp_configure`; those structures are both 16 bytes today, but the mismatch is fragile.
- The shared report buffer relies on `mcp->lock`; any future command path that bypasses it could corrupt in-flight requests.
- Response correlation is based only on command byte and the one-command-at-a-time convention. Stray or delayed input reports set `status = -EIO`.
- Direction changes perform a full device configure and may briefly glitch outputs despite the replay step.

## Test Signals

Useful tests include gpiochip registration/removal with HID open/close failures, `READ_ALL` timeout and invalid-response handling, set/clear bitmap correctness for single and multiple GPIO writes, direction changes on pins with alternate functions, output replay after configure, and ensuring GPIO calls tolerate sleeping contexts. Hardware tests should verify no output glitches beyond the MCP2200 configure behavior and that alternate pins TXLED/RXLED/USBCFG/SSPND are released when used as GPIO.
