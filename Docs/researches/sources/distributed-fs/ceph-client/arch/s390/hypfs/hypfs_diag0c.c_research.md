<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_diag0c.c -->
# sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_diag0c.c

Purpose: Exposes z/VM DIAG 0C per-CPU diagnostic data through the hypfs debugfs framework.

Important APIs/types/functions: Defines `diag0c_fn()`, `diag0c_store()`, `dbfs_diag0c_free()`, `dbfs_diag0c_create()`, `dbfs_file_0c`, `hypfs_diag0c_init()`, and `hypfs_diag0c_exit()`. Uses `struct hypfs_diag0c_data`, `struct hypfs_diag0c_entry`, and `struct hypfs_diag0c_hdr` from UAPI/asm hypfs headers.

Control flow: `diag0c_store()` locks the CPU hotplug read side, allocates a vector indexed by possible CPU and a real-storage DMA-capable result structure sized for online CPUs, fills per-online-CPU pointers, runs `diag0c_fn()` on each CPU using `on_each_cpu()`, and returns the collected data. The debugfs create callback adds a TOD timestamp and header length/count before returning the buffer.

State and persistence: No global diagnostic state persists beyond the registered debugfs file. Each read allocates a fresh snapshot.

Dependencies and integration points: Available only on z/VM (`machine_is_vm()`). Integrates with CPU hotplug locking, per-CPU execution, DIAG 0C, hypfs debugfs callbacks, and TOD clock.

Risks: DIAG 0C requires 8-byte alignment and real storage, so allocation flags matter. CPU hotplug must be locked while building and using the CPU vector. `on_each_cpu()` latency affects debugfs reads.

Test signals: z/VM debugfs `diag_0c` reads with CPU hotplug stress, non-z/VM no-op init/exit, per-CPU count/header validation, and allocation failure injection.

Source read size: 124 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_diag0c.c -->
