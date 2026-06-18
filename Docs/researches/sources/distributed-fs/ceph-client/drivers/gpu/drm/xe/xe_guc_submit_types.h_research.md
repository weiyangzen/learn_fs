# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_submit_types.h

Purpose: defines GuC submission data layouts shared between host and GuC-facing submission code, especially parallel submission scratch/WQ memory and devcoredump snapshots.

Important types/constants: WQ status/type masks, GuC ID and ring tail masks, `PARALLEL_SCRATCH_SIZE`, `WQ_SIZE`, `struct guc_sched_wq_desc`, cacheline-padded `struct sync_semaphore`, `struct guc_submit_parallel_scratch`, and `struct xe_guc_submit_exec_queue_snapshot`.

Control flow: `xe_guc_submit.c` initializes `guc_submit_parallel_scratch`, appends NOOP or multi-LRC WQ entries, reads WQ head/tail/status for snapshots, and prints the snapshot fields later from devcoredump/debug paths.

State/persistence: the scratch structure is memory shared with GuC through the LRC parallel scratch mapping. The snapshot persists a point-in-time copy of queue identity, scheduling properties, LRC snapshots, schedule state, parallel WQ contents, and multi-queue metadata.

Dependencies/integration: depends on `xe_hw_engine_types.h` for engine classes and `XE_HW_ENGINE_MAX_INSTANCE`; implicitly depends on LRC snapshot definitions through pointers. ABI layout and packed descriptors must remain compatible with GuC expectations.

Risks/test signals: layout, size, and mask changes can corrupt GuC WQ interpretation. Tests should cover WQ wrap/noop behavior, multi-LRC width bounds, snapshot allocation/printing, and early sequence wrap behavior in parallel queue submission.
