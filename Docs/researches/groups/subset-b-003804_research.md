# subset-b-003804 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-mcp2200.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-mcp2200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-mcp2221.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-mcp2221.c

## Purpose

`hid-mcp2221.c` drives the Microchip MCP2221A HID USB bridge and exposes it as a Linux I2C/SMBus adapter, optional four-line GPIO controller, and optional IIO voltage device for ADC/DAC functions. It serializes all HID command/response traffic because MCP2221 responses do not carry enough transaction identity to safely pipeline commands.

## Important APIs, Types, and Functions

- `struct mcp2221` is the central device state: HID device, I2C adapter, mutex, completion, init delayed work, RX/TX buffers, response status, I2C clock divisor, GPIO chip, GPIO index/direction/mode state, and optional IIO channel/ADC/DAC state.
- `mcp_send_report()` and `mcp_send_data_req_status()` are the synchronous HID command primitives.
- I2C path: `mcp_i2c_xfer()`, `mcp_i2c_write()`, `mcp_i2c_smbus_read()`, `mcp_chk_last_cmd_status[_free_bus]()`, `mcp_cancel_last_cmd()`, and `mcp_set_i2c_speed()`.
- SMBus path: `mcp_smbus_xfer()` and `mcp_smbus_write()` implement quick, byte, word, block, I2C-block, process-call, and block-process-call transactions.
- GPIO path, gated by gpiolib: `mcp_gpio_read_sram()`, `mcp2221_check_gpio_pinfunc()`, `mcp_gpio_get/set`, `mcp_gpio_direction_input/output`, and `mcp_gpio_get_direction()`.
- `mcp2221_raw_event()` decodes all supported input reports, translates MCP status bytes to Linux errors, copies received I2C data, updates GPIO/IIO state, and completes waiters.
- IIO path: `mcp_iio_channels()`, `mcp_init_work()`, `mcp2221_read_raw()`, and `mcp2221_write_raw()` expose ADC raw reads, DAC writes, and scale values.
- `mcp2221_probe()` registers HID, I2C, GPIO, and scheduled IIO setup; `mcp2221_remove()` cancels pending IIO work.

## Control Flow

Probe parses and opens HID, installs a managed HID unregister action, starts I/O, clamps the `i2c_clk_freq` module parameter to 50-400 kHz, sends an I2C speed command, then registers an `i2c_adapter`. If gpiolib is reachable, it creates a sleeping GPIO chip and optionally forces non-GPIO alternate pin functions into GPIO input mode when IIO is disabled or `gpio_mode_enforce` is set. If IIO is reachable and GPIO mode is not enforced, delayed work reads SRAM/flash configuration, discovers ADC/DAC channels from GP1-GP3 modes, and registers an IIO device.

I2C and SMBus transfers power the HID device to `PM_HINT_FULLON`, lock the single command mutex, build reports in `txbuf`, and wait on `wait_in_report`. Reads first command the chip to perform the slave read, then repeatedly send `MCP2221_I2C_GET_DATA` until `rxbuf_idx` reaches the requested length. Final bus status is queried and failures issue a cancel to free the bus. Raw events are the only place where response status and payloads are interpreted.

## State and Persistence Behavior

Driver state is per-device and volatile. `cur_i2c_clk_div` persists after probe. `rxbuf`, `rxbuf_idx`, and `rxbuf_size` describe the currently active read and must only be touched under the serialized transaction model. GPIO mode bytes come from SRAM settings and may be changed in chip SRAM by `mcp2221_check_gpio_pinfunc()`. IIO `adc_values`, `adc_scale`, `dac_value`, and `dac_scale` are cached from status/flash/SRAM reports; DAC writes update SRAM settings and the cached value after success.

## Dependencies and Integration Points

The file bridges HID core to I2C core (`i2c_algorithm`, `devm_i2c_add_adapter`), SMBus emulation flags, gpiolib, IIO, power management hints, completions, delayed work, and ACPI companion propagation. It uses `hid-ids.h` for Microchip IDs and `FIELD_GET`, `GENMASK`, and endian helpers for status parsing.

## Risks and Edge Cases

