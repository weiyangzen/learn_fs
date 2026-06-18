# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_4_2_0_offset.h

## Purpose

`mmhub_4_2_0_offset.h` is a generated AMDGPU ASIC register-offset header for MMHUB IP version 4.2.0. It maps MMHUB hardware register names to SOC15 register offsets and base-index selectors. The primary consumer is `drivers/gpu/drm/amd/amdgpu/mmhub_v4_2_0.c`, which includes this file with the matching `mmhub_4_2_0_sh_mask.h` field definitions and uses the constants to program MMHUB virtual memory, GART, cache, fault, invalidation, aperture, XGMI, and clock-gating state.

This file contains no executable runtime logic. Its job is to be the compile-time address contract between the v4.2.0 MMHUB driver and the hardware register map. It is especially important because the driver derives repeated-register spacing from these offsets, such as VM context distance, page-table address distance, invalidation request distance, and invalidation address-range distance.

## Important APIs, Types, and Constants

The header defines no C functions, structs, enums, storage objects, or inline helpers. Its public interface is 357 `reg...` register-offset macros and 357 matching `reg..._BASE_IDX` macros, guarded by `_mmhub_4_2_0_OFFSET_HEADER`.

Important register families include:

- `regDAGB0_CNTL_MISC2` and `regDAGB1_CNTL_MISC2`: DAGB control registers used by `mmhub_v4_2_0_update_medium_grain_clock_gating()` to toggle fine-grain clock-gating bits.
- `regMM_CANE_ICG_CTRL`: MM CANE clock-gating/control offset exposed by the v4.2.0 MMHUB map.
- `regMMMC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_LSB/MSB`: default system-aperture page target programmed from `adev->mem_scratch.gpu_addr`.
- `regMMVM_L2_CNTL`, `regMMVM_L2_CNTL2`, `regMMVM_L2_CNTL3`, `regMMVM_L2_CNTL4`, and `regMMVM_L2_CNTL5`: L2 VM cache controls programmed during GART enable and disable.
- `regMMVM_L2_PROTECTION_FAULT_*`: protection-fault control, status, fault-address, and default-address registers used for fault policy, dummy-page redirection, and fault reporting.
- `regMMVM_L2_CONTEXT1_IDENTITY_APERTURE_*` and `regMMVM_L2_CONTEXT_IDENTITY_PHYSICAL_OFFSET_*`: identity aperture controls disabled during normal GART setup.
- `regMMMC_VM_L2_PERFCOUNTER*`, `regMMUTCL2_PERFCOUNTER*`, and `regMM_ATC_L2_PERFCOUNTER*`: performance-counter configuration and result registers.
- `regMMMC_VM_FB_LOCATION_*`, `regMMMC_VM_AGP_*`, and `regMMMC_VM_SYSTEM_APERTURE_*`: framebuffer, AGP, and system-aperture bounds used to define visible memory ranges.
- `regMMVM_CONTEXT0_CNTL` through `regMMVM_CONTEXT15_CNTL`: VMID context control registers. VMID0 is configured as the system domain; VMIDs 1-15 are configured for user VM contexts.
- `regMMVM_INVALIDATE_ENG0_*` through `regMMVM_INVALIDATE_ENG17_*`: 18 invalidation engines with semaphore, request, acknowledgment, and address-range registers.
- `regMMVM_CONTEXT[0-15]_PAGE_TABLE_BASE_ADDR_*`, `START_ADDR_*`, and `END_ADDR_*`: split 64-bit page-table base and bounds registers for VM contexts.
- `regMMVM_L2_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` and per-context variants: PF/VF PTE-cache fragment-size controls.
- `regMMVM_PCIE_ATS_CNTL`, `regMMMC_VM_PCIE_ATOMIC_SUPPORTED`, and northbridge/PCI window registers: ATS, PCIe atomic, and platform address-window controls.
- `regMMMC_VM_XGMI_LFB_CNTL`, `regMMMC_VM_XGMI_LFB_SIZE`, `regMMMC_VM_XGMI_GPUIOV_ENABLE`, and related host/local/cacheable address registers: XGMI and platform memory steering.
- `regMM_ATC_L2_*`: ATC L2 control, cache-data, group RT class, status, clock-gating, and SDP-port registers.
- `regMMVM_IOMMU_*` and `regMMMC_VM_FB_OFFSET`: PSP/IOMMU and framebuffer-offset registers.

The generated address-block sections are:

- `mmhub_dagb_dagbdec`, base address `0x60000`
- `mmhub_mm_cane_mmcanedec`, base address `0x60c20`
- `mmhub_mmutcl2_mmvmsharedpfdec`, base address `0x66000`
- `mmhub_mmutcl2_mmvml2pfdec`, base address `0x66090`
- `mmhub_mmutcl2_mmvml2prdec`, base address `0x66210`
- `mmhub_mmutcl2_mmatcl2prdec`, base address `0x66250`
- `mmhub_mmutcl2_mmvml2pldec`, base address `0x66290`
- `mmhub_mmutcl2_mmatcl2pldec`, base address `0x662f0`
- `mmhub_mmutcl2_mmvmsharedvcdec`, base address `0x66400`
- `mmhub_mmutcl2_mmvml2vcdec`, base address `0x66440`
- `mmhub_mmutcl2_mmvmsharedvfdec`, base address `0x667c0`
- `mmhub_mmutcl2_mmvmsharedhvdec`, base address `0x667e0`
- `mmhub_mmutcl2_mmatcl2dec`, base address `0x669d0`
- `mmhub_mmutcl2_mmvml2pspdec`, base address `0x66b40`
- `mmhub_mmutcl2_mmvmsharedpspdec`, base address `0x66b90`

Most `_BASE_IDX` values are `2` for the MMUTCL2/MMVM/ATC blocks, while DAGB and CANE entries use base index `1`. Consumers pass the offset macro to SOC15 accessors such as `RREG32_SOC15()`, `WREG32_SOC15()`, `RREG32_SOC15_OFFSET()`, `WREG32_SOC15_OFFSET()`, and `SOC15_REG_OFFSET()`, and the accessor machinery uses the generated offset/base-index pairing to reach the correct register aperture.

## Control Flow

There is no runtime control flow in this header. Runtime behavior emerges when consumers use these constants.

In `mmhub_v4_2_0.c`, the typical control flow is:

1. `mmhub_v4_2_0_init()` iterates over active MMHUB instances from `adev->aid_mask` and initializes each `struct amdgpu_vmhub` with SOC15 offsets built from this header.
2. `mmhub_v4_2_0_mid_init()` records fixed register offsets for page-table base, invalidation sem/request/ack, context control, fault status/control, bank-select, and context-disable state. It also computes repeated-register spacing from pairs such as `regMMVM_CONTEXT1_CNTL - regMMVM_CONTEXT0_CNTL` and `regMMVM_INVALIDATE_ENG1_ADDR_RANGE_LO32 - regMMVM_INVALIDATE_ENG0_ADDR_RANGE_LO32`.
3. `mmhub_v4_2_0_gart_enable()` calls the MID helper sequence: page-table base/bounds setup, system aperture setup, L1 TLB setup, L2 cache setup, system-domain enablement, identity-aperture disablement, VMID context setup, and invalidation-engine range setup.
4. `mmhub_v4_2_0_mid_setup_vm_pt_regs()` writes the split low/high page-table base registers for the selected VMID and each active MMHUB instance.
5. `mmhub_v4_2_0_mid_init_system_aperture_regs()` writes FB, AGP, system aperture, default page, and protection-fault default-address registers. It skips selected registers in SR-IOV VF mode because the PF owns those apertures.
6. `mmhub_v4_2_0_mid_init_cache_regs()` reads/writes L2 cache control registers and seeds `regMMVM_L2_CNTL3`, `regMMVM_L2_CNTL4`, and `regMMVM_L2_CNTL5` from local default constants before applying field-level policy from the shift/mask header.
7. `mmhub_v4_2_0_mid_setup_vmid_config()` loops over VMIDs 1-15, using context-distance and address-distance values derived from this file to program context control and page-table bounds.
8. `mmhub_v4_2_0_mid_program_invalidation()` loops over 18 invalidation engines and uses the generated engine address-distance to program full address ranges for each engine.
9. `mmhub_v4_2_0_get_invalidate_req()` constructs an invalidate request using `MMVM_INVALIDATE_ENG0_REQ` fields from the sibling shift/mask header; the request is later written through the VMHUB infrastructure using offsets initialized from this file.
10. Suspend/resume paths in `mmhub_v4_2_0_xcp_suspend()` and `mmhub_v4_2_0_xcp_resume()` disable or re-enable the same register groups for selected XCP/MMHUB instance masks.

Other direct integration is lighter: `imu_v12_1.c` includes this offset header but currently performs IMU RAM loading through GC offsets. The include keeps MMHUB v4.2.0 offsets available to the IMU v12.1 unit as that integration evolves.

## State and Persistence Behavior

The macros are immutable compile-time constants and hold no runtime state. They do not allocate memory, persist data, or perform hardware access by themselves.

