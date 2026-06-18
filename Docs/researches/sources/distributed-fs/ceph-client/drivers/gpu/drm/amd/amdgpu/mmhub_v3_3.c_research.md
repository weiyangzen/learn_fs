# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_3.c

## Purpose

`mmhub_v3_3.c` implements MMHUB 3.3/3.4 support for later GMC v11 devices. It keeps the familiar GART, aperture, TLB, cache, VMID, fault-control, invalidation, framebuffer, and clock-gating callbacks, but adds client maps selected by exact MMHUB IP version plus standalone walker and TLS setup used by this generation.

## Important APIs, Types, And Functions

The exported symbol is `mmhub_v3_3_funcs`. Core callbacks are `mmhub_v3_3_init`, `mmhub_v3_3_gart_enable`, `mmhub_v3_3_gart_disable`, `mmhub_v3_3_set_fault_enable_default`, `mmhub_v3_3_setup_vm_pt_regs`, `mmhub_v3_3_get_fb_location`, `mmhub_v3_3_get_mc_fb_offset`, `mmhub_v3_3_set_clockgating`, and `mmhub_v3_3_get_clockgating`. Generation-specific helpers include `mmhub_v3_3_init_client_info`, `mmhub_v3_3_init_saw_regs`, and `mmhub_v3_3_enable_tls`. It contains three client maps: `mmhub_client_ids_v3_3`, `mmhub_client_ids_v3_3_1`, and `mmhub_client_ids_v3_4`.

## Control Flow

`init` populates VM hub offsets and calls `mmhub_v3_3_init_client_info`, which switches on `amdgpu_ip_version(adev, MMHUB_HWIP, 0)` for 3.3.0, 3.3.1, 3.3.2, or 3.4.0 maps. `gart_enable` runs the standard sequence, then configures the standalone walker with VMID0 page-table base/start/end, enables only SAW context0, sets snooped PDE/PTE requests, and writes DAGB L1TLB TLS registers. Fault printing special-cases CID `0x140` as `UMSCH`, then falls back to the registered client table.

## State And Persistence Behavior

Persistent state is in MMHUB registers and `adev->vmhub[AMDGPU_MMHUB0(0)]`. SAW context registers persist independently of normal VM context registers. TLS state is written directly to two DAGB L1TLB registers. `get_invalidate_req` uses `flush_type ? : 1`, ensuring a nonzero hardware flush type if callers pass zero. Clock-gating state is reflected in `MM_ATC_L2_MISC_CG` bits.

## Dependencies And Integration Points

The file uses generated `mmhub_3_3_0` register definitions, `navi10_enum.h`, SOC15 helpers, VM/GMC fields, and IP-version dispatch. It is selected by `gmc_v11_0.c`. It integrates with common VM invalidation and fault printing via `amdgpu_vmhub_funcs`, with fault diagnostics through `amdgpu_mmhub_init_client_info`, and with power management through MC MGCG/LS callbacks.

## Risks

The exact IP-version-to-client-map mapping is a diagnostic correctness risk; wrong maps make faults hard to triage. SAW and TLS register writes are extra hardware state that must stay synchronized with normal VMID0 programming. No SR-IOV guards are used around several PF-owned-looking registers, so selection must match hardware virtualization policy. The hard-coded SAW context disable mask `0xfffe` assumes 16 contexts and context0-only usage.

## Test Signals

Test by probing each supported MMHUB IP version and forcing VM faults from VCN/JPEG/VPE/ISP clients to validate names. GART tests should confirm both normal and SAW walkers translate VMID0 addresses. Clock-gating tests should validate `MM_ATC_L2_MISC_CG` bit changes. Suspend/resume and GPU reset should verify SAW/TLS registers are restored.