- Response matching depends on strict one-command-at-a-time locking; any future async path would need explicit correlation.
- `mcp_set_i2c_speed()` returns `0` even if setting speed fails after cancel, so probe may continue with an unexpected bus speed.
- GPIO callbacks return status from HID reports directly; `mcp_gpio_get()` returns the line value encoded in `mcp->status`, so negative errors and boolean values share one path.
- `mcp_init_work()` uses a static retry counter shared across all devices, which can make multi-device retry behavior surprising.
- Block SMBus reads depend on `data->block[0]` as a requested length before the read; callers must initialize it correctly.
- The GPIO-vs-IIO mode policy can rewrite SRAM pin modes and surprise users expecting existing alternate functions to remain active.

## Test Signals

Exercise I2C single-message read/write, two-message repeated-start reads, unsupported multi-message rejection, SMBus transaction variants, timeout/cancel behavior, and address NACK translation to `-ENXIO`. GPIO tests should cover alternate-function pins, direction reads, direction set plus value set, and `gpio_mode_enforce`. IIO tests should validate channel discovery, scale derivation from flash, ADC bounds, DAC range checks, delayed retry behavior, and removal while delayed work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-mcp2221.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-megaworld.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-megaworld.c

## Purpose

`hid-megaworld.c` adds force-feedback rumble support for Mega World gamepads. The generic HID/input mapping handles normal controls; this driver locates the device's output report fields and wires Linux `FF_RUMBLE` events to the report values expected by the controller.

## Important APIs, Types, and Functions

- `struct mwctrl_device` stores the selected output report and pointers to the weak/strong magnitude fields inside that report.
- `mwctrl_play()` is the memless force-feedback callback. It scales 16-bit Linux rumble magnitudes down by eight bits, writes strong and weak values into the HID report fields, and sends `HID_REQ_SET_REPORT`.
- `mwctrl_init()` validates output report fields, gets the first input device, allocates per-FF data, enables `FF_RUMBLE`, creates a memless FF device, initializes the report's constant field, and stores weak/strong field pointers.
- `mwctrl_probe()` parses the device, starts HID with default connections except generic FF, and initializes rumble.

## Control Flow

Probe calls `hid_parse()`, starts hardware with `HID_CONNECT_DEFAULT & ~HID_CONNECT_FF`, then `mwctrl_init()`. Initialization requires at least one HID input, validates output report values for indices 0 through 3, allocates `mwctrl_device`, registers a memless FF handler on the first input device, selects the output report, writes the fixed first field value `0x02`, and records field 2 as strong and field 3 as weak. Later FF playback calls update the report and send it synchronously through HID core.

## State and Persistence Behavior

The only persistent driver state is the allocated `mwctrl_device` retained by input FF core and pointers into HID report storage. Rumble state is not separately cached; the current effect lives in the report values. There is no suspend/resume logic or nonvolatile configuration.

## Dependencies and Integration Points

The driver depends on HID report validation, HID output requests, Linux input FF memless support, and Mega World VID/PID definitions from `hid-ids.h`. It deliberately disables generic HID force feedback to avoid duplicate ownership of the output report.

## Risks and Edge Cases

- `mwctrl_init()` loops over output report value indices and uses the last validated report; unusual descriptors with multiple output reports could select an unintended report.
- It assumes field 2 is strong and field 3 is weak, with field 0 fixed to `0x02`; descriptor changes could break rumble silently.
- No remove callback is provided; cleanup relies on HID/input teardown and the FF core's ownership of the allocated data.
- Magnitudes are truncated from 16 bits to 8 bits, so low-level effects may lose precision.

## Test Signals

Test probe failure with no inputs, missing/short output reports, memless FF creation failure, and successful rumble playback writing weak/strong bytes then sending `SET_REPORT`. Hardware validation should verify both actuators respond with the expected strength mapping and stop when zero magnitudes are sent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-megaworld.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-mf.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-mf.c

## Purpose

`hid-mf.c` provides force-feedback support for Mayflash controller adapters that identify as DragonRise devices. These adapters may expose multiple input devices and output reports; the driver pairs each output report with the corresponding input device and creates a memless rumble interface.

## Important APIs, Types, and Functions

