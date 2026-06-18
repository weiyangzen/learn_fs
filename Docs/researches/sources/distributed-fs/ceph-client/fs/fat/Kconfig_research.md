# sources/distributed-fs/ceph-client/fs/fat/Kconfig

## Purpose
`Kconfig` declares build-time configuration for Linux FAT-family filesystems. It defines the shared FAT core, the MSDOS and VFAT filesystem drivers, default FAT character conversion settings, default UTF-8 mount-option behavior, and optional FAT KUnit tests.

## Important Config Symbols
`FAT_FS` is a tristate core selected by both `MSDOS_FS` and `VFAT_FS`; it selects `BUFFER_HEAD`, `NLS`, and `LEGACY_DIRECT_IO`. `MSDOS_FS` enables classic 8.3-name DOS FAT support and builds module `msdos`. `VFAT_FS` enables Windows 95-style long filename support and builds module `vfat`. `FAT_DEFAULT_CODEPAGE` sets the default codepage for FAT mounts. `FAT_DEFAULT_IOCHARSET` sets the default VFAT I/O charset. `FAT_DEFAULT_UTF8` controls whether the `utf8` mount option is on by default. `FAT_KUNIT_TEST` builds FAT KUnit tests when KUnit is enabled.

## Control Flow
Kconfig control flow is dependency and selection based. Enabling MSDOS or VFAT selects the common FAT core. Charset defaults are visible only when their filesystem prerequisites are enabled. `FAT_KUNIT_TEST` defaults to `KUNIT_ALL_TESTS`, allowing global KUnit configuration to pull the tests in automatically.

## State And Persistence Behavior
This file has no runtime state. Its persistent effect is the generated kernel configuration, which controls whether FAT support is built in, modular, or absent, and which defaults are compiled into the FAT/VFAT mount behavior. Mount options can override the compiled defaults at runtime.

## Dependencies And Integration Points
The symbols integrate with `fs/fat/Makefile`, native language support, buffer-head based block I/O, legacy direct I/O, and KUnit. The help text points users to VFAT documentation and explains module naming constraints: if common FAT support is a module, FAT-based filesystems must also be modules.

## Risks
Misconfigured charset defaults can produce unexpected filename conversion behavior. Enabling UTF-8 by default is explicitly cautioned against in the help text because FAT filesystems often need a specific charset. Tristate relationships matter: the shared core must be compatible with the selected front-end filesystems.

## Test Signals
Test signals include Kconfig dependency resolution, `oldconfig`/`menuconfig` visibility, built-in versus module builds for FAT/MSDOS/VFAT, mount tests with default and overridden `codepage`, `iocharset`, and `utf8` options, and `FAT_KUNIT_TEST` execution under KUnit.
