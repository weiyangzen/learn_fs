# sources/distributed-fs/ceph-client/drivers/input/touchscreen/goodix.h

## Purpose
`goodix.h` is the shared private interface for the legacy Goodix touchscreen driver and its firmware upload helper. It centralizes register addresses, request codes, controller limits, GPIO access modes, chip configuration callbacks, runtime driver state, and cross-file function prototypes.

## Important APIs, types, and functions
- Register definitions cover reset/upload control registers, firmware signature/main clock locations, request/status/command registers, config data addresses for GT1x and GT9x chips, ID and coordinate registers, and backup-reference storage.
- `enum goodix_irq_pin_access_method` describes how the driver may drive the interrupt pin during reset and PM: no access, normal GPIO, ACPI GPIO with raw semantics, or ACPI INTI/INTO methods.
- `struct goodix_chip_data` is the per-family configuration contract used by `goodix.c`: config base address, config length, config validator, and checksum updater.
- `struct goodix_ts_data` is the shared runtime object for the main driver and firmware upload code. It stores I2C/input devices, regulators, GPIOs, config state, IRQ flags, firmware/config names, controller ID/version, keymap, main clock bytes, and backup-reference memory.
- Exported helper prototypes expose I2C access, config sending, interrupt synchronization, reset-without-INT-sync, firmware checking, firmware request handling, and backup-reference saving.

## Control flow
The header does not execute code, but it defines the contracts that tie `goodix.c` and `goodix_fwupload.c` together. `goodix_ts_probe()` fills the shared structure, calls `goodix_firmware_check()`, and later configures input reporting. The firmware helper uses the same register constants and state object to upload code, answer controller requests, send main-clock data, and preserve backup-reference data.

## State and persistence
The structure layout makes configuration and firmware-upload state persistent for the lifetime of the I2C client. `config[]`, `main_clk[]`, `bak_ref`, `bak_ref_len`, and `firmware_name` are the key fields shared across normal event handling, PM, and flashless-firmware request handling. Hardware state persists only in the controller.

## Dependencies and integration points
The header depends on GPIO descriptor, I2C, input, MT, touchscreen-property, and regulator types. It is intentionally private to the touchscreen driver directory rather than a UAPI header.

## Risks
- Because `struct goodix_ts_data` is shared across two C files, changing field meaning or initialization order can break firmware upload or PM paths without compiler errors.
- Register constants are reused for different controller families; incorrect chip-data selection can send valid-looking writes to the wrong address.
- `GOODIX_CONFIG_MAX_LENGTH`, key counts, and ID length are embedded array bounds and must remain synchronized with parsing code.

## Test signals
- Build both `goodix.c` and `goodix_fwupload.c` after any header changes.
- Static checks should verify all shared fields are initialized before firmware helper use, especially `chip`, `config`, `gpiod_int`, `gpiod_rst`, and `irq_pin_access_method`.
- Firmware-upload and suspend/resume tests are the best behavioral coverage for this header contract.
