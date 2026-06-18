<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/iris/iris.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/iris/iris.c

## Purpose
Installs a custom `pm_power_off` handler for Eurobraille Iris machines that lack APM/ACPI shutdown.

## Important APIs, Types, And Functions
`iris_power_off()` writes a two-step pulse/rest sequence to I/O ports `0x341`. `iris_probe()` validates input port `0x340` unless `force` already allowed device creation, saves `old_pm_power_off`, and installs the handler. Module init registers a platform driver and synthetic platform device only when `force=1`.

## Control Flow
Module init requires `force` and then creates the platform device. Probe reads the GIO input port; `0xff` means likely absent and aborts. Remove restores the previous poweroff function and unregisters device/driver state.

## State And Persistence
Stores the previous global poweroff hook and the registered platform device pointer. The poweroff operation itself is hardware I/O and does not persist in memory.

## Dependencies And Integration Points
Uses platform-device infrastructure, legacy x86 I/O port access, sleep delays, and the global `pm_power_off` hook.

## Risks And Edge Cases
The module is intentionally force-gated because probing is weak and I/O writes are board-specific. It overwrites a global poweroff hook and restore ordering matters if another handler changes it concurrently.

## Test Signals
Module load with `force=1`, log messages for handler install/uninstall, and physical poweroff sequencing on Iris hardware validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/iris/iris.c -->