- `struct mf_device` stores the HID output report associated with one input device.
- `mf_play()` scales Linux strong/weak rumble magnitudes from 16-bit to 8-bit values, writes weak then strong into the first output field, and sends `HID_REQ_SET_REPORT`.
- `mf_init()` iterates every HID output report, validates it has at least one field with two values, advances through the HID input list, allocates one `mf_device` per input, enables `FF_RUMBLE`, creates memless FF, initializes the output report to zero, and sends that zero report.
- `mf_probe()` applies `id->driver_data` quirks, parses HID, starts hardware with generic FF disabled, and calls `mf_init()`.

## Control Flow

The device ID table marks several Mayflash/DragonRise adapters with `HID_QUIRK_MULTI_INPUT` so each controller port can become a separate input device. Probe applies that quirk before parsing. After hardware start, `mf_init()` walks output reports in descriptor order and expects a matching input device for each one. Playback is straightforward: scale, store into the report, and request a set-report transfer.

## State and Persistence Behavior

Each registered FF device owns a small `mf_device` pointing at its output report. The current rumble values live in HID report field storage. No persistent configuration, workqueue, timer, or sysfs state exists.

## Dependencies and Integration Points

The file integrates HID parsing/startup, HID output reports, input FF memless support, DragonRise/Mayflash IDs, and HID quirk flags. It logs with `dbg_hid`, `hid_info`, and `hid_err`.

## Risks and Edge Cases

- The report-to-input pairing depends on descriptor/list ordering. If an adapter exposes reports and inputs in different order, rumble could target the wrong port.
- If FF creation fails after previous ports were initialized, the function returns an error and probe stops, relying on subsystem cleanup for already-created memless devices.
- It assumes report field 0 values 0 and 1 are weak/strong bytes for all matched devices.
- Some listed devices are marked as "probably work" in comments; hardware coverage may be incomplete.

## Test Signals

Tests should cover multi-input descriptor parsing, matching output-report count to input count, invalid output reports, zero-initialization reports on probe, and playback scaling. Hardware tests should verify each adapter port rumbles independently and that the `HID_QUIRK_MULTI_INPUT` choices produce expected input devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-mf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-microsoft.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-microsoft.c

## Purpose

`hid-microsoft.c` collects quirks for Microsoft-branded HID devices and compatible Bluetooth controllers. It fixes a specific bad report descriptor, maps vendor usages on ergonomic keyboards and presenters, suppresses duplicate usages or unwanted Surface Dial axes, applies selected HID core quirks, and provides Bluetooth Xbox/8BitDo rumble support through a worker-sent output report.

## Important APIs, Types, and Functions

- Quirk bits `MS_HIDINPUT`, `MS_ERGONOMY`, `MS_PRESENTER`, `MS_RDESC`, `MS_NOGET`, `MS_DUPLICATE_USAGES`, `MS_SURFACE_DIAL`, and `MS_QUIRK_FF` select behavior from the ID table.
- `struct ms_data` stores quirks, HID device pointer, FF work item, current strong/weak magnitudes, and a DMA-safe output report buffer.
- `ms_report_fixup()` patches Wireless Desktop Receiver Model 1028 descriptor bytes from Usage Min/Max to Physical Min/Max.
- `ms_ergonomy_kb_quirk()`, `ms_presenter_8k_quirk()`, and `ms_surface_dial_quirk()` implement input mapping decisions.
- `ms_event()` handles vendor-packed ergonomic keyboard events for keypad symbols, scroll wheel deltas, and F14-F18 style keys.
- `ms_init_ff()`, `ms_play_effect()`, `ms_ff_worker()`, and `ms_remove_ff()` implement Xbox-style rumble report 3.
- `ms_probe()` allocates state, applies HID quirks, parses/starts HID, and initializes FF; `ms_remove()` stops HID and cancels FF work.

## Control Flow

The ID table supplies quirk bits. Probe stores them, sets `HID_QUIRK_NOGET` or `HID_QUIRK_INPUT_PER_APP` where required, parses, then starts HID with normal connections plus `HID_CONNECT_HIDINPUT_FORCE` when needed. During descriptor parsing, `.report_fixup`, `.input_mapping`, and `.input_mapped` adjust mappings. Runtime `.event` consumes special ergonomic keyboard vendor usages that need value decoding instead of normal one-usage mapping.

