<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_vm.c -->
# sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_vm.c

Purpose: Implements z/VM DIAG 2FC data collection and raw debugfs exposure for hypfs.

Important APIs/types/functions: Defines query strings for local/all guests, global `diag2fc_guest_query`, low-level `diag2fc()`, public `diag2fc_store()` and `diag2fc_free()`, debugfs structs `dbfs_d2fc_hdr` and `dbfs_d2fc`, callback `dbfs_diag2fc_create()`, `dbfs_file_2fc`, `hypfs_vm_init()`, and `hypfs_vm_exit()`.

Control flow: `diag2fc()` builds a parameter list with EBCDIC-converted user and group queries, calls DIAG 2FC, and returns either residual-derived size/count information or a hypervisor return code. `diag2fc_store()` first queries required size, vmallocs size plus optional header offset, then retries until a store succeeds. Init runs only on z/VM, preferring all-guest query if authorized, falling back to local-guest query, then registers raw debugfs `diag_2fc`.

State and persistence: `diag2fc_guest_query` records the authorized query mode for later raw and filesystem reads. Each snapshot is vmalloced and freed per read.

Dependencies and integration points: Used by `hypfs_vm_fs.c` to create the mounted tree and by `hypfs_dbfs.c` for raw debugfs. Depends on z/VM DIAG 2FC, EBCDIC conversion, exception-table guarded inline assembly, TOD timestamps, and machine type detection.

Risks: Authorization failures are represented as `-EACCES`; systems without all-guest authorization must fall back correctly. The size-query/store loop must handle changing guest counts. Raw data format depends on `struct diag2fc_data` layout.

Test signals: z/VM systems with all-guest and local-only privileges, changing guest population during reads, raw `diag_2fc` header validation, and non-z/VM no-op behavior.

Source read size: 142 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_vm.c -->
