
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_migrate.h

## Purpose

`xe_migrate.h` exposes the migration subsystem API to BO movement, VM binding, page-table update, SR-IOV CCS, and GPU memory access callers. It intentionally hides `struct xe_migrate` internals while defining the callback contract used by page-table code to populate or clear PTE values in CPU or GPU command-buffer memory.

## Important APIs, Types, and Functions

- `enum xe_migrate_copy_dir`: selects VRAM-to-system or system-to-VRAM direction for pagemap-address copy helpers.
- `struct xe_migrate_pt_update_ops`: callback table with `populate`, `clear`, and optional `pre_commit`.
- `struct xe_migrate_pt_update`: embeddable update context carrying callback ops, VMA ops, generated scheduler/TLB jobs, tile id, and invalidation jobs.
- Public lifecycle and accessors: `xe_migrate_alloc()`, `xe_migrate_init()`, `xe_migrate_lrc()`, `xe_migrate_exec_queue()`, and `xe_migrate_get_vm()`.
- Data movement APIs: `xe_migrate_copy()`, `xe_migrate_resolve()`, `xe_migrate_vram_copy_chunk()`, `xe_migrate_to_vram()`, `xe_migrate_from_vram()`, `xe_migrate_clear()`, and `xe_migrate_access_memory()`.
- Synchronization APIs: `xe_migrate_wait()`, `xe_migrate_job_lock()`, `xe_migrate_job_unlock()`, and lockdep-only `xe_migrate_job_lock_assert()`.

## Control Flow

Consumers allocate/init a per-tile migration context, then call copy/clear/update helpers with BO resources or page-table update descriptors. For page-table updates, the caller supplies callbacks that know how to encode PTE content; migration chooses CPU or GPU execution and invokes those callbacks against either an `iosys_map` or command-buffer position. Returned `dma_fence` objects are the caller-visible completion signal.

## State and Persistence Behavior

The header establishes that migration operations are asynchronous unless a helper explicitly waits. The `xe_migrate_pt_update` object is caller-owned but receives transient job pointers while pre-commit hooks run. Clear flags persist through BO contents and CCS state rather than through header-managed state.

## Dependencies and Integration Points

It forward declares core Xe, TTM, DRM pagemap, sync, and scheduler types to keep compile dependencies small. The API is used by BO resource moves, VM bind code, page-fault rebinds, SR-IOV VF CCS handling, and tests.

## Risks and Edge Cases

- Callback contracts rely on consistent qword counts and offsets; the compiler cannot enforce that `populate` and `clear` write the exact number of qwords requested.
- Callers must handle returned `ERR_PTR` fences and partial-copy synchronization semantics from the implementation.
- Lock helper behavior differs for migration queues versus user queues, so callers must pass the correct queue object.

## Test Signals

Build coverage should catch signature drift. Runtime tests should exercise all public movement directions, clear flag combinations, CPU/GPU page-table update paths, and lockdep assertions for migration versus user queues.
