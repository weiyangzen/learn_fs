# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0.c

## Purpose
This file implements the GFXHUB 3.0 backend for GC 11 devices. It programs the newer `regGCVM_*` and `regGCMC_*` register namespace and exposes GFX VM hub callbacks for GMC v11.

## Important APIs, Types, and Functions
The public export is `gfxhub_v3_0_funcs`. It includes callbacks for FB base/offset discovery, VM page-table base writes, GART enable/disable, default fault handling, and VM hub initialization. Private VM hub functions create invalidate requests and print L2 protection fault status using the local `gfxhub_client_ids[]` table.

## Control Flow and State
The flow follows the modern GFXHUB pattern: `init()` seeds `adev->vmhub[AMDGPU_GFXHUB(0)]`; `gart_enable()` handles SR-IOV VF FB location programming, programs VMID0 GART page tables, system apertures, dummy/default fault pages, L1/L2 cache controls, context0, identity aperture disablement, contexts 1-15, and invalidate engine ranges. `set_fault_enable_default()` additionally sets `CP_DEBUG.CPG_UTCL1_ERROR_HALT_DISABLE` before applying L2 protection default bits, preventing CP halt on page faults. User contexts use `amdgpu_noretry` for retry policy rather than per-device `adev->gmc.noretry`.

## Dependencies and Integration Points
The file depends on GC 11.0.0 offset/mask/default headers, SOC15 helpers, and `navi10_enum.h`. `gmc_v11_0_set_gfxhub_funcs()` selects this implementation by default for GC 11 devices that do not require v3.0.3 or v11.5-specific tables.

## Risks and Test Signals
Risks include global retry-policy mismatch, CP debug side effects, SR-IOV register access, and incorrect context stride offsets. Test signals include GC 11 boot/resume, VM fault logging without CP halt, KFD retry/no-retry workloads, GFXOFF TLB invalidation, and VF boot paths.
