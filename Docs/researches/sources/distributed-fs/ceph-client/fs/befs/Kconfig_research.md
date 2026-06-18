# sources/distributed-fs/ceph-client/fs/befs/Kconfig

Purpose: defines kernel configuration for BeFS support and optional BeFS debug logging.

Important APIs/types/functions: `config BEFS_FS` is a tristate depending on `BLOCK`, selecting `BUFFER_HEAD` and `NLS`; `config BEFS_DEBUG` is a bool depending on `BEFS_FS`.

Control flow: enabling `BEFS_FS` builds the read-only BeOS filesystem driver as built-in or module. Enabling `BEFS_DEBUG` activates debug support and the `debug` mount option pathway used by `debug.c`/`linuxvfs.c`.

State and persistence: configuration controls build-time availability only; no runtime state is stored here.

Dependencies and integration: integrates with block-device filesystems, native language support, and the `befs` module build in the Makefile.

Risks: help text notes BeFS attributes and indices are not fully exposed. Users may expect write support, but the driver is read-only.

Test signals: Kconfig allmodconfig/build coverage for `BEFS_FS=m/y` and debug on/off; mount option parsing with and without debug compiled.
