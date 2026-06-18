# sources/distributed-fs/ceph-client/drivers/infiniband/core/restrack.c

## Purpose
`restrack.c` maintains per-device RDMA resource tracking databases. It assigns stable IDs to tracked objects, records whether they are user or kernel resources, attaches task/name metadata, supports lookup by resource ID, and synchronizes object lifetime with krefs and completions.

## Important APIs, types, and functions
- `rdma_restrack_init()` and `rdma_restrack_clean()` allocate and destroy per-type XArrays.
- `rdma_restrack_count()` counts resources of a given type, optionally hiding driver-detail objects marked `RESTRACK_DD`.
- `rdma_restrack_new()`, `rdma_restrack_add()`, `rdma_restrack_del()` manage entry lifecycle.
- `rdma_restrack_get_byid()`, `rdma_restrack_get()`, and `rdma_restrack_put()` manage lookup references.
- `rdma_restrack_set_name()` and `rdma_restrack_parent_name()` attach task or kernel-name ownership.
- Static `res_to_dev()` maps a resource entry type back to its owning `ib_device`.

## Control flow and behavior
Initialization allocates `RDMA_RESTRACK_MAX` roots and initializes each XArray with allocation support. Adding a resource first resolves the owning device, skips XArray insertion for `no_track`, and then selects an ID strategy. QPs use their QPN, with SMI/GSI port encoded in the high byte and driver QPs marked as detail objects. Counters use the counter ID. Other resource types use cyclic XArray allocation. Deletion erases valid entries from the XArray, marks them invalid, drops the restrack kref, and waits for the release completion so callers know outstanding lookups are gone.

## State, persistence, and dependencies
Each `ib_device` owns `dev->res[type].xa` plus a cyclic `next_id`. Each `rdma_restrack_entry` owns `id`, `type`, `valid`, `no_track`, `user`, `task`, `kern_name`, `kref`, and completion state. Task ownership is reference-counted with `get_task_struct()` / `put_task_struct()`.

## Integration points
The file integrates with verbs object structures (`ib_pd`, `ib_cq`, `ib_qp`, `ib_mr`, `ib_ucontext`, `ib_srq`, `ib_dmah`), RDMA CM IDs, counters, and user-visible resource reporting paths such as nldev. It is called from resource create/destroy paths across the RDMA core and drivers.

## Risks and test signals
Risks include wrong `res_to_dev()` container mapping, duplicate QP IDs, forgetting `rdma_restrack_del()`, task reference leaks, use-after-free if deletions do not wait for lookups, and `no_track` entries retaining stale task references. Test signals include resource leak warnings in `rdma_restrack_clean()`, nldev resource count checks, concurrent `get_byid()`/destroy stress, driver QP detail filtering tests, and task-exit tests for user resource ownership.