Runtime state lives in MMHUB hardware registers and AMDGPU structures:

- `adev->vmhub[AMDGPU_MMHUB0(i)]` stores SOC15 register addresses and spacing values derived from this header.
- `adev->gmc`, `adev->gart`, `adev->vm_manager`, `adev->mmhub`, `adev->mem_scratch`, and `adev->dummy_page_addr` provide runtime addresses and policy values written into registers named here.
- MMHUB registers retain state only according to hardware power/reset behavior. GPU reset, suspend, runtime power transitions, XCP partition suspend/resume, or PF/VF ownership changes can require the driver to rewrite the programmed state.

The most persistence-sensitive state is the VM/GART programming: page-table base and bounds, aperture bounds, L1/L2 enablement, invalidation engine ranges, fault defaults, and context controls. If those registers are reset or mismatched with the driver-side `amdgpu_vmhub` offsets, MMHUB clients such as display, video, SDMA, VPE, JPEG, and VCN can translate through stale or invalid VM state.

SR-IOV is an explicit state boundary. Several helper paths return early for VFs because the host/PF programs inaccessible or PF-owned MMHUB registers. The offset header is common, but runtime access rights differ by mode.

## Dependencies

Direct dependencies are intentionally minimal:

- A C preprocessor/compiler.
- The include guard `_mmhub_4_2_0_OFFSET_HEADER`.
- AMD generated register naming conventions using `reg...` offsets and `reg..._BASE_IDX` selectors.

Functional dependencies are broader:

- `mmhub_4_2_0_sh_mask.h` supplies field masks and shifts for every field-level operation using `REG_SET_FIELD()` and `REG_GET_FIELD()`.
- `soc15_common.h` and SOC15 accessors translate these offsets into actual MMIO register accesses for a selected hardware IP and instance.
- `mmhub_v4_2_0.c` provides the v4.2.0 MMHUB implementation and local default values for several L2 cache control registers.
- AMDGPU VM/GMC infrastructure supplies `struct amdgpu_device`, `struct amdgpu_vmhub`, `struct amdgpu_mmhub_funcs`, `struct amdgpu_vmhub_funcs`, `AMDGPU_MMHUB0()`, `GET_INST()`, `for_each_inst()`, `amdgpu_gmc_pd_addr()`, `amdgpu_gmc_vram_mc2pa()`, `lower_32_bits()`, and `upper_32_bits()`.
- Higher-level GMC dispatch in `gmc_v12_0.c` selects `mmhub_v4_2_0_funcs` for the matching hardware generation and marks active MMHUB VM hubs.

## Integration Points

The primary integration point is the `mmhub_v4_2_0_funcs` function table. It exposes MMHUB operations for initialization, framebuffer location readout, MC framebuffer offset readout, VM page-table programming, GART enable/disable, default fault handling, clock gating, and XGMI information.

The `amdgpu_vmhub` integration is particularly dependent on this header. `mmhub_v4_2_0_mid_init()` stores offsets for:

- `ctx0_ptb_addr_lo32` and `ctx0_ptb_addr_hi32`
- `vm_inv_eng0_sem`, `vm_inv_eng0_req`, and `vm_inv_eng0_ack`
- `vm_context0_cntl`
- `vm_l2_pro_fault_status` and `vm_l2_pro_fault_cntl`
- `vm_l2_bank_select_reserved_cid2`
- `vm_contexts_disable`

It also computes:

- `ctx_distance`
- `ctx_addr_distance`
- `eng_distance`
- `eng_addr_distance`

Those derived distances are then used by shared VM code and by local loops that write repeated context and invalidation-engine registers. This means the offset header is not just a list of constants; it defines layout invariants that driver loops rely on.

MMHUB v4.2.0 also integrates with:

- GART and VMID setup, through `setup_vm_pt_regs`, `gart_enable`, and `gart_disable`.
- XGMI address discovery, through `regMMMC_VM_XGMI_LFB_CNTL` and `regMMMC_VM_XGMI_LFB_SIZE`.
- Fault reporting, through `regMMVM_L2_PROTECTION_FAULT_STATUS_LO32` and client-name lookup initialized from `mmhub_client_ids_v4_2_0`.
- Clock/power management, through `regMM_ATC_L2_MISC_CG`, `regDAGB0_CNTL_MISC2`, and `regDAGB1_CNTL_MISC2`.
- XCP partition suspend/resume, through instance masks passed to the MID helpers.
- Ring owners that select `AMDGPU_MMHUB0(...)` as their VM hub, including multimedia and DMA engines in nearby AMDGPU code.

