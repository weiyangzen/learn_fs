# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/page_track.c

## Purpose
`page_track.c` is the GVT-side registry for guest page write tracking. It registers handlers per guest frame number, enables/disables backend write protection, and dispatches KVM page-track writes.

## Important APIs, Types, And Functions
Public functions are `intel_vgpu_find_page_track`, `intel_vgpu_register_page_track`, `intel_vgpu_unregister_page_track`, `intel_vgpu_enable_page_track`, `intel_vgpu_disable_page_track`, and `intel_vgpu_page_track_handler`. Runtime records use `struct intel_vgpu_page_track`.

## Control Flow
Registration checks for duplicates, allocates a record, stores callback/private data, and inserts it into `vgpu->page_track_tree`. Enable/disable look up the record and call backend add/remove functions. Unregister removes backend write protection if active and frees the record. Dispatch looks up by `gpa >> PAGE_SHIFT` and either calls the handler or removes write protection in failsafe mode.

## State And Persistence
State lives in the vGPU radix tree. `tracked` mirrors backend write-protection state; `priv_data` belongs to the caller.

## Dependencies And Integration Points
It depends on KVMGT `intel_gvt_page_track_add/remove` and is called from KVM page-track notifier code under `vgpu_lock`.

## Risks
Radix-tree and backend protection state must stay synchronized. Duplicate/unknown GFNs return errors. Failsafe removes backend protection without updating `tracked`, so teardown must tolerate stale local state.

## Test Signals
Register/enable/disable/unregister flows, write traps reaching handlers, duplicate rejection, unknown-GFN errors, backend protection table updates, failsafe trap suppression, and leak-free teardown.
