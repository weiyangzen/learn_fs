# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_3_0_default.h

## Purpose

`mmhub_2_3_0_default.h` is a generated AMDGPU ASIC register-default header for MMHUB IP version 2.3.0. It records reset/default values for MMHUB register blocks as C preprocessor constants named `mm..._DEFAULT`. The header is included by `drivers/gpu/drm/amd/amdgpu/mmhub_v2_3.c` together with the matching `mmhub_2_3_0_offset.h` and `mmhub_2_3_0_sh_mask.h` headers, giving the MMHUB v2.3 driver a consistent register-address, field-mask, and hardware-default contract.

This file is compile-time register metadata, not executable logic. Its value is the hardware baseline it captures for MMHUB request gateways, memory endpoint arbitration, power-control state, L1/L2 translation hardware, stream/TLS state, MMVM contexts, invalidation engines, virtualization apertures, IOMMU/ATS controls, and performance counters.

## Important APIs, Types, and Constants

The file defines no C functions, structs, enums, or storage objects. Its public interface is 1,164 `#define` constants guarded by `_mmhub_2_3_0_DEFAULT_HEADER`.

Important constant families include:

- `mmDAGB0_*_DEFAULT`: defaults for DAGB read/write clients, read/write control, GMI control, address/data gateway burst and lazy timers, virtual-channel controls, TLB/data/misc credits, pending-state registers, FIFO state, clock/light-sleep control, performance counters, and reserved registers.
- `mmMMEA0_*_DEFAULT`: defaults for memory endpoint arbitration and address decoding. These include DRAM/IO client-to-group maps, group-to-VC maps, priority aging/queuing/fixed/urgency controls, priority quanta, address normalization, bank/hash/column/row selection, SDP arbitration, EDC/DSM controls, clock control, error status, and always-on misc state.
- `mmPCTL_*_DEFAULT`: power-control defaults for deep sleep, power-gating ignore bits, slice busy/deep-sleep allow state, register-engine controls, state-save ranges, exclusion sets, status, performance counters, and reserved values.
- `mmMMMC_VM_MX_L1_*_DEFAULT`: L1 TLB status and performance-counter defaults, plus the MMHUB 2.3-specific `TLS0` stream-prefetch/control region. `mmMMMC_VM_MX_L1_TLS0_CNTL_DEFAULT` is nonzero (`0xa5a50004`), while the per-stream `CNTL0` through `CNTL37`, start/end address pairs, invalidation stream, pending, protection-fault, and IOMMU-fault defaults are zero.
- `mmMMVM_L2_SAW_*_DEFAULT`: SAW/context defaults that appear in this 2.3.0 register set before the shared L2/ATC blocks.
- `mmMM_ATC_L2_*_DEFAULT`: ATC L2 control, cache data, group RT class, status, clock-gating, memory power, SDP port, and performance-counter defaults.
- `mmMMVM_L2_*_DEFAULT`: L2 cache, invalidate, dummy-page fault, protection-fault, identity-aperture, context-disable, bank-selection, parity, interrupt-log, clock, GCR, busy, and PTE-cache-dump defaults.
- `mmMMVM_CONTEXT[0-15]_*_DEFAULT`: VM context control defaults and page-table base/start/end register defaults. Context controls default to `0x007ffe80`; page-table address and reserve registers default to zero.
- `mmMMVM_INVALIDATE_ENG[0-17]_*_DEFAULT`: invalidation engine semaphore, request, acknowledgment, address-range, and reserve defaults. Request defaults are `0x02f80000`; semaphores, acknowledgments, address ranges, and reserves reset to zero.
- `mmMMMC_VM_FB_SIZE_OFFSET_VF[0-31]_DEFAULT` and `mmMMVM_PCIE_ATS_CNTL_VF_[0-31]_DEFAULT`: SR-IOV virtual-function framebuffer sizing and PCIe ATS defaults, all reset to zero in this file.
- Shared aperture and platform defaults such as `mmMMMC_VM_NB_*_DEFAULT`, `mmMMMC_VM_FB_LOCATION_*_DEFAULT`, `mmMMMC_VM_AGP_*_DEFAULT`, `mmMMMC_VM_SYSTEM_APERTURE_*_DEFAULT`, `mmMMMC_VM_LOCAL_HBM_ADDRESS_*_DEFAULT`, `mmMMMC_VM_MARC_*_DEFAULT`, and `mmMMMC_SHARED_*_DEFAULT`.

The generated address-block sections are:

