# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/gtt.c

## Purpose
`gtt.c` implements GVT graphics translation table virtualization. It emulates guest GGTT MMIO reads/writes, shadows guest per-process GTT page tables into host-addressable shadow page tables, translates guest graphics memory addresses to guest physical addresses, manages scratch pages, tracks guest page-table writes, and restores host GGTT state after power management.

## Important APIs And Functions
Device-level APIs are `intel_gvt_init_gtt()`, `intel_gvt_clean_gtt()`, and `intel_gvt_restore_ggtt()`. Per-vGPU APIs include `intel_vgpu_init_gtt()`, `intel_vgpu_clean_gtt()`, `intel_vgpu_reset_ggtt()`, `intel_vgpu_invalidate_ppgtt()`, `intel_vgpu_destroy_all_ppgtt_mm()`, `intel_vgpu_emulate_ggtt_mmio_read()`, `intel_vgpu_emulate_ggtt_mmio_write()`, `intel_vgpu_gma_to_gpa()`, `intel_vgpu_get_ppgtt_mm()`, `intel_vgpu_put_ppgtt_mm()`, `intel_vgpu_pin_mm()`, `intel_vgpu_unpin_mm()`, `intel_vgpu_flush_post_shadow()`, and `intel_vgpu_sync_oos_pages()`.

The main internal subsystems are Gen8 PTE operations, GMA index operations, shadow page-table allocation/population/invalidation, GGTT virtual/host entry management, partial GGTT PTE write handling, out-of-sync page-table optimization, and scratch page tree setup.

## Control Flow
Initialization sets Gen8 operation tables, allocates a device scratch page, optionally preallocates out-of-sync pages, and initializes LRU locking. A vGPU then creates a GGTT `intel_vgpu_mm`, allocates virtual GGTT plus saved host aperture/hidden arrays, resets host GGTT entries to the scratch page, initializes page-table tracking lists, and builds per-type scratch page tables.

For GGTT MMIO writes, the code normalizes the offset, rejects invalid access sizes, ignores ballooned-out GM ranges, handles split 4-byte updates by queuing partial PTE state, maps present guest GFNs to DMA addresses, falls back to scratch on mapping failure, updates the virtual guest GGTT copy, unmaps the previous host mapping, writes the host GGTT PTE, and invalidates GGTT. It also invalidates cached last context descriptors if their LRCA entry was overwritten.

For PPGTT, `intel_vgpu_get_ppgtt_mm()` finds or creates an MM object keyed by guest PDP roots. Creation shadows roots immediately if the vGPU is attached. Shadowing walks guest page tables, allocates `intel_vgpu_ppgtt_spt` pages, registers write protection, recursively populates child tables, maps leaf guest pages, splits unsupported 64K entries into 4K PTEs, and splits 2M entries when host mapping cannot support them. Guest page-table writes enter `ppgtt_write_protection_handler()`, which updates or defers shadow entries depending on write size. Before workload submission, post-shadow and out-of-sync lists are flushed back into consistent shadow state.

`intel_vgpu_gma_to_gpa()` translates through GGTT by reading the virtual GGTT PTE. For PPGTT it walks shadow roots and child SPTs using GMA index helpers, reading the guest final entry at the last level so the returned address is a guest physical address.

## State And Persistence
Global state in `gvt->gtt` includes PTE/GMA ops, scratch page, optional out-of-sync free/use lists, and a PPGTT MM LRU list protected by `ppgtt_mm_lock`. Per-vGPU state includes `ggtt_mm`, PPGTT MM list, SPT radix tree keyed by shadow MFN, out-of-sync and post-shadow lists, and per-level scratch page tree. Host GGTT aperture/hidden PTE arrays are saved per vGPU for restore. No disk persistence exists; state is reconstructed during driver/vGPU init and restored to hardware on resume.

## Dependencies And Integration Points
The implementation depends on i915 GGTT structures, MMIO runtime power helpers, VFIO DMA read/write from `gvt.h`, GVT page tracking, DMA map/unmap cache helpers, tracepoints, execlist submission state, and guest workload submission ordering. It is on the hot path for framebuffer decoding, command parsing, context shadowing, and display base translation.

## Risks And Edge Cases
This is a high-risk memory translation layer. Incorrect refcounts or invalidation can leak DMA mappings or leave stale host PTEs. Partial PTE writes must not expose half-written shadow mappings. 64K and 2M splitting paths must clean up already-mapped pages on failure. Out-of-sync mode is disabled by default but, if enabled, weak synchronization before workload submission can produce stale shadows. LRU reclaim cannot invalidate pinned MMs. `intel_vgpu_gma_to_gpa()` reports a generic "invalid mm type" message even for translation failures, so diagnostics can be misleading.

## Test Signals
Important signals include GGTT read/write emulation for 4- and 8-byte accesses, split PTE updates, invalid GM range handling, DMA map failure fallback to scratch, PPGTT creation for 3-level and 4-level roots, guest page-table write protection updates, post-shadow flush before workload submission, 64K/2M split coverage, MM pin/LRU reclaim behavior, clean vGPU teardown with empty SPT tree, suspend/resume GGTT restore, and framebuffer GMA-to-GPA translation matching guest mappings.
