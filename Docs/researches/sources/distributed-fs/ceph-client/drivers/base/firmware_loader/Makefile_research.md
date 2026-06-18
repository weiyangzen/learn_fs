# sources/distributed-fs/ceph-client/drivers/base/firmware_loader/Makefile

## Purpose
This Makefile wires firmware loader objects into the kernel build according to Kconfig selections.

## Important APIs, Types, And Functions
It builds `firmware_class.o` from `main.o`, conditionally adds `fallback.o`, `fallback_platform.o`, `sysfs.o`, and `sysfs_upload.o`, builds `fallback_table.o` when the user-helper is enabled, and always descends into `builtin/`.

## Control Flow, State, And Persistence
`obj-$(CONFIG_FW_LOADER)` controls the main firmware class object. Conditional `firmware_class-$(CONFIG_...)` lines compose optional features into that object, while `fallback_table.o` is a separate object for exported fallback configuration/sysctl state. `obj-y += builtin/` ensures built-in firmware metadata support participates even when the extra firmware list is empty.

## Dependencies, Integration Points, Risks, And Test Signals
The Makefile must stay aligned with `Kconfig` and header `#ifdef`s. Risks include unresolved symbols when sysfs/upload/fallback files are omitted incorrectly, and missing built-in firmware support if the subdirectory is not visited. Test signals include `CONFIG_FW_LOADER=m/y`, combinations of user-helper, EFI embedded firmware, sysfs, upload, and successful link of namespace exports.
