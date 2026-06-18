# sources/distributed-fs/ceph-client/arch/x86/kernel/kdebugfs.c

Purpose: Creates the architecture debugfs root `/sys/kernel/debug/x86` and, when enabled, exposes boot parameter and setup-data contents for debugging early boot handoff structures.

Important APIs/types/functions: exports `arch_debugfs_dir`. Under `CONFIG_DEBUG_BOOT_PARAMS`, defines `struct setup_data_node`, `setup_data_read()`, `create_setup_data_nodes()`, and `boot_params_kdebugfs_init()`. The init entry point is `arch_kdebugfs_init()` via `arch_initcall`.

Control flow: init creates the `x86` debugfs directory. With boot parameter debugging enabled, it creates `boot_params`, a scalar `version` file, a blob `data` file containing the whole `boot_params`, and one numbered directory per setup-data node. Setup-data enumeration follows `boot_params.hdr.setup_data`; for indirect nodes it remaps enough bytes to inspect `struct setup_indirect` and either exposes the indirect target or the raw invalid indirect payload. File reads remap the requested physical range, copy to user, and update the file offset.

State and persistence: `arch_debugfs_dir` is a global dentry used by other x86 debugfs providers such as ITMT. Each setup-data node is heap allocated and attached as debugfs private data. All content reflects in-memory boot parameters and physical setup-data payloads for the running kernel only.

Dependencies and integration points: depends on debugfs, `boot_params`, `memremap()`/`memunmap()`, setup-data type definitions, and user-copy helpers. It mirrors some of the same setup-data exposure implemented in `ksysfs.c`, but under debugfs and gated by `CONFIG_DEBUG_BOOT_PARAMS`.

Risks: exposing raw boot parameters and setup data can reveal platform information and should remain debug-only. Physical remap failures return `-ENOMEM`; user-copy failure returns `-EFAULT`. The allocated node objects are not freed after successful debugfs creation, matching debugfs lifetime for the boot.

Test signals: with `CONFIG_DEBUG_BOOT_PARAMS`, verify `/sys/kernel/debug/x86/boot_params/data`, `version`, and numbered `setup_data/*/data` files read expected sizes and handle offsets. Systems with indirect setup data should expose the indirect target length and type.
