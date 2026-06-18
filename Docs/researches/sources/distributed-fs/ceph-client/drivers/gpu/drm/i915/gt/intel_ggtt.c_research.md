# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ggtt.c

## Purpose
This file implements GGTT probing, initialization, PTE encoding, binding, invalidation, suspend/resume, aliasing PPGTT setup, GuC reservations, and cleanup for i915 GTs. It covers Gen6+ GMCH-backed GGTT and modern Gen8+ 64-bit PTE paths, while delegating older x86 GMCH handling to `intel_ggtt_gmch.c`.

## Important APIs, Types, and Functions
Public functions include `i915_ggtt_probe_hw()`, `i915_ggtt_create()`, `i915_ggtt_enable_hw()`, `i915_ggtt_init_hw()`, `i915_init_ggtt()`, `i915_ggtt_suspend_vm()`, `i915_ggtt_suspend()`, `i915_ggtt_resume_vm()`, `i915_ggtt_resume()`, `i915_ggtt_driver_release()`, `i915_ggtt_driver_late_release()`, `intel_ggtt_bind_vma()`, `intel_ggtt_unbind_vma()`, and `intel_ggtt_read_entry()`.

Important implementation groups are PTE encoders (`mtl_ggtt_pte_encode()`, `gen8_ggtt_pte_encode()`, `snb_pte_encode()`, `ivb_pte_encode()`, `byt_pte_encode()`, `hsw_pte_encode()`, `iris_pte_encode()`), insert/clear paths for Gen8 and Gen6, GGTT invalidation (`gen6_ggtt_invalidate()`, `gen8_ggtt_invalidate()`, `guc_ggtt_invalidate()`), binder updates through `MI_UPDATE_GTT`, and probe helpers for BAR/GSM mapping and scratch-page setup.

## Control Flow
Probe assigns each GT a GGTT, then chooses Gen8, Gen6, or legacy GMCH probe based on platform generation. Probe maps the GSM page-table aperture, creates scratch pages, selects PTE functions, sets VMA ops, and installs invalidation callbacks. Init reserves low/error-capture regions, GuC top address space, and guard/scratch pages, then optionally creates an aliasing PPGTT for platforms that need it.

Binding converts VMA resources into GGTT PTEs with guard pages and scratch fill. On platforms requiring GPU-side GGTT updates, it tries the BCS0 bind context and emits `MI_UPDATE_GTT`; otherwise it writes PTEs through CPU mappings. Suspend evicts or clears mappings while avoiding unnecessary PTE rewrites. Resume clears the address space, rebinds all bound VMAs, restores UC mappings, invalidates TLBs, optionally flushes CPU caches, and restores fences.

## State and Persistence Behavior
`struct i915_ggtt` persists BAR resources, GSM mapping, mappable aperture size, total GGTT size, scratch encoding, error-capture node, GuC firmware reservation, aliasing PPGTT, fence list, and invalidation/PTE callbacks. VMA `bound_flags` and `page_sizes_gtt` are updated during bind. Scratch PTEs fill unallocated or guard regions to keep speculative GPU accesses valid.

## Dependencies and Integration Points
This file integrates with PCI BAR/config probing, stolen memory, VGT ballooning, GuC submission/TLB invalidation, BCS0 bind context, GEM object/VMA binding, PPGTT code, runtime PM, fences, DPT/GGTT suspend paths, MOCS/PAT cache policy, VT-d workarounds, and error capture.

## Risks
PTE encoding is platform-sensitive; cache, local-memory, PAT, and address-mask mistakes can corrupt memory or break display/GPU access. GGTT invalidation must happen after all PTE writes are visible. Binder updates depend on the bind context being awake and not wedged; fallback paths must remain correct for reset/error capture. Aperture reservations and guard pages prevent GPU prefetch and GuC address issues, so changing them can cause hangs. Suspend/resume must not race pinned VMAs or leave stale mappings.

## Test Signals
Signals include successful GGTT probe/init on Gen6 through modern platforms, correct reported GGTT/GMADR sizes, working VMA bind/unbind and aperture mmap, GuC firmware loading with reserved top GGTT space, VT-d/BXT workaround stability, suspend/resume with display and GEM workloads, reset/error-capture success, PTE readback tests, and no GPU faults after GGTT invalidation.
