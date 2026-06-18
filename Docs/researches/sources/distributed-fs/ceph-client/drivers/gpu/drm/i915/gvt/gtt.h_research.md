# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/gtt.h

## Purpose
`gtt.h` declares the GVT GTT virtualization interface and the core data structures shared by GGTT/PPGTT emulation. It defines generic GTT entry operations, GMA index operations, MM objects, shadow page-table objects, scratch pages, out-of-sync pages, and exported functions used by submission, display, command parsing, and vGPU lifecycle code.

## Important Types
`struct intel_gvt_gtt_entry` wraps a 64-bit PTE value and GVT type. `struct intel_gvt_gtt_pte_ops` abstracts PTE read/write, present/PSE/IPS/64K-split bits, and PFN access. `struct intel_gvt_gtt_gma_ops` abstracts GGTT and PPGTT GMA index extraction. `struct intel_gvt_gtt` is device-global GTT state. `enum intel_gvt_gtt_type` enumerates GGTT PTEs, PPGTT leaf entries, root entries, and page-table levels. `struct intel_vgpu_mm` represents either a GGTT MM with virtual/host PTE arrays and partial write list or a PPGTT MM with guest/shadow PDPs, root type, shadowed flag, and list links. `struct intel_vgpu_ppgtt_spt` represents a shadow page table and its associated guest page tracking metadata.

## Control Flow And State
The header encodes the reference model: MM objects are `kref` managed with a separate pin count; PPGTT shadow pages are tracked in a radix tree; guest page table writes may be post-shadowed or moved to out-of-sync pages; GGTT state is split into guest-visible virtual entries and host hardware entries. Inline helpers `intel_vgpu_mm_get()`, `intel_vgpu_mm_put()`, and `intel_vgpu_destroy_mm()` define lifetime transitions.

## Dependencies And Integration Points
It includes `gt/intel_gtt.h`, Linux kref/mutex/radix tree APIs, and forward-declares GVT objects. The exported APIs are consumed by `gtt.c`, execlist/context submission, command parser paths that need PPGTT roots, display decoders that translate framebuffer bases, and vGPU lifecycle cleanup/reset code.

## Risks And Test Signals
Type enum ordering is semantically significant because implementation helpers test ranges and derive child/scratch types by arithmetic. Any new type must preserve those assumptions or update `gtt.c`. Struct fields carry concurrency and lifetime invariants; tests should stress kref/pin interactions, radix-tree cleanup, partial PTE list cleanup, and all exported init/clean/reset APIs.