For FF devices, `ms_init_ff()` takes the first input, allocates an `xb1s_ff_report`, registers `FF_RUMBLE`, and uses `input_ff_create_memless()`. Playback scales 16-bit magnitudes to 0-100, stores them in `ms_data`, and schedules `ms_ff_worker()`, which builds report ID 3 with weak/strong enables, maximum duration/loop count, and the two magnitudes before calling `hid_hw_output_report()`.

## State and Persistence Behavior

Quirk selection is persistent for the HID device lifetime. FF state is cached as two 8-bit magnitudes and a reusable output buffer. The ergonomic key handler has a function-static `last_key` used to release the previously emitted F14-F18 key; because it is static, it is shared across devices. There is no durable storage.

## Dependencies and Integration Points

The driver integrates HID core callbacks for report fixup, input mapping, mapped cleanup, events, probe/remove, Linux input key/relative events, workqueues, and input FF. Device IDs and key constants come from kernel HID/input headers and `hid-ids.h`.

## Risks and Edge Cases

- `ms_remove()` calls `hid_hw_stop()` before `ms_remove_ff()`. Any pending worker is canceled after hardware stop, which prevents future sends but means ordering should be reviewed if FF teardown changes.
- The static `last_key` in `ms_event()` is shared across all devices and could release the wrong key if multiple matching keyboards emit interleaved events.
- Descriptor fixup uses exact size/byte offsets and will skip near variants.
- FF playback writes shared `strong`/`weak` values without explicit locking; repeated effects coalesce through the workqueue and may drop intermediate states, which is acceptable for rumble but worth noting.
- Surface Dial filtering returns `-1` for several axes, so descriptor changes could hide useful controls.

## Test Signals

Test descriptor fixup on the exact Model 1028 descriptor, ergonomic vendor-usage mapping and value event decoding, presenter mappings, duplicate usage clearing, Surface Dial ignored axes, `HID_QUIRK_NOGET`, and forced hidinput connection. FF tests should validate report bytes for zero/nonzero rumble, worker cancellation on remove, and no warnings on unsupported effect types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-microsoft.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-monterey.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-monterey.c

## Purpose

`hid-monterey.c` is a small quirk driver for Monterey/Genius KB29E keyboards. It fixes one malformed report descriptor page byte and maps several consumer-page application keys to Linux key codes.

## Important APIs, Types, and Functions

- `mr_report_fixup()` checks descriptor size and bytes at offsets 29 and 30, then changes the usage page from Button (`0x09`) to Consumer (`0x0c`) for the affected descriptor.
- `mr_input_mapping()` maps consumer usages `0x156`, `0x157`, `0x158`, and `0x15c` to `KEY_WORDPROCESSOR`, `KEY_SPREADSHEET`, `KEY_PRESENTATION`, and `KEY_STOP`.
- The HID driver registers `.report_fixup` and `.input_mapping` for the Monterey KB29E VID/PID.

## Control Flow

On bind, HID core calls `mr_report_fixup()` before parsing. If the expected malformed descriptor signature is present, the driver mutates the descriptor in place. During input mapping, it only handles consumer-page usages and leaves all other usages to generic HID.

## State and Persistence Behavior

The driver has no per-device allocation or mutable runtime state. Its only mutation is in-memory descriptor correction during probe.

## Dependencies and Integration Points

It depends on HID core descriptor fixup/input mapping callbacks, Linux input key codes, and Monterey device IDs from `hid-ids.h`. It uses `hid_map_usage_clear()` through `mr_map_key_clear`.

## Risks and Edge Cases

- Descriptor fixup is offset-based and intentionally narrow; firmware variants with shifted descriptors will not be fixed.
- It assumes the listed consumer usages have the intended labels on this keyboard and does not expose configuration.
- There is no probe/remove because generic HID lifecycle is sufficient.

## Test Signals

Validate that the exact bad descriptor is patched, unrelated descriptors remain unchanged, the four consumer usages map to the expected key codes, and all other usages continue through generic HID handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-monterey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-multitouch.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-multitouch.c

