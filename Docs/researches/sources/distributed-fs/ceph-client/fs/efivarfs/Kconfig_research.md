<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efivarfs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/efivarfs/Kconfig

## Purpose
`Kconfig` exposes the `EFIVAR_FS` build option for the EFI variable filesystem. It lets the kernel or module build include the replacement filesystem for older EFI variable sysfs support.

## Important APIs, types, and functions
The single symbol is `CONFIG_EFIVAR_FS`, a tristate that depends on `EFI` and defaults to module. The help text documents that the module name is `efivarfs` and that efivarfs avoids the old sysfs 1024-byte variable size limit.

## Control flow
There is no runtime control flow. Build selection controls whether `inode.o`, `file.o`, `super.o`, and `vars.o` are linked into `efivarfs.o`.

## State and persistence
The file has no state. Its persistence effect is build configuration only; EFI variables themselves live in firmware NVRAM.

## Dependencies and integration points
It integrates with the kernel Kconfig system and requires EFI runtime variable support. The default modular setting makes efivarfs commonly available without forcing it built in.

## Risks and test signals
Risks are configuration mismatches on non-EFI systems and tests assuming efivarfs exists when `EFI` or `EFIVAR_FS` is disabled. Test signals are build coverage for `n`, `m`, and `y` configurations and boot-time module registration on EFI-capable machines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efivarfs/Kconfig -->
