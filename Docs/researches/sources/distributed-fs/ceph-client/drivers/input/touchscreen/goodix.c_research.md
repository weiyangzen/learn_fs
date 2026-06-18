# sources/distributed-fs/ceph-client/drivers/input/touchscreen/goodix.c

## Purpose
`goodix.c` is the main I2C input driver for older Goodix GT1x/GT9x touchscreen controllers. It powers the controller, handles GPIO/ACPI reset and interrupt-line sequencing, optionally loads configuration from firmware files, reports multitouch/key/active-pen events, and coordinates suspend/resume with the firmware upload helper in `goodix_fwupload.c`.

## Important APIs, types, and functions
- `struct goodix_chip_id` maps textual controller IDs to `struct goodix_chip_data`, which selects config register address, config length, and 8-bit or 16-bit config checksum routines.
- `goodix_i2c_read()`, `goodix_i2c_write()`, and `goodix_i2c_write_u8()` are exported helpers used by this file and the firmware upload file. They perform raw 16-bit-register Goodix I2C transfers.
- `goodix_ts_read_input_report()` polls `GOODIX_READ_COOR_ADDR` until the ready bit appears, reads the first contact/key footer, fetches extra contacts, and services firmware request IRQs when the status byte is zero on flashless devices.
- `goodix_process_events()` dispatches key events, 8-byte or 9-byte finger reports, and active pen reports. It uses `input_mt_sync_frame()` with `INPUT_MT_DROP_UNUSED` slots.
- `goodix_get_gpio_config()` discovers regulators plus IRQ/reset GPIOs and can synthesize ACPI GPIO mappings or ACPI INTI/INTO method access for x86 tablets with broken firmware descriptions.
- `goodix_read_config()`, `goodix_check_cfg_*()`, `goodix_calc_cfg_checksum_*()`, and `goodix_send_cfg()` read, validate, patch, and write controller configuration blocks.
- `goodix_configure_dev()` allocates and registers the main input device, applies touchscreen properties and DMI quirks, creates the delayed-registration pen input device, and requests IRQ or polling mode.
- `goodix_ts_probe()`, `goodix_ts_remove()`, `goodix_suspend()`, and `goodix_resume()` implement I2C driver lifetime and power management.

## Control flow
Probe checks raw I2C functionality, allocates `goodix_ts_data`, gets `AVDD28`/`VDDIO` regulators and GPIOs, enables power, optionally resets the controller, tests I2C, performs firmware upload if a `firmware-name` property exists, reads the controller ID/version, and selects chip data. If board policy says to load config from disk, it starts `request_firmware_nowait()` and finishes initialization in `goodix_config_cb()`. Otherwise it directly calls `goodix_configure_dev()`.

At runtime the threaded IRQ or polling callback calls `goodix_process_events()` and then clears the coordinate status register. The event path reads the controller packet, reports a special active-pen path when a single touch has the pen flag, releases stale pen or key state as needed, and reports each finger into its MT slot. Suspend waits for asynchronous config loading, frees the IRQ if it needs to drive the INT line, saves backup reference data for flashless firmware, drives INT low, sends `GOODIX_CMD_SCREEN_OFF`, and observes the required wake delay. Resume drives INT high, synchronizes the interrupt pin, verifies the config version, resets and resends config on mismatch, and re-requests the IRQ.

## State and persistence
Runtime state lives in `struct goodix_ts_data`: controller ID/version, config bytes, keymap, touchscreen properties, IRQ flags, GPIO access mode, pen registration state, backup reference buffer, and the firmware-loading completion. Persistent device state is in controller firmware/config registers; config writes and firmware request handling program hardware immediately but are not saved by the kernel. Asynchronous config loading requires `remove()` and suspend to wait on `firmware_loading_complete`.

## Dependencies and integration points
The driver integrates with the I2C core, input/MT, touchscreen property parsing, firmware loader, regulator framework, GPIO descriptors, ACPI GPIO mappings, x86 SOC/DMI quirks, OF/ACPI device matching, and the companion firmware upload helpers declared in `goodix.h`.

## Risks
- ACPI GPIO inference is intentionally heuristic and hardware-specific; wrong mapping can break reset, IRQ locking, or wake sequencing.
- `goodix_config_cb()` ignores the return from `goodix_configure_dev()` after config processing, so probe-time async failures are only visible through logs and missing input registration.
- Active pen input is registered lazily inside the event path; failures are cached and future pen events are dropped.
- IRQ-free suspend uses the same INT pin as output; error recovery must re-request IRQs on all failed sleep-command paths.
- Flashless firmware request handling can trigger firmware re-upload from an IRQ-driven read path, making I2C failures and timing regressions visible as lost events.
- DMI quirks change packet format and coordinate inversion; tests must cover both standard and quirked report layouts.

## Test signals
- Build with `CONFIG_TOUCHSCREEN_GOODIX`, ACPI, OF, DMI, and firmware upload support.
- Probe tests should cover regulator deferral, missing GPIOs, ACPI mapping variants, no-IRQ polling mode, reset retry after failed I2C test, async config loading, and default config fallback.
- Event tests should validate 8-byte and 9-byte packets, contact count bounds, key footer handling, pen down/up, status clearing, and firmware request status-zero handling.
- PM tests should cover screen-off suspend, resume config-version mismatch resend, IRQ-free vs no-pin suspend, and flashless backup-reference save/restore interactions.