## Purpose

`hid-multitouch.c` is the generic HID multitouch driver for a large range of USB, I2C, Bluetooth, and Win8-certified touchscreens/touchpads. It converts HID digitizer descriptors and reports into Linux input-mt slot events, applies extensive device-class quirks, sets HID feature modes such as input mode/latency/contact reporting, supports haptic touchpads, and maintains a broad VID/PID match table for devices that need non-default behavior.

## Important APIs, Types, and Functions

- `struct mt_class` describes class-level quirks, signal/noise ratios, maximum contacts, direct/indirect behavior, and whether non-touch inputs should be exported.
- `struct mt_device` is per-HID-device state: selected class, release timer, haptic state, maximum contacts, input mode, buttonpad/pressurepad/haptic flags, serial detection, application list, report list, and `mt_io_flags`.
- `struct mt_application` tracks one HID application/report identity, per-contact usage list, quirks, scan time/contact count pointers, expected/received contacts, button aggregation, palm-release bitmap, timestamp state, and input-mt flags.
- `struct mt_usages` stores pointers to HID field values for one contact slot: coordinates, tool size, pressure, azimuth, contact ID, tip, in-range, and confidence.
- Parsing helpers allocate/find applications and reports, store field pointers, fetch feature reports, and map HID usages (`mt_feature_mapping()`, `mt_touch_input_mapping()`, `mt_input_mapping()`).
- Runtime handlers `mt_report()`, `mt_touch_report()`, `mt_process_slot()`, `mt_sync_frame()`, and `mt_expired_timeout()` convert full HID reports into input events and release sticky contacts.
- Mode/power helpers `mt_set_modes()`, `mt_need_to_apply_feature()`, `mt_suspend()`, `mt_resume()`, `mt_reset_resume()`, `mt_on_hid_hw_open()`, and `mt_on_hid_hw_close()` program feature reports.
- `mt_probe()` selects a class, sets HID quirks, parses/starts hardware, creates sysfs `quirks`, and initializes haptics.

## Control Flow

Probe chooses a class from `id->driver_data`, allocates `mt_device` and haptic storage, sets default touchscreen input mode, forces HID no-input-sync and per-application input handling, optionally forces multi-input behavior, parses the descriptor, applies descriptor/constant-field fixes, starts HID, creates the quirks sysfs group, and sends normal latency/all-report feature settings.

During descriptor parsing, `mt_feature_mapping()` reads contact max/button type/inputmode-related features and haptic features. `mt_input_mapping()` creates report/application bookkeeping and either maps multitouch collections itself or lets hid-input handle non-touch collections when allowed. Repeated HID usage fields are grouped into `mt_usages` records representing contacts.

At runtime, `.event` consumes individual events for multitouch collections, and `.report` processes whole reports. `mt_touch_report()` computes timestamps and expected contact count, processes every stored contact through `mt_process_slot()`, forwards non-touch events such as buttons, syncs when expected contacts have arrived, and manages a timer for sticky-finger release. Slot selection depends on class quirks: contact ID, contact number, Cypress special rules, minus-one IDs, or input-mt key lookup.

## State and Persistence Behavior

All state is runtime per HID device. The class quirks can be read and overwritten through the `quirks` sysfs attribute, which updates each application and drops contact-count accuracy when unavailable. Applications persist across parsed reports and retain pointers into HID field values. `mt_io_flags` contains a running bit lock and low bits for active slots. Feature-mode settings are written to the device on probe/open/close/suspend/resume but are not stored by this driver beyond `inputmode_value`.

## Dependencies and Integration Points

The file integrates deeply with HID core callbacks (`probe`, `remove`, `report_fixup`, `feature_mapping`, `input_mapping`, `input_mapped`, `input_configured`, `event`, `report`, PM/open/close), Linux input-mt, timers, sysfs attributes, haptic support from `hid-haptic.h`, and many vendor/product constants from `hid-ids.h`. Its comments explicitly call out hid-tools regression tests as an expected validation path.

## Risks and Edge Cases

