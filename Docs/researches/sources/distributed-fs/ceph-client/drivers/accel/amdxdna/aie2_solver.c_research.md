# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_solver.c

Purpose: provides a small column/resource solver used by AMD XDNA to allocate AIE partitions to hardware contexts and select a default DPM level that satisfies QoS requirements.

Important APIs/functions: `xrsm_init()` creates a solver state with one resource group and action callbacks. `xrs_allocate_resource()` sanity-checks a request, rejects duplicate request IDs, creates a solver node, finds or shares a partition, calls the load callback, sets a DPM level, and stores callback state. `xrs_release_resource()` finds a node by request ID, unloads the associated context, and frees or decrements the partition. Helpers calculate GOPS from QoS, validate feasible throughput, choose DPM level from the configured clock list, scan bitmaps for free columns, and share compatible non-exclusive partitions.

Control flow: AIE2 hardware-context initialization calls allocation with CDO partition possibilities and QoS. Load/unload callbacks in `aie2_pci.c` create/destroy firmware contexts and assign columns. The solver itself is single-threaded by contract; callers must provide locking.

State and persistence: `solver_state` owns a bitmap of occupied columns, a list of allocated solver nodes, and a list of partition nodes with share counts. State lives for the DRM device lifetime through managed allocation.

Dependencies: uses Linux bitmaps/lists, DRM logging, `init_config` clock/action callbacks, and AIE QoS structs from `aie2_solver.h`.

Risks: no internal locking; misuse can corrupt lists or bitmap. Sharing logic currently marks all partitions non-exclusive, so isolation depends on higher-level request semantics. `sanity_check()` only checks max-clock feasibility, not all layout constraints.

Test signals: duplicate RID rejection, full-column exhaustion, partition sharing, release of shared partitions, invalid QoS/CDO inputs, DPM selection under multiple active nodes, and caller-side locking under parallel context creation.
