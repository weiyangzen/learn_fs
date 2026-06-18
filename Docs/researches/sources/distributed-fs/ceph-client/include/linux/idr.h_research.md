# sources/distributed-fs/ceph-client/include/linux/idr.h

## Purpose
Provides the legacy IDR and IDA allocation APIs: ID-to-pointer mapping via radix tree and plain integer ID allocation via xarray. It is widely used by kernel subsystems that need compact numeric handles without fixed-size tables.

## Important APIs, Types, And Functions
`struct idr` wraps a radix-tree root plus base and cyclic cursor. Initialization macros include `IDR_INIT_BASE`, `IDR_INIT`, and `DEFINE_IDR`; helpers include cursor get/set, lock wrappers, `idr_preload()`, allocation (`idr_alloc`, `idr_alloc_u32`, `idr_alloc_cyclic`), lookup, removal, replace, destroy, and iteration macros. `DEFINE_CLASS(idr_alloc, ...)` supplies cleanup integration that removes an allocated ID unless ownership is taken. `struct ida` wraps an xarray for ID-only allocation with `IDA_INIT`, `DEFINE_IDA`, `ida_alloc_range`, `ida_alloc`, min/max variants, `ida_free`, `ida_destroy`, and existence/find helpers.

## Control Flow
IDR users initialize, optionally preload memory, lock around modifications, allocate IDs for pointers, look up entries possibly under RCU, iterate or replace, then remove and destroy. IDA users allocate/free integer IDs without an external lock because the implementation handles locking internally. Cyclic allocation uses `idr_next` as a cursor and can be read/written with `READ_ONCE`/`WRITE_ONCE`.

## State And Persistence
State lives in radix tree/xarray nodes, free-space tags, `idr_base`, `idr_next`, and stored pointers or allocated bits. It is in-memory only; callers own object lifetimes and any RCU grace period after deletion.

## Dependencies And Integration Points
Depends on radix tree, xarray locking, GFP flags, percpu preload storage, cleanup helpers, and RCU synchronization conventions. Integrates with device minors, namespace IDs, request IDs, filesystem handles, and many driver subsystems.

## Risks
IDR lookups may be lockless only if callers manage object lifetime correctly. Forgetting `idr_preload_end()`, using the wrong allocation bounds/base, freeing objects before RCU readers are done, or mixing IDR lock wrappers with external locks incorrectly can cause leaks, UAF, or deadlocks. IDA differs from IDR in locking semantics, so porting between them is error-prone.

## Test Signals
Allocation/removal under concurrency, cyclic cursor wraparound, base-offset allocation, `idr_alloc_u32()` bounds, replace failure modes, iteration correctness during sparse IDs, RCU lookup lifetime tests, cleanup-class ownership transfer, and IDA range exhaustion/free/reuse tests.
