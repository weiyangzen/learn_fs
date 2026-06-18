# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_stolen.c

## Purpose
This file manages BIOS/GPU-reserved stolen memory as i915 memory regions and GEM objects. It discovers valid stolen ranges, excludes hardware-reserved WOPCM/GSCPSMI areas, allocates objects from a `drm_mm` allocator, wraps stolen allocations in SG tables, and exposes a display-facing stolen-memory interface.

## Important APIs, Types, and Functions
Key public setup and query functions are `i915_gem_stolen_smem_setup`, `i915_gem_stolen_lmem_setup`, `i915_gem_object_create_stolen`, `i915_gem_object_is_stolen`, and `i915_display_stolen_interface`. Internal helpers handle node insertion/removal, stolen validation, platform reserved range decoding (`g4x_get_stolen_reserved`, `gen6_get_stolen_reserved`, `vlv_get_stolen_reserved`, `gen7_get_stolen_reserved`, `chv_get_stolen_reserved`, `bdw_get_stolen_reserved`, `icl_get_stolen_reserved`), memory-region init/release, and stolen object ops.

## Control Flow
Initialization rejects vGPU, older VT-d cases, invalid ranges, and conflicting system memory reservations. It adjusts old platforms where GTT lives inside stolen memory, records the full DSM, discovers reserved top-of-stolen areas, shrinks usable region, initializes `i915->mm.stolen`, and may disable userspace access on MTL A0. LMEM stolen setup derives DSM size/base from LMEMBAR, MCR tile range, DSMBASE, or MTL GGC, then creates an IO mapping when direct or BAR access is possible.

Object creation allocates or reserves a `drm_mm_node`, initializes a private GEM object with contiguous stolen ops, pins its pages immediately, and releases nodes on failure. Page get creates a one-entry SG table with DMA address `dsm.stolen.start + offset`; release removes the node and memory-region membership.

## State and Persistence Behavior
Persistent driver state includes `i915->dsm.stolen`, `dsm.reserved`, `dsm.usable_size`, `i915->mm.stolen`, `stolen_lock`, memory-region `private` flags, optional region `iomap`, and per-object `obj->stolen`. Stolen contents persist outside normal system memory and are often reused for BIOS/display allocations.

## Dependencies and Integration Points
It integrates with PCI BAR/resource discovery, uncore register reads, GT MCR, `drm_mm`, stolen display-parent interface, GGTT error-capture poisoning in debug builds, memory-region creation, local-memory region logic, and many platform feature macros.

## Risks
Platform register decoding is fragile and safety-critical; reusing reserved WOPCM/GSCPSMI space can hang hardware. System stolen reservation conflicts point to BIOS/kernel resource bugs. CPU accessibility differs between system stolen, local stolen, small-BAR, and direct DSM modes. Immediate pinning and contiguous allocation limit flexibility. Debug poisoning must avoid stop_machine inversion.

## Test Signals
Boot logs for stolen size/usable size, BIOS framebuffer handoff, display stolen allocations, stolen object create/pin/release tests, MTL GGC decoding, small-BAR DGFX behavior, vGPU/VT-d disable paths, and debug GEM poisoning are relevant signals.
