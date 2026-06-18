## sources/distributed-fs/ceph-client/fs/isofs/Kconfig

Purpose: defines build-time configuration for ISO 9660 filesystem support and optional Joliet and zisofs extensions.

Important options: `ISO9660_FS` is a tristate selecting `BUFFER_HEAD`; it enables the `isofs` module or built-in driver. `JOLIET` depends on `ISO9660_FS` and selects `NLS` for Microsoft Unicode filename extensions. `ZISOFS` depends on `ISO9660_FS` and selects `ZLIB_INFLATE` for transparent decompression.

Control flow and state: no runtime control flow. These symbols determine which source files are compiled and which code paths in `inode.c`, `dir.c`, `namei.c`, `rock.c`, and `compress.c` are enabled.

Dependencies and integration points: integrates with kernel Kconfig, module naming, NLS, zlib inflate, and buffer-head based block reading.

Risks and test signals: risk is a missing select or dependency causing compile failures when optional features are enabled independently. Test matrix should build ISOFS built-in/module, with and without Joliet, and with and without zisofs.
