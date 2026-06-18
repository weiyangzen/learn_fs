<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sync.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sync.c

## Purpose

`xe_sync.c` parses user synchronization objects for Xe ioctls, creates dependencies, signals syncobjs/timeline syncobjs/user fences, and constructs input fences from queue/VM state.

## Important APIs, Types, and Functions

`xe_sync_entry_parse()` decodes `drm_xe_sync` entries. `xe_sync_entry_add_deps()` adds in-fence dependencies to scheduler jobs. `xe_sync_entry_wait()` and `xe_sync_needs_wait()` handle blocking waits. `xe_sync_entry_signal()` signals normal syncobj, timeline syncobj, or user fence outputs. `xe_sync_entry_cleanup()` releases references. `xe_sync_in_fence_get()` returns a queue/VM fence or fence array covering VM queues and TLB invalidation fences. User fence helpers manage `struct xe_user_fence` references and signaled status.

## Control Flow

Parse copies the uABI struct, rejects reserved flags, handles syncobj/timeline/user-fence types, validates LR mode restrictions and address alignment, looks up syncobjs, obtains input fences for wait entries, and preallocates chain fences for signal entries. User-fence signal paths add a timeline point to an internal syncobj, then register a dma-fence callback; on callback or already-signaled fence they queue ordered work to copy the value into the saved user address.

## State and Persistence Behavior

Each `xe_sync_entry` owns references to syncobjs, fences, chain fences, and optional user fence. `xe_user_fence` persists until callback work completes and all external references are dropped; it keeps an `mm_struct` reference and signaled flag.

## Dependencies and Integration Points

The file integrates DRM syncobj/timeline syncobj, dma-fence arrays/chains, scheduler jobs, Xe exec queues, Xe VMs, ordered workqueues, user access helpers, and queue last-fence/TLB-invalidation fence tracking.

## Risks and Test Signals

Risks include user fence writes after mm exit, missing cleanup on parse failures, LR mode signal restrictions, timeline seqno lookup failures, and fence-array reference leaks. Tests should cover all sync types, input versus signal paths, invalid flags/reserved fields, aligned/unaligned user fences, callback already-signaled path, cleanup idempotence, and VM queue fence aggregation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sync.c -->