- `mmhub_dagbdec`
- `mmhub_mmea_mmeadec0`
- `mmhub_pctldec`
- `mmhub_l1tlb_mmutcl1pfdec`
- `mmhub_l1tlb_mmutcl1pldec`
- `mmhub_l1tlb_mmutcl1prdec`
- `mmhub_l1tlb_mmvmtlspfdec`
- `mmhub_mmutcl2_mmatcl2dec`
- `mmhub_mmutcl2_mmvml2pfdec`
- `mmhub_mmutcl2_mmvml2vcdec`
- `mmhub_mmutcl2_mmvml2pldec`
- `mmhub_mmutcl2_mmvml2prdec`
- `mmhub_mmutcl2_mmvmsharedhvdec`
- `mmhub_mmutcl2_mmvmsharedpfdec`
- `mmhub_mmutcl2_mmvmsharedvcdec`
- `mmhub_mmutcl2_mmatcl2pfcntrdec`
- `mmhub_mmutcl2_mmatcl2pfcntldec`
- `mmhub_mmutcl2_mmvml2ptdec`
- `mmhub_mmutcl2_mmvml2indec`
- `mmhub_mmutcl2_mml2tlbpfdec`
- `mmhub_mmutcl2_mml2tlbpldec`
- `mmhub_mmutcl2_mml2tlbprdec`

## Control Flow

There is no runtime control flow in this header. The preprocessor exposes constants that consumers use as register-programming seeds.

The principal consumer is `drivers/gpu/drm/amd/amdgpu/mmhub_v2_3.c`. That driver includes this header after the matching offset and shift/mask headers, then uses selected defaults while enabling and maintaining the MMHUB/GART path:

- `mmhub_v2_3_gart_enable()` sequences MMHUB setup: optional SR-IOV VF framebuffer-location programming, GART aperture programming, system aperture setup, L1 TLB enablement, L2 cache setup, system-domain enablement, identity-aperture disablement, VMID context setup, and invalidation-engine range initialization.
- `mmhub_v2_3_init_cache_regs()` explicitly seeds `MMVM_L2_CNTL3`, `MMVM_L2_CNTL4`, and `MMVM_L2_CNTL5` from `mmMMVM_L2_CNTL3_DEFAULT`, `mmMMVM_L2_CNTL4_DEFAULT`, and `mmMMVM_L2_CNTL5_DEFAULT`, then applies runtime field overrides with `REG_SET_FIELD()` before writing the registers.
- `mmhub_v2_3_setup_vmid_config()` reads existing context-control registers, applies policy fields for VMIDs 1-15, and programs page-table bounds. It relies on the register families defaulted here and on distance calculations derived from the sibling offset header.
- `mmhub_v2_3_program_invalidation()` initializes all 18 invalidation engines by writing address ranges for `MMVM_INVALIDATE_ENG0` through `ENG17`, matching the repeated invalidation-engine defaults in this header.
- `mmhub_v2_3_set_fault_enable_default()` updates the runtime default fault-handling policy for `MMVM_L2_PROTECTION_FAULT_CNTL`, whose reset default is defined here.
- `mmhub_v2_3_update_medium_grain_clock_gating()`, `mmhub_v2_3_update_medium_grain_light_sleep()`, and `mmhub_v2_3_get_clockgating()` manipulate DAGB and ATC L2 clock/light-sleep registers that have reset defaults in this header.

The control pattern is therefore data-driven: the driver selects a register, starts from either hardware readback or a `*_DEFAULT` macro when the reset baseline matters, patches fields according to runtime policy, and writes the final value through SOC15 register accessors.

## State and Persistence Behavior

The constants are immutable compile-time data. They do not store runtime state, allocate memory, or persist anything independently.

Runtime state lives in GPU registers and AMDGPU device structures such as `adev->vmhub[AMDGPU_MMHUB0(0)]`, `adev->gmc`, `adev->gart`, `adev->vm_manager`, and `adev->mmhub`. The driver rewrites MMHUB state during initialization, GART enable/disable, page-table setup, TLB invalidation setup, fault-policy changes, and clock-gating transitions.

Persistence boundaries are hardware and power-management driven:

- GPU reset or power transitions can return registers to these default values, requiring the driver to reapply runtime policy.
- PCTL state-save range and exclusion defaults describe hardware save/restore behavior for MMHUB power-control flows, but the header itself does not perform save/restore.
- In SR-IOV VF mode, `mmhub_v2_3_gart_enable()` programs VF framebuffer location registers because VBIOS does not initialize those VF copy registers. Other clock-gating operations return early for VFs to avoid inaccessible or PF-owned MMHUB registers.
- Address and context registers default mostly to zero, but zero is a reset baseline, not a valid configured GART or VM address space. The driver replaces those defaults with page-table, aperture, scratch-page, and dummy-page addresses during setup.

## Dependencies

Direct dependencies are intentionally small:

- A C preprocessor/compiler.
- The include guard `_mmhub_2_3_0_DEFAULT_HEADER`.
- Consumers that follow AMD's generated `mm...` register naming convention.

Functional use depends on sibling generated headers:

- `mmhub_2_3_0_offset.h` supplies register offsets such as `mmMMVM_L2_CNTL3`, `mmMMVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32`, and `mmMMVM_INVALIDATE_ENG0_REQ`.
- `mmhub_2_3_0_sh_mask.h` supplies field masks and shifts used by `REG_SET_FIELD()` and `REG_GET_FIELD()`.

Runtime integration depends on AMDGPU/SOC15 infrastructure:

