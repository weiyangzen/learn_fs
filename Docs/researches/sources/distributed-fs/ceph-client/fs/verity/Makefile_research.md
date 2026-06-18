<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/Makefile -->
# sources/distributed-fs/ceph-client/fs/verity/Makefile

Purpose: Provides Kbuild object selection for fs-verity core and optional builtin signature support.

Important APIs, types, and functions: Builds `enable.o`, `hash_algs.o`, `init.o`, `measure.o`, `open.o`, `pagecache.o`, `read_metadata.o`, and `verify.o` when `CONFIG_FS_VERITY=y`. Adds `signature.o` when `CONFIG_FS_VERITY_BUILTIN_SIGNATURES=y`.

Control flow: Kbuild links the listed translation units into the kernel fs-verity implementation. Optional signature code is excluded entirely when the config is disabled, relying on inline stubs in `fsverity_private.h`.

State and persistence: No runtime state. Object selection determines which exports and init paths are available.

Dependencies and integration points: Integrates with the Kconfig options and the private header’s conditional prototypes/stubs.

Risks and test signals: Risks are missing a core object after symbol movement or building signature code without its config dependencies. Test all config combinations and module-less built-in link coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/Makefile -->