- The quirk matrix is large; changing default class behavior can affect many devices.
- `mt_probe()` overwrites `td->mtclass.quirks` with only `MT_QUIRK_ORIENTATION_INVERT` when one axis is inverted, rather than OR-ing it with existing class quirks; this is a subtle behavior worth review.
- Contact processing relies on descriptor-time pointers into HID field values and assumptions about report ordering.
- Sticky-finger timer and report processing coordinate through bit locks; missed unlocks or long report handlers could suppress releases.
- Feature report writes are best-effort and often ignore return values, so devices may remain in unexpected modes.
- Sysfs quirk writes can alter live parsing behavior without reinitializing slots or input capabilities.

## Test Signals

Run hid-tools regression suites for known multitouch devices. Add targeted tests for descriptor mapping, contact ID/contact number slot selection, duplicate suppression, confidence/in-range/tip validity, Win8 button aggregation, timestamp wrap/resync, sticky-finger release timer, feature-mode programming, haptic pressure integration, Goodix descriptor fixup, Yoga Book report filtering/naming, sysfs quirk writes, suspend/resume/open/close mode changes, and representative entries from the device table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-multitouch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-nintendo.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-nintendo.c

## Purpose

`hid-nintendo.c` is a full HID driver for Nintendo Switch Joy-Cons, Pro Controllers, charging grip combinations, and Nintendo Switch Online NES/SNES/Genesis/N64 controllers. It performs controller initialization through USB commands and Switch subcommands, reads calibration from controller SPI flash, exposes gamepad and optional IMU input devices, implements rumble, player/home LEDs, battery power-supply status, suspend/resume behavior, and careful subcommand rate limiting for Bluetooth reliability.

## Important APIs, Types, and Functions

- `struct joycon_ctlr` is the persistent controller object. It stores HID/input devices, player/home LEDs, controller state/type, spinlock, MAC address, synchronous command state, calibration data, battery data, rumble queue/workqueue, and IMU timestamp/average-delta state.
- Wire structs model reports: `joycon_subcmd_request`, `joycon_subcmd_reply`, `joycon_input_report`, `joycon_rumble_output`, and `joycon_imu_data`.
- Send path: `__joycon_hid_send()`, `joycon_hid_send_sync()`, `joycon_send_usb()`, `joycon_send_subcmd()`, `joycon_enforce_subcmd_rate()`, and `joycon_wait_for_input_report()`.
- Initialization helpers read info/calibration and enable modes: `joycon_read_info()`, `joycon_request_calibration()`, `joycon_request_imu_calibration()`, `joycon_set_report_mode()`, `joycon_enable_imu()`, `joycon_enable_rumble()`, and `joycon_init()`.
- Input path: `nintendo_hid_event()`, `joycon_ctlr_handle_event()`, `joycon_parse_report()`, stick/button/dpad reporters, and `joycon_parse_imu_report()`.
- FF path: rumble frequency/amplitude tables, `joycon_encode_rumble()`, `joycon_set_rumble()`, `joycon_send_rumble_data()`, and `joycon_rumble_worker()`.
- Device integration: `joycon_input_create()`, `joycon_imu_input_create()`, `joycon_leds_create()`, `joycon_power_supply_create()`, probe/remove, PM suspend/resume, and module init/exit for IDA cleanup.

## Control Flow

Probe allocates `joycon_ctlr`, initializes locks/waitqueue/workqueue, parses HID, marks the HID version high bit so userspace can distinguish this mapping, starts HIDRAW-only hardware, opens I/O, and calls `joycon_init()`. Initialization performs USB handshake and baud setup when applicable, requests controller info to determine real controller type, reads stick and IMU calibration with user calibration preferred over factory, enables IMU and rumble where supported, and switches to full input report mode. Probe then registers LEDs, battery power supply, main input device, optional IMU input device, and enters `JOYCON_CTLR_STATE_READ`.

Raw input first checks whether a synchronous USB/subcommand response is awaited. Matching replies are copied into `input_buf`, clear the message type, and wake the sender. Normal input reports are parsed only in READ state. Button/stick/dpad mapping depends on controller type, not only HID product ID. IMU reports contain three samples; the driver estimates sample timestamps from a running average of packet deltas and applies calibration before reporting accelerometer and gyro axes. Rumble is queued in a small circular buffer and sent by a workqueue, with periodic sends triggered by vibrator reports and rate limited to avoid Bluetooth drops.

