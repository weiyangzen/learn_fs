# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v4_1_0.c

## Purpose

`mmhub_v4_1_0.c` provides the MMHUB 4.1.0 backend for GMC v12-era devices. It programs the same MMHUB VM plumbing as v3 files but adapts to v4 register names, LO32 fault-status fields, updated client IDs, SR-IOV host-owned register policy, and DAGB-based clock-gating controls.

## Important APIs, Types, And Functions

The exported table is `mmhub_v4_1_0_funcs`. Key callbacks are `init`, `get_fb_location`, `get_mc_fb_offset`, `gart_enable`, `gart_disable`, `set_fault_enable_default`, `set_clockgating`, `get_clockgating`, and `setup_vm_pt_regs`. Internal helpers build invalidation requests, print L2 fault status, initialize system/GART apertures, TLB/cache, VMID contexts, invalidation engines, and medium-grain clock gating.

## Control Flow

`mmhub_v4_1_0_init()` fills the single `AMDGPU_MMHUB0(0)` VM hub offsets, including v4-specific `regMMVM_L2_PROTECTION_FAULT_STATUS_LO32`, `regMMVM_L2_BANK_SELECT_RESERVED_CID2`, and `regMMVM_CONTEXTS_DISABLE`. `gart_enable` sets VMID0 page-table base and GART range, skips full system aperture setup on VFs, initializes TLB/cache, enables context0, disables identity aperture on PF paths, configures VMIDs 1-15, and programs 18 invalidation engines. Invalidation requests intentionally force `FLUSH_TYPE` to zero because this backend uses legacy MMHUB invalidation.

## State And Persistence Behavior

Hardware registers retain aperture, cache, TLB, context, and invalidation-range state across normal execution until reset or `gart_disable`. Default page address is computed as `mem_scratch.gpu_addr - vram_start + vm_manager.vram_base_offset`, which differs from older variants using `amdgpu_gmc_vram_mc2pa`. Clock-gating state is only partially maintained: active code toggles DAGB0/DAGB1 read/write return tap-chain FGCG disable bits, while older `MM_ATC_L2_MISC_CG` and light-sleep reporting paths are behind `#if 0`.

## Dependencies And Integration Points

The file depends on generated `mmhub_4_1_0` headers, `soc24_enum.h`, SOC15 macros, SR-IOV helpers, and core AMDGPU GMC/VM structures. It is selected by `gmc_v12_0.c`. It uses `amdgpu_mmhub_init_client_info` for fault-client decoding and participates in generic VM invalidation via `amdgpu_vmhub_funcs`.

## Risks

`get_clockgating` is disabled by `#if 0`, so it does not report active flags even if hardware is gated. Light-sleep control is similarly inactive. V4 fault status is read only from LO32; if future fields needed by diagnostics are in HI32, this implementation will omit them. The `setup_vmid_config` initial read uses offset `i` before writing with `i * hub->ctx_distance`, which is worth preserving only if intentional for this register layout.

## Test Signals

Probe on v4.1.0 hardware, run GPUVM/GART workloads, inject MMHUB faults and verify LO32 field decoding, exercise PF versus VF paths, and toggle MC MGCG flags while checking DAGB registers. Suspend/resume and GPU reset should ensure `vm_contexts_disable`, fault-control, and aperture registers are restored.
