# sources/distributed-fs/ceph-client/drivers/platform/x86/amilo-rfkill.c

## Purpose
`amilo-rfkill.c` provides WLAN rfkill support for specific Fujitsu-Siemens Amilo laptop models whose radios are controlled through legacy keyboard-controller commands or fixed I/O ports.

## Important APIs, Types, and Functions
The driver defines two rfkill operation implementations: `amilo_a1655_rfkill_set_block()` sends command `A1655_WIFI_COMMAND` through i8042, and `amilo_m7440_rfkill_set_block()` writes paired values to ports `0x118f` and `0x118e` and verifies them. `amilo_rfkill_id_table` maps DMI system matches to the correct `struct rfkill_ops`. `amilo_rfkill_probe()` allocates and registers the rfkill device, and init/exit functions register a simple platform driver/device only on matching DMI systems.

## Control Flow
Module init first checks the DMI table. If unsupported, it exits with `-ENODEV`. On supported systems it registers `amilo_rfkill_driver`, then creates a platform device named after `KBUILD_MODNAME`. Probe resolves the first matching DMI entry, allocates an `RFKILL_TYPE_WLAN` rfkill device with the model-specific operations pointer stored in `driver_data`, and registers it. User rfkill changes call the selected `.set_block` callback. Remove unregisters and destroys the rfkill object; module exit unregisters both platform device and driver.

## State and Persistence
The driver has two global pointers, `amilo_rfkill_pdev` and `amilo_rfkill_dev`, for the singleton platform device and rfkill device. Radio state is not cached locally and is driven directly into hardware on each rfkill set. There is no persistence beyond the platform firmware/hardware latch state.

## Dependencies and Integration Points
Dependencies are DMI matching, platform devices, the rfkill subsystem, i8042 locking/commands for A1655/L1310-class systems, and raw port I/O for M7440-class systems. The driver is intentionally narrow and does not rely on ACPI.

## Risks and Test Signals
The code uses legacy raw hardware access. Incorrect DMI matches could write to unrelated I/O ports or send unintended i8042 commands, so DMI specificity is critical. The M7440 path validates writes by reading back the ports, while the A1655 path relies on `i8042_command()` return status. Tests are mostly hardware or emulation based: DMI non-match should avoid registration; DMI match should create one WLAN rfkill; block/unblock should call the correct hardware path; M7440 readback mismatch should return `-EIO`; unregister should destroy the singleton without leaks.
