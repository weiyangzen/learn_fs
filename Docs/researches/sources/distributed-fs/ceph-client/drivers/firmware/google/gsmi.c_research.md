# sources/distributed-fs/ceph-client/drivers/firmware/google/gsmi.c

Purpose: Implements the Google SMI firmware interface on supported x86/ACPI/DMI platforms. It provides sysfs controls for firmware event logs/config clearing, logs shutdown reasons during reboot/oops/panic, logs S0ix suspend/resume events, and can register an EFI variable backend using GSMI NVRAM commands.

Important APIs/types/functions: `gsmi_device` stores the platform device, three DMA32-accessible SMI buffers, lock, SMI command port, handshake type, and slab cache. `gsmi_exec()` performs inline assembly SMI calls and translates firmware return codes. EFI callbacks are `gsmi_get_variable()`, `gsmi_get_next_variable()`, and `gsmi_set_variable()`. Sysfs handlers include `eventlog_write()`, `gsmi_clear_eventlog_store()`, and `gsmi_clear_config_store()`.

Control flow: Init validates DMI/FADT, checks for a GSMI handler, registers a platform device/driver, creates DMA32 buffers, probes handshake mode, creates `/sys/firmware/gsmi`, optionally registers efivars, and installs reboot/die/panic notifiers. SMI calls serialize on `gsmi_dev.lock`, populate parameter/data/name buffers, invoke callback `0xef`, and interpret return codes. Exit unregisters notifiers, efivars, sysfs files, buffers, cache, and platform devices.

State and persistence behavior: State is global and includes preallocated buffers used even during panic paths. Firmware event logs, config, NVRAM variables, and S0ix logs are persistent firmware/platform state. `gsmi_shutdown_reason()` tracks logged reasons to avoid duplicates.

Dependencies and integration points: Depends on x86 ACPI FADT SMI command, DMI, EFI efivars core, sysfs firmware kobjects, notifiers, suspend callbacks, DMA32 slab allocation, and direct port I/O assembly.

Risks and test signals: SMI execution is platform-specific and can hang if handshake detection is wrong. Panic callback avoids taking a held spinlock, but notifier context remains sensitive. Buffer size is fixed at 1024 bytes, constraining EFI variable names/data. Test on supported Google/coreboot boards, verify sysfs writes, EFI variable operations, shutdown reason logging, S0ix logging opt-out, module unload cleanup, and old/quirky board rejection.
