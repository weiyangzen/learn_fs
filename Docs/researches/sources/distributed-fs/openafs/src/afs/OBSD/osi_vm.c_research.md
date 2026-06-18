# sources/distributed-fs/openafs/src/afs/OBSD/osi_vm.c

## Purpose
OpenBSD VM/cache coherency helpers for flushing, invalidating, and resizing vnode pages associated with AFS vcaches.

## Important APIs, Types, and Functions
Defines `osi_VM_FlushVCache`, `osi_VM_StoreAllSegments`, `osi_VM_TryToSmush`, `osi_VM_FlushPages`, and `osi_VM_Truncate`.

## Control Flow
Flush paths drop GLOCK and call `cache_purge` plus `uvm_vnp_uncache`, then reacquire GLOCK. Try-to-smush temporarily releases the vcache write lock around `osi_VM_FlushVCache`. FlushPages purges pages and resets UVM size to the vcache length. Truncate calls `uvm_vnp_setsize`.

## State and Persistence
Mutates OpenBSD VM page cache and vnode UVM size only. Does not itself write dirty pages back to servers; `osi_VM_StoreAllSegments` is a no-op.

## Dependencies and Integration Points
Depends on OpenBSD UVM, name cache purge, common AFS vcache locks, callback revocation paths, flush commands, and truncation flows.

## Risks
No-op store-all means callers must not rely on this function to persist dirty data on OpenBSD. Flush functions drop locks, so concurrent page creation can occur after return. The Solaris-style `activeV` comment notes stronger behavior elsewhere than OpenBSD provides.

## Test Signals
Callback revocation should purge stale pages, truncation should adjust mapped size, cache recycle should not retain stale UVM pages, and concurrent readers/writers should not panic under UVM assertions.
