# sources/distributed-fs/ceph-client/fs/exfat/Kconfig

## Purpose
`Kconfig` exposes the exFAT filesystem driver to the kernel configuration system. It declares the build-time switch for native exFAT support and a separate default charset option used when mounts do not specify `iocharset=`.

## Important APIs, types, and functions
`config EXFAT_FS` is a tristate option named "exFAT filesystem support". It selects `BUFFER_HEAD`, `NLS`, and `LEGACY_DIRECT_IO`, which are required by the implementation files in this directory. `config EXFAT_DEFAULT_IOCHARSET` is a string option defaulting to `"utf8"` and depending on `EXFAT_FS`.

## Control flow
This file has no runtime flow. During kernel configuration, enabling `EXFAT_FS=y` links the driver built-in and `EXFAT_FS=m` builds `exfat.ko`. The default iocharset string becomes `CONFIG_EXFAT_DEFAULT_IOCHARSET`, which `super.c` uses for mount option defaults.

## State and persistence behavior
The selected tristate persists in the kernel build configuration. The default charset persists as a compiled-in string but can be overridden per mount through the exFAT mount options. The selected helper dependencies determine whether the driver can use buffer-head block I/O, NLS conversion tables, and legacy direct I/O helpers.

## Dependencies and integration points
The option is consumed by the exFAT `Makefile` and by code guarded through normal `CONFIG_EXFAT_FS` build selection. Its `select` lines tie the driver to core block-buffer cache, NLS, and direct-I/O infrastructure.

## Risks and test signals
Risks are configuration-level: missing selected dependencies would break compilation, and a poor default charset changes filename conversion behavior for users who do not pass `iocharset`. Test signals include all three build modes (`n`, `m`, `y`), mount behavior with default and overridden iocharset, and build coverage when NLS or buffer-head options are otherwise disabled.