## State and Persistence Behavior

State is per physical controller and mostly volatile. Calibration data read from controller SPI flash persists in the controller, while parsed calibration values persist in RAM. LEDs are represented by Linux LED class devices and mirrored to hardware by subcommands. Battery state is updated from input reports under spinlock. Rumble state persists in the queue and last encoded data packet; zero-rumble packets are sent a bounded number of times before traffic stops. Controller state gates command sending during removal and suspend.

## Dependencies and Integration Points

The driver integrates HID raw events/output reports, Linux input/FF, LED class, power-supply class, IDA player allocation, workqueues, waitqueues, mutexes, spinlocks, jiffies timing, PM callbacks, endian/unaligned helpers, and Nintendo IDs from `hid-ids.h`. It exposes HIDRAW rather than generic hid-input because the driver creates its own Linux input devices.

## Risks and Edge Cases

- Synchronous command matching depends on `output_mutex`, `msg_type`, and ACK IDs; unexpected replies can be treated as normal input or ignored.
- Bluetooth stability depends on timing heuristics and input-report cadence; regressions can cause disconnects.
- `joycon_input_create()` registers the input device before configuring capabilities, which is unusual and should be checked against input-core expectations in this tree.
- Rumble queue overwrite deliberately keeps the latest state but can drop intermediate effects.
- Calibration fallback allows operation but may produce inaccurate sticks/IMU.
- Removal destroys the workqueue after setting REMOVED, but any future LED/FF path must continue to handle `-ENODEV` cleanly.
- IMU timestamp estimation can be wrong under highly irregular host/controller packet timing.

## Test Signals

Test USB and Bluetooth probe paths, charging grip handshake failure, controller type decoding for NSO variants, SPI calibration reads with user/factory/default fallback, stick mapping bounds, button maps per controller type, IMU calibration/divisor zero handling, IMU dropped-packet compensation, rumble encoding and queue overrun, LED registration and set failures, battery properties, synchronous command timeout/retry, suspend/resume state transitions, and unplug during pending LED/rumble/subcommand work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-nintendo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-nti.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-nti.c

## Purpose

`hid-nti.c` is a descriptor-fixup quirk driver for the Network Technologies USB-SUN adapter used with pre-USB Sun keyboards. Its only behavior is correcting a wrong logical maximum in the report descriptor so generic HID keyboard handling can interpret key usages correctly.

## Important APIs, Types, and Functions

- `nti_usbsun_report_fixup()` checks for the known bad descriptor signature at offsets 53 and 59 and changes both bytes from `0x65` to `0xe7`.
- The HID device table binds `USB_VENDOR_ID_NTI`/`USB_DEVICE_ID_USB_SUN`.
- `nti_driver` registers the fixup callback and otherwise relies on generic HID behavior.

## Control Flow

When HID core probes the matching adapter, it calls the report-fixup callback before descriptor parsing. If the descriptor is at least 60 bytes and both expected logical-maximum bytes are present, the callback patches them in place and logs the fix. No custom input mapping or runtime event handling is used.

## State and Persistence Behavior

There is no allocated per-device state and no persistent runtime state. The descriptor mutation is in-memory for the current device instance.

## Dependencies and Integration Points

This file depends on HID core report fixup and NTI IDs from `hid-ids.h`. Generic HID input handles all keyboard events after the descriptor is corrected.

## Risks and Edge Cases

- The fixup is exact-offset based and will miss alternate firmware descriptors.
- If a descriptor coincidentally matches those bytes but is not the USB-SUN layout, the patch could be wrong; the narrow VID/PID match limits this risk.
- There is no validation beyond the two byte checks.

## Test Signals

Validate that the known bad descriptor is patched, shorter descriptors are left alone, nonmatching bytes are left alone, and generic keyboard events expose the formerly unreachable Sun key usages after parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-nti.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-ntrig.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-ntrig.c

## Purpose

`hid-ntrig.c` handles older N-Trig USB touchscreens that need special filtering and activation logic beyond generic HID multitouch. It supports pen, single-touch, and multitouch reports, exposes sysfs tunables for physical/logical sensor sizes and contact filtering thresholds, reports firmware version for USB devices, and implements an activation/deactivation state machine to avoid noisy or bogus touch frames.

