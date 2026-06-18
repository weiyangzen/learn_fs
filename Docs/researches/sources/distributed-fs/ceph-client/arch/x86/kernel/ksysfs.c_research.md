# sources/distributed-fs/ceph-client/arch/x86/kernel/ksysfs.c

Purpose: Exposes x86 boot parameters and setup-data records under `/sys/kernel/boot_params` using sysfs attributes and binary attributes.

Important APIs/types/functions: init entry is `boot_params_ksysfs_init()` via `arch_initcall`. Important helpers include `version_show()`, `boot_params_data_read()`, `get_setup_data_paddr()`, `get_setup_data_size()`, `type_show()`, `setup_data_data_read()`, `create_setup_data_node()`, `create_setup_data_nodes()`, and cleanup helpers. Attributes include `version`, binary `data`, and per-setup-data `type`/`data`.

Control flow: init creates the `boot_params` kobject under `kernel_kobj`, adds a group for the boot protocol version and full binary bootparams, then enumerates setup-data nodes from `boot_params.hdr.setup_data`. For each numbered node it computes the effective payload size, creates a kobject, sets the shared binary attribute size, and creates a group. Read paths remap setup-data headers, handle `SETUP_INDIRECT` by switching to the indirect target unless the target is itself invalid indirect, clamp offsets and counts, remap the payload, and copy bytes into sysfs buffers.

State and persistence: sysfs objects persist for the boot lifetime. The data is live kernel memory or physical setup-data content from boot and has no writable path. `data_attr.size` is a static bin attribute updated during node creation, so creation is serialized at init time.

Dependencies and integration points: depends on kobject/sysfs infrastructure, boot protocol structures, `memremap()`, setup-data indirect format, and `kernel_kobj`. It complements debugfs boot-param exposure in `kdebugfs.c` with a stable sysfs location.

Risks: indirect setup-data handling must avoid following recursively invalid indirect records. Shared `data_attr` mutation would be unsafe outside init-time single-threaded creation. Remapping the full setup-data length for partial reads can be heavier than needed but keeps logic simple.

Test signals: verify `/sys/kernel/boot_params/version` and `data` read correctly, numbered setup-data directories are created with correct binary sizes, offset reads clamp at EOF, indirect setup-data exposes the indirect type and payload, and init failures clean up created kobjects/groups.
