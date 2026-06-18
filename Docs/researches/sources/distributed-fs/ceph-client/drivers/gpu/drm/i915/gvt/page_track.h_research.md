# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/page_track.h

## Purpose
`page_track.h` declares the GVT guest-page write-tracking interface and abstracts storage of per-GFN handlers from the KVMGT backend.

## Important APIs, Types, And Functions
`gvt_page_track_handler_t` receives the page-track record, GPA, written data, and byte count. `struct intel_vgpu_page_track` stores callback, tracked state, and private data. The header declares find/register/unregister/enable/disable/dispatch APIs.

## Control Flow
No executable flow exists here. Normal use is register a GFN, enable tracking, receive writes through `intel_vgpu_page_track_handler`, then disable/unregister during teardown.

## State And Persistence
The defined record is stored by `page_track.c` in `vgpu->page_track_tree` and persists per vGPU until unregister/teardown.

## Dependencies And Integration Points
It includes `linux/types.h`, forward-declares GVT types, and is used by page-track users and KVMGT notifier callbacks.

## Risks
Callbacks must handle arbitrary guest write sizes and offsets. The `tracked` flag mirrors backend state and should only be changed through the API.

## Test Signals
Compile coverage, write-trap delivery, handler private-data behavior, enable/disable idempotence, and cleanup.