## Important APIs, Types, and Functions

- Module parameters `min_width`, `min_height`, `activate_slack`, `deactivate_slack`, `activation_width`, and `activation_height` seed per-device filtering thresholds.
- `struct ntrig_data` stores current contact fields, multitouch footer accumulation, activation state, slack values, thresholds, and sensor physical/logical dimensions.
- `ntrig_version_string()`, `ntrig_get_mode()`, `ntrig_set_mode()`, and `ntrig_report_version()` decode firmware information and nudge newer firmware modes.
- Sysfs show/set functions expose sensor dimensions and threshold/slack tuning through `ntrig_attribute_group`.
- `ntrig_input_mapping()` maps logical multitouch X/Y/width/height fields, captures sensor dimensions, suppresses untrusted/contact-control usages, and lets pen/single-touch physical fields use generic handling.
- `ntrig_event()` consumes HID events, accumulates contact data and vendor footer bytes, filters contacts by confidence/size/pen activity, emits MT events, and updates BTN_TOUCH/BTN_TOOL_DOUBLETAP at contact-count frame boundaries.
- Probe/remove allocate/free `ntrig_data`, apply duplicate-usage quirks, start HID, adjust mode, create sysfs, and stop hardware on removal.

## Control Flow

Probe applies `HID_QUIRK_MULTI_INPUT` and `HID_QUIRK_NO_INIT_REPORTS` for listed devices, initializes per-device thresholds and sensor defaults, parses and starts HID, sends a feature-report wake/mode sanity sequence if report `0x0a` exists, reports firmware version through a USB control message, and creates sysfs attributes. Descriptor mapping stores sensor scale information from logical multitouch X/Y fields and initializes physical-unit thresholds.

Runtime event handling distinguishes pen, single-touch, and multitouch. A vendor usage marks the start of a multitouch group. X/Y/width/height/contact ID/tip/confidence fields are cached. Vendor footer usage `0xff000002` arrives four times per contact; once complete, the driver detects pen activity, placeholders, size threshold failures, activation threshold shortcuts, confidence failures, first-contact single-touch emulation, and emits MT position/major/minor/orientation plus `input_mt_sync()`. On `HID_DG_CONTACTCOUNT`, it updates the activation state machine and reports touch buttons if the frame is active.

## State and Persistence Behavior

All mutable state is in `struct ntrig_data` and sysfs-adjustable at runtime. Thresholds are stored in logical sensor units but shown and accepted in physical dimensions. `act_state` tracks inactive, active, and pen-termination phases; `reading_mt` and footer counters reset across frames. There is no persistent storage beyond module parameters used for new devices.

## Dependencies and Integration Points

The file integrates HID core mapping/event/configured callbacks, input MT protocol B-era helpers (`input_mt_sync`), sysfs attributes, USB control transfers for firmware version, usbhid helpers, and N-Trig IDs. It grabs all usages through `ntrig_grabbed_usages` so it can filter events before generic hidinput emits them.

## Risks and Edge Cases

- Sysfs threshold conversions divide by sensor physical/logical dimensions; probe seeds them to 1, but malformed descriptors with zero physical size could still make scale behavior questionable.
- `ntrig_get_mode()` and `ntrig_set_mode()` rely on specific feature report IDs and do limited validation.
- The activation state machine is sensitive to footer order, contact count semantics, and pen activity frames; small firmware differences can cause stuck or suppressed touch.
- `ntrig_input_mapped()` clears generic mappings for many usages, so missed custom emission can remove input events entirely.
- Size filtering marks confidence false for small contacts but still uses them for activation state, which is intentional but tricky.

## Test Signals

Test pen-only reports, physical single-touch reports, logical multitouch frames, footer accumulation, placeholder contacts, pen-activity termination, activation/deactivation slack transitions, threshold sysfs conversions and bounds, duplicate usage devices, mode sanity path, firmware-version control transfer, and input device naming. Regression hardware tests should verify no stuck BTN_TOUCH after empty frames or pen transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-ntrig.c -->
