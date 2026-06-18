<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fb_pin.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fb_pin.c

## Purpose
This file pins framebuffer BOs into the address space needed for display scanout. It supports traditional GGTT pinning, DPT-backed pinning, fence installation for tiled scanout/FBC, physical alignment for legacy planes, VT-d guard space, and surface address calculation for plane state.

## Important APIs, Types, and Functions
Public functions are `intel_fb_pin_to_ggtt()`, `intel_fb_unpin_vma()`, `intel_plane_pin_fb()`, `intel_plane_unpin_fb()`, and `intel_fb_get_map()`. Internal helper `intel_fb_pin_to_dpt()` binds framebuffer objects into the DPT VM. Alignment helpers derive min display alignment, physical alignment, and VT-d guard requirements from framebuffer and plane state.

## Control Flow
GGTT pinning validates framebuffer BO state and power-of-two alignment, takes a runtime PM reference, increments restore pending pin count, locks the object with WW retries, attaches physical memory if needed or migrates to LMEM, pins pages, pins a display VMA with requested view/alignment/guard, optionally pins a fence, gets a VMA reference, unpins object pages, drops locks and RPM, and returns the VMA.

DPT pinning rejects async-bind VMs, ensures framebuffer BOs, locks/migrates/cache-levels the object, creates or reuses a VMA in the DPT address space, unbinds misplaced VMAs, pins globally, flushes for display, and returns a referenced VMA. `intel_plane_pin_fb()` chooses GGTT or DPT flow, pins the DPT page table itself into GGTT when needed, and computes `plane_state->surf` from either a physical DMA address or GGTT offset plus plane-specific surface offset. Unpin reverses the relevant VMA and DPT pins.

## State and Persistence Behavior
Pinning persists VMA pins, optional fence pins, `plane_state->ggtt_vma`, `plane_state->dpt_vma`, `plane_state->flags`, and `plane_state->surf` for the lifetime of the committed plane state. `display->restore.pending_fb_pin` tracks in-flight pins for restore sequencing. Unpin must clear plane-state VMA pointers and drop all references.

## Dependencies and Integration Points
The file depends on GEM object locking/migration/cache-level APIs, i915 VMA pinning, DPT VM helpers, runtime PM, framebuffer view computation from `intel_fb.c`, plane callbacks for physical needs and surface offsets, and display restore tracking. It is called from atomic plane commit paths.

## Risks
Pinning is deadlock-prone without correct WW retry handling. Failing to unpin pages, fences, DPT GGTT mappings, or VMA references leaks memory/address space. DPT VMs must not bind asynchronously because the display path does not synchronize with binding. LMEM migration for clear-color CCS must keep CPU-readable memory on small-BAR systems. Fence failure is fatal on pre-gen4 but tolerated later, affecting power-saving features.

## Test Signals
Signals include successful plane pin/unpin on GGTT and DPT framebuffers, WW deadlock retry tests, LMEM migration behavior, fence pinning on tiled pre-gen4/FBC planes, physical-alignment scanout, VT-d guard validation, restore pending-pin counters returning to zero, and no VMA/DPT leaks after failed pin paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fb_pin.c -->
