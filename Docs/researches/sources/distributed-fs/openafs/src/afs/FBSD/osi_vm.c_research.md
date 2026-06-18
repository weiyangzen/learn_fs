# sources/distributed-fs/openafs/src/afs/FBSD/osi_vm.c

## Purpose
Implements FreeBSD VM and buffer-cache synchronization for OpenAFS vcaches, including page cleaning, invalidation, callback flush, truncation, and vcache recycle checks.

## Important APIs, Types, And Functions
Exports `osi_VM_FlushVCache`, `osi_VM_StoreAllSegments`, `osi_VM_TryToSmush`, `osi_VM_FlushPages`, and `osi_VM_Truncate`. Helpers/macros wrap vnode locking and version-specific VM object write locks and dirty checks.

## Control Flow
Flush-vcache locks the vnode interlock, calls `osi_fbsd_checkinuse`, holds the vnode, drops the global lock, purges name cache, restores locks, and drops the hold. Store-all asserts the vnode is locked, checks `v_object` dirty state, drops the vcache/global locks, write-locks the VM object, synchronously cleans pages, then restores locks. Try-to-smush rejects doomed vnodes, ensures an exclusive vnode lock, cleans VM pages, retries `vinvalbuf(V_SAVE)` up to five times, restores prior lock state, and reacquires the global lock. Flush-pages removes VM pages and invalidates buffers. Truncate calls `vnode_pager_setsize`.

## State And Persistence
State includes vnode `v_object`/`v_bufobj.bo_object`, dirty page flags, buffer cache contents, vnode interlock/lock state, vcache locks, and vnode pager size.

## Dependencies And Integration Points
Depends on FreeBSD VM object APIs, vnode/buffer invalidation, `osi_fbsd_checkinuse`, OpenAFS callback invalidation, file storeback, truncation, and vcache recycling paths.

## Risks
The file comments emphasize FreeBSD vnode/VM locking protocol drift. Calling with someone else's exclusive lock panics in smush. `OBJPC_SYNC` choices trade correctness/performance. `osi_VM_FlushPages` asserts the vnode is locked and will fail if generic callers violate that contract.

## Test Signals
Dirty mmap/writeback, callback revocation, `fs flush`, truncation, vnode recycle under cache pressure, concurrent page faults, and FreeBSD-version builds should validate this file. Watch for `TryToSmush retrying vinvalbuf` warnings and lock assertion failures.
