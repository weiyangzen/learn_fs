# sources/distributed-fs/ceph-client/fs/dlm/memory.c

## Purpose
`memory.c` centralizes slab cache creation and allocation/free wrappers for core DLM objects: writequeue entries, midcomms handles, lowcomms messages, lock blocks, resource blocks, callbacks, and lock value blocks.

## Important APIs, Types, And Functions
Lifecycle functions are `dlm_memory_init()` and `dlm_memory_exit()`. Allocation wrappers include `dlm_allocate_rsb()`, `dlm_free_rsb()`, `dlm_allocate_lkb()`, `dlm_free_lkb()`, `dlm_allocate_lvb()`, `dlm_free_lvb()`, `dlm_allocate_mhandle()`, `dlm_free_mhandle()`, `dlm_allocate_writequeue()`, `dlm_free_writequeue()`, `dlm_allocate_msg()`, `dlm_free_msg()`, `dlm_allocate_cb()`, and `dlm_free_cb()`.

## Control Flow
Initialization creates caches in dependency order and unwinds on allocation failure. RSB and LKB frees use `call_rcu()`; callback `__free_rsb_rcu()` also frees an attached LVB, while `__free_lkb_rcu()` frees user-argument storage and user LVB pointers for user locks. Exit calls `rcu_barrier()` before destroying caches.

## State And Persistence
State is limited to static cache pointers. Allocated objects live in kernel memory until their DLM refcount/RCU lifecycle releases them.

## Dependencies And Integration Points
Cache constructors come from `lowcomms.c` and `midcomms.c`. RCU lifetime is required because locks and resources can be visible to concurrent readers. User lock cleanup integrates with `user.c` structures stored in `lkb_ua`.

## Risks
Because most allocations use `GFP_ATOMIC`, memory pressure can surface as operation failures in lock and communication paths. Missing `rcu_barrier()` would risk destroying caches before deferred frees complete. Freeing user arguments only for `DLM_DFL_USER_BIT` locks must remain consistent with lock ownership flags.

## Test Signals
Allocation-failure injection, module unload under recently freed locks/resources, and KASAN/RCU diagnostics are the primary signals. Lock/unlock tests should not leak `dlm_user_args`, LVBs, callbacks, or message handles.