- SOC15 register access macros such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET`.
- AMDGPU VM/GMC structures and helpers including `struct amdgpu_device`, `struct amdgpu_vmhub`, `amdgpu_gmc_pd_addr()`, `amdgpu_gmc_vram_mc2pa()`, `lower_32_bits()`, and `upper_32_bits()`.
- MMHUB and VMHUB function tables, notably `amdgpu_mmhub_funcs` and `amdgpu_vmhub_funcs`.
- Device IP-version dispatch through `amdgpu_ip_version(adev, MMHUB_HWIP, 0)`.

## Integration Points

`gmc_v10_0_set_mmhub_funcs()` selects `mmhub_v2_3_funcs` for MMHUB IP versions 2.3.0, 2.4.0, and 2.4.1. The selected implementation lives in `amdgpu/mmhub_v2_3.c` and includes this default header.

The header must be used as a matched set with `mmhub_2_3_0_offset.h` and `mmhub_2_3_0_sh_mask.h`. Mixing defaults from this file with another MMHUB revision's offsets or masks can compile but program wrong registers or wrong bit fields.

The file is part of a family of generated MMHUB register-description headers for other IP versions (`mmhub_2_0_0_default.h`, `mmhub_3_0_1_default.h`, and others). Those alternatives are selected by their corresponding driver files and should not be manually substituted unless the underlying register model is known to be compatible.

## Risks and Edge Cases

- Hardware-generation mismatch: the defaults describe MMHUB 2.3.0 register semantics. Reusing them for an incompatible revision can corrupt VM, cache, aperture, invalidation, or power-control programming.
- Untyped macro misuse: all values are raw integer constants. The compiler cannot prove that `mmMMVM_L2_CNTL3_DEFAULT` is paired with `mmMMVM_L2_CNTL3`, or that a default matches the active mask header.
- Default is not policy: many reset values are intentionally overwritten by `mmhub_v2_3.c`. For example, L2 cache behavior, VMID context controls, fault handling, page-table bounds, and invalidation ranges are runtime decisions.
- Zero address defaults: page-table, aperture, MARC, system aperture, TLS stream start/end, and fault-address registers reset to zero. Treating reset zeroes as valid configured addresses can route translations or faults to address zero.
- TLS0 stream region sensitivity: this header exposes 38 TLS0 stream control entries with split start/end address pairs. Any future consumer that programs these must keep stream index, address split, invalidation, pending, and fault-status semantics aligned.
- Invalidation engine repetition: all 18 engines share a repeated layout and default request value. Incorrect engine-distance calculations or offset-header mismatches can make loops program the wrong engine.
- Reserved and status registers: some defaults describe status or reserved registers rather than safe write values. Reserved defaults such as all-ones DAGB reserve entries should not be treated as normal writable initialization data.
- SR-IOV constraints: PF and VF MMHUB access differ. VF paths must avoid inaccessible registers while still programming VF copy registers that firmware leaves unset.
- Fault-handling sensitivity: `MMVM_L2_PROTECTION_FAULT_*`, `MMVM_CONTEXT*_CNTL`, dummy-page, and IOMMU-fault defaults influence whether faults are redirected, retried, interrupted, logged, or fatal. Bad defaults or overrides can cause VM fault storms, hidden data loss, or GPU hangs.
- Power-management interactions: DAGB, ATC L2, PCTL, clock-gating, light-sleep, and deep-sleep defaults must match firmware/platform expectations. Inconsistent programming can show up as resume failures, intermittent hangs, or lost register state.

## Test Signals

Useful validation signals for changes touching this header or its consumers include:

- Build coverage for AMDGPU with MMHUB v2.3 support enabled, catching missing or renamed macros in `mmhub_v2_3.c`.
- Boot or module-load testing on hardware using MMHUB IP 2.3.0, 2.4.0, or 2.4.1, with successful `gmc_v10_0` initialization and no MMHUB register access errors.
- GPU VM/GART workloads that exercise page-table setup, GART mappings, VRAM/system/AGP apertures, context switches, and TLB invalidation.
- VM fault tests that trigger `MMVM_L2_PROTECTION_FAULT_STATUS` reporting and confirm sane client IDs through `amdgpu_mmhub_client_name()`.
- Runtime toggles of fault-default policy through `mmhub_v2_3_set_fault_enable_default()` with expected dummy-page redirection or crash-on-fault behavior.
- Suspend/resume and runtime power-management tests with medium-grain clock gating and light sleep enabled (`AMD_CG_SUPPORT_MC_MGCG`, `AMD_CG_SUPPORT_MC_LS`).
- SR-IOV PF/VF testing that confirms VF framebuffer-location registers are initialized and PF-owned/inaccessible clock-gating paths are skipped in VF mode.
- Register readback checks around `gart_enable`, `gart_disable`, cache setup, VMID setup, and invalidation programming, comparing reset/default baselines with expected programmed values.

## Summary

`mmhub_2_3_0_default.h` is a generated register-default contract for AMD MMHUB 2.3.0. It contributes no runtime logic by itself, but it is important to MMHUB initialization because `mmhub_v2_3.c` uses selected defaults as trusted starting points for cache, VM, fault, invalidation, and power-management register programming. The main maintenance requirement is keeping the default, offset, and shift/mask headers synchronized with the ASIC register model and treating reset values as hardware baselines rather than universally safe runtime policy.
