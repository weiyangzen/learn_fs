# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f34.c

## Purpose

`rmi_f34.c` implements common and bootloader-v5 support for RMI4 Function 34 firmware flashing. It exposes sysfs attributes for bootloader ID, configuration ID, firmware update trigger, and update status, coordinates full device reprobe around flash mode entry, and delegates bootloader-v7-or-newer flashing to `rmi_f34v7.c`.

## Important APIs, Types, and Functions

Important functions include `rmi_f34_command()`, `rmi_f34_attention()`, `rmi_f34_write_blocks()`, `rmi_f34_flash_firmware()`, `rmi_f34_update_firmware()`, `rmi_firmware_update()`, `rmi_driver_update_fw_store()`, `rmi_f34v5_probe()`, `rmi_f34_probe()`, `rmi_f34_create_sysfs()`, and `rmi_f34_remove_sysfs()`. The file uses `struct f34_data` and v5 fields declared in `rmi_f34.h`.

## Control Flow

Probe allocates `f34_data` and selects v5 or v7 probing based on function version. The sysfs `update_fw` store callback requests a firmware file, then `rmi_firmware_update()` validates F34 availability and bootloader support. It enters flash mode, disables IRQs, frees and reprobes functions so the device is represented in bootloader mode, performs the v5 or v7 reflash, then resets/scans/reinitializes functions and re-enables the sensor. V5 flashing writes the bootloader ID when required, issues erase/write commands, and waits for completion signaled by `rmi_f34_attention()`.

## State and Persistence Behavior

`f34_data` persists bootloader/configuration IDs, update status/progress/size, command completions, and v5 geometry such as block size and block counts. During firmware update, the broader RMI function list is intentionally torn down and rebuilt. Hardware flash contents are persistent and modified by erase/write commands. Sysfs status reports percent progress or a final return code.

## Dependencies and Integration Points

The file depends on firmware loading, RMI scan/probe/init/reset helpers, RMI IRQ control, sysfs, completions, mutex guards, unaligned little-endian helpers, and the v7 helper API in `rmi_f34.h`. It integrates with the RMI core through `data->f34_container`, `bootloader_mode`, and function handler attention callbacks.

## Risks and Edge Cases

Firmware updates are high-risk because they intentionally erase persistent device flash. Correct block-size validation is essential. Failure after entering bootloader mode but before final reprobe can leave the device in an unusable state until reset or retry. Completion waits depend on F34 IRQ delivery after masks are configured. The sysfs update path is synchronous and can block for erase/write time. Reprobe failures after a successful flash still return errors to userspace.

## Test Signals

Tests should cover v5 image/config size validation, config-only and firmware-plus-config updates, unsupported bootloader versions, missing F34, firmware request failures, command timeout/error status, update status progression, IRQ disable/enable sequencing, successful post-flash reset/reprobe, and sysfs attribute creation/removal.
