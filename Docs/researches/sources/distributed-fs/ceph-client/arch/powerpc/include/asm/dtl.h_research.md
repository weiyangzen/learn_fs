## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dtl.h

Purpose: defines the pseries hypervisor dispatch trace log entry format and DTL buffer management hooks.

Important APIs/types/functions: `struct dtl_entry`, `DISPATCH_LOG_BYTES`, `N_DISPATCH_LOG`, `DTL_LOG_*` masks, `dtl_cache`, `dtl_access_lock`, `register_dtl_buffer()`, and `alloc_dtl_buffers()`.

Control flow: implementation allocates per-CPU DTL buffers, registers them with firmware, and exposes log data under synchronization. The header only defines layouts and declarations.

State and persistence: per-CPU DTL buffers contain hypervisor-written dispatch/preempt/fault timing data in big-endian fields. `dtl_cache` and `dtl_access_lock` persist as allocation/synchronization state.

Dependencies and integration: depends on `asm/lppaca.h` and rwsem support. Used by pseries accounting, debugfs/proc reporting, and stolen-time analysis.

Risks and test signals: endian layout and buffer size must match firmware expectations. Test signals include pseries DTL registration, dispatch log reads, SPLPAR accounting, CPU hotplug buffer registration, and concurrency under `dtl_access_lock`.