The file must remain synchronized with its sibling shift/mask header and the actual ASIC register specification. Mixing this offset header with another MMHUB generation's masks can compile but program the wrong fields or wrong registers.

## Risks and Edge Cases

- Hardware-generation mismatch: MMHUB 4.2.0 offsets differ from earlier versions such as 3.x and 4.1.0. Reusing the wrong offset map can silently redirect writes to unrelated registers.
- Repeated-layout assumptions: the driver derives context and invalidation-engine distances from adjacent offsets. If generated offsets stop being uniform, loops over VMIDs or invalidation engines will write incorrect registers.
- Base-index mismatch: each offset has a matching `_BASE_IDX`. Incorrect generated base-index values can make SOC15 accessors target the wrong MMIO base even when the offset number looks correct.
- Untyped macros: register offsets are raw preprocessor constants. The compiler cannot enforce pairing between a `reg...` offset, the matching field masks, and the expected hardware IP version.
- Split 64-bit address registers: many addresses are programmed through LO32/HI32 pairs with shifts by 12, 18, 24, or 44 depending on register semantics. Offset mistakes or swapped halves can corrupt aperture and page-table addressing.
- SR-IOV access limits: VF mode must skip PF-owned or inaccessible registers. The same constants exist for PF and VF builds, so runtime access checks remain critical.
- Fault-policy sensitivity: protection-fault control/status/default-address registers decide whether faults are retried, redirected, logged, interrupted, or escalated. Wrong offsets can cause hidden memory corruption, fault storms, or GPU hangs.
- Invalidation correctness: `regMMVM_INVALIDATE_ENG*_REQ/ACK/SEM` offsets are central to TLB shootdown. Bad offsets can leave stale translations visible to MMHUB clients.
- Multi-instance/AID behavior: v4.2.0 code loops over `adev->aid_mask` and uses `GET_INST(MMHUB, i)`. Per-instance offset initialization must match the active hardware topology.
- Status and performance-counter registers: not every register named here is a safe write target. Some are read-only status/counter outputs or require specific sequencing.
- Generated-file maintenance: manual edits are risky because the file is a hardware register contract. Regeneration from the authoritative register database is safer than one-off edits.

## Test Signals

Useful validation signals for changes touching this header or its consumers include:

- Compile coverage for AMDGPU with MMHUB v4.2.0 and GMC v12 support enabled, catching renamed, removed, or mismatched macros.
- Boot or module-load testing on hardware using MMHUB 4.2.0, with successful `gmc_v12_0` initialization and `mmhub_v4_2_0_funcs` selection.
- Register readback around `mmhub_v4_2_0_init()` confirming `amdgpu_vmhub` offsets and derived distances match expected hardware layout.
- GART and VM workloads that exercise VMID0 setup, VMIDs 1-15, page-table base updates, page-table bounds, FB/AGP/system apertures, and dummy-page handling.
- TLB invalidation stress tests across all 18 invalidation engines, checking request/ack behavior and absence of stale translations.
- VM fault injection or fault-stop policy tests that verify `MMVM_L2_PROTECTION_FAULT_STATUS_LO32` decoding, default fault enable toggles, and dummy-page redirection behavior.
- XGMI-connected platform tests that validate physical node count, physical node ID, and segment-size extraction from `MMMC_VM_XGMI_LFB_*` registers.
- Suspend/resume and XCP partition suspend/resume tests confirming MMHUB GART state is disabled and restored for the targeted instance masks.
- SR-IOV PF/VF tests confirming VF paths avoid inaccessible registers while PF paths still program shared MMHUB state.
- Clock-gating tests for `AMD_CG_SUPPORT_MC_MGCG` and `AMD_CG_SUPPORT_MC_LS`, with readback of `MM_ATC_L2_MISC_CG` and DAGB control registers.
- Media/display/DMA workloads that route through `AMDGPU_MMHUB0(...)` VM hubs, such as JPEG, VCN, VPE, SDMA, and display paths.

## Summary

`mmhub_4_2_0_offset.h` is the generated register-offset map for AMD MMHUB 4.2.0. It contributes no executable logic, but it is central to MMHUB v4.2.0 because the driver uses these constants to build SOC15 register addresses, configure VM/GART hardware, compute repeated-register spacing, program invalidation engines, handle faults, read XGMI and framebuffer state, and toggle clock-gating controls. The main maintenance rule is to keep this offset header synchronized with the matching shift/mask header and the hardware register database, because small offset or base-index errors can become VM translation, aperture, invalidation, or power-management failures at runtime.
