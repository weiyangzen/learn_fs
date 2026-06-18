# sources/distributed-fs/openafs/src/afs/DARWIN/osi_vm.c

## Purpose
Implements Darwin UBC/VM cache synchronization primitives for vcache recycling, storeback, invalidation, truncation, and setup.

## Important APIs, Types, And Functions
Exports `osi_VM_FlushVCache`, `osi_VM_StoreAllSegments`, `osi_VM_TryToSmush`, `osi_VM_FlushPages`, `osi_VM_Truncate`, `osi_VM_NukePages`, and `osi_VM_Setup`.

## Control Flow
Flush-vcache purges name cache for the vnode. Store-all drops the vcache lock and global lock, pushes dirty UBC pages with `ubc_msync_range` or `ubc_pushdirty`, then restores locks. Try-to-smush similarly drops locks and invalidates UBC contents. Flush-pages invalidates pages and updates UBC size if the vcache has valid stat data. Truncate sets UBC size to the new length. Setup initializes UBC info and size on older Darwin when the vnode is valid and stat data is available.

## State And Persistence
State is the vnode UBC object and size, dirty page state, name cache entries, and vcache length/stat bits. `osi_VM_NukePages` is intentionally empty.

## Dependencies And Integration Points
Depends on Darwin UBC APIs, vnode cache purge, global lock choreography, and generic OpenAFS callbacks that revoke callbacks, truncate files, store dirty segments, or recycle vcaches.

## Risks
Dropping locks around UBC calls allows concurrent page creation, as comments note. Size synchronization depends on `CStatd` and may be stale when stat data is invalid. Modern and older UBC APIs differ significantly. Empty `osi_VM_NukePages` means callers must tolerate no targeted invalidation.

## Test Signals
Read/write through mapped and unmapped paths, callback revocation, `fs flush`, truncation, dirty storeback on close/fsync, and vcache recycling should show correct file contents and no stale UBC pages.
