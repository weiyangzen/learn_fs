# sources/distributed-fs/ceph-client/drivers/infiniband/core/frmr_pools.c

## Purpose
This file implements a per-RDMA-device pool manager for FRMR handles. It lets providers cache, pin, reuse, age, and destroy fast-registration memory-region handles keyed by requested FRMR properties, reducing repeated provider allocations while bounding idle resources.

## Important APIs, Types, And Functions
The public entry points are `ib_frmr_pools_init()`, `ib_frmr_pools_cleanup()`, `ib_frmr_pools_set_aging_period()`, `ib_frmr_pools_set_pinned()`, `ib_frmr_pool_pop()`, and `ib_frmr_pool_push()`. Pools are keyed by `struct ib_frmr_key`, stored in an rb-tree under `struct ib_frmr_pools`, and implemented as `struct ib_frmr_pool` objects with regular and inactive `struct frmr_queue` lists. Provider allocation and destruction are abstracted through `struct ib_frmr_pool_ops`.

## Control Flow
Initialization allocates `struct ib_frmr_pools`, initializes the rb-tree lock, stores provider operations, creates the aging workqueue, sets the default 60-second aging period, and attaches it to `device->frmr_pools`. `ib_frmr_pool_pop()` finds or creates the key's pool and returns a handle from the regular queue, inactive queue, or provider `create_frmrs()`. `ib_frmr_pool_push()` returns a handle to the regular queue and schedules aging when the pool becomes non-empty. Aging destroys previously inactive handles, moves the regular queue to inactive, and reschedules only when more aging remains; pinned mode preserves `pinned_handles` by destroying only excess handles.

## State And Persistence
Pool state is runtime-only and per `ib_device`. Each pool tracks active/inactive queues, `in_use`, `max_in_use`, `pinned_handles`, the canonical key, and delayed aging work. Handles are batched into page-sized allocations, with queue `ci` acting as a stack index. Pool queues/counters are protected by `pool->lock`; rb-tree lookup and insertion use `pools->rb_lock`.

## Dependencies And Integration Points
The implementation depends on provider `ib_frmr_pool_ops` for `create_frmrs()`, `destroy_frmrs()`, and optional `build_key()`, plus `ib_check_mr_access()`. Providers and MR users must initialize pools before pop/push and clean up only after all handles are returned.

## Risks And Test Signals
Risks include queue accounting mistakes across page boundaries, failed queue push after provider allocation, races between concurrent create/find, aging work during cleanup, pinned-handle shrink/expand behavior, and handle leaks if callers do not push all popped MRs. Tests should cover concurrent pop/push, same-key pool creation races, distinct key matching including block-count tolerance, pinned growth/shrink, aging-period changes, allocation failure injection, page-boundary counts, and cleanup with leak detection.
