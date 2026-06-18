# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_0_0_default.h

## Purpose

`mmhub_2_0_0_default.h` is a generated AMDGPU ASIC register-default header for MMHUB IP version 2.0.0. It contains reset/default values for MMHUB register blocks, expressed as C preprocessor constants named `mm..._DEFAULT`. The file is included by `drivers/gpu/drm/amd/amdgpu/mmhub_v2_0.c` together with the matching `mmhub_2_0_0_offset.h` and `mmhub_2_0_0_sh_mask.h` headers, giving the MMHUB v2.0 driver the register addresses, bit fields, and hardware default values needed to program memory-management hardware.

The header is not a standalone algorithm. Its value is the hardware contract it records: known-good baseline values for DAGB data/address gateway behavior, memory endpoint arbitration, MMHUB power-control save/restore ranges, L1/L2 translation buffers, MMVM context registers, invalidation engines, IOMMU/ATS virtualization registers, apertures, and performance counters.

## Important APIs, Types, and Constants

This file defines no C functions, structs, enums, or exported symbols. Its public interface is the set of `#define` constants protected by `_mmhub_2_0_0_DEFAULT_HEADER`.

Important constant families include:

- `mmDAGB0_*_DEFAULT`: defaults for the DAGB read/write clients, virtual-channel controls, burst and lazy timers, TLB/data/misc credits, pending-state registers, FIFO state, performance counters, and reserved registers. These establish the gateway baseline for MMHUB request routing.
- `mmMMEA0_*_DEFAULT`: defaults for MMHUB memory endpoint arbitration and address decoding. These include DRAM and IO client-to-group maps, priority aging/queuing/fixed/urgency values, address normalization, address decoder bank/hash/selection registers, SDP arbitration, EDC/DSM controls, clock control, and error status.
- `mmPCTL*_*_DEFAULT`: defaults for MMHUB power-control, deep sleep, power gating, register-engine RAM access, state-save ranges, exclusion sets, and PCTL performance counters.
- `mmMMMC_VM_MX_L1_*_DEFAULT`: L1 TLB status, performance counter, and control defaults.
- `mmMM_ATC_L2_*_DEFAULT`: ATC L2 control, cache data, status, clock gating, memory power, SDP port control, and performance counter defaults.
- `mmMMVM_L2_*_DEFAULT`: MMVM L2 cache, invalidate, protection-fault, dummy-page, identity-aperture, bank-selection, parity, interrupt-log, clock, and walker-throttle defaults.
- `mmMMVM_CONTEXT[0-15]_*_DEFAULT`: per-VMID context control and page-table base/start/end defaults. These are all-zero for page-table address ranges and `0x007ffe80` for context control defaults.
- `mmMMVM_INVALIDATE_ENG[0-17]_*_DEFAULT`: invalidation engine semaphore, request, acknowledgment, and address-range defaults. Request defaults are `0x02f80000`; semaphores, acknowledgments, and ranges reset to zero.
- `mmMMMC_VM_FB_SIZE_OFFSET_VF[0-31]_DEFAULT` and `mmMMVM_PCIE_ATS_CNTL_VF_[0-31]_DEFAULT`: virtualization/SR-IOV defaults for VF framebuffer sizing and ATS control.
- Shared aperture and platform registers such as `mmMMMC_VM_NB_*_DEFAULT`, `mmMMMC_VM_FB_LOCATION_*_DEFAULT`, `mmMMMC_VM_AGP_*_DEFAULT`, `mmMMMC_VM_SYSTEM_APERTURE_*_DEFAULT`, `mmMMMC_VM_LOCAL_HBM_ADDRESS_*_DEFAULT`, and `mmMMMC_SHARED_*_DEFAULT`.

The file has 856 `#define` entries grouped under generated `// addressBlock:` comments:

- `mmhub_dagbdec`
- `mmhub_mmea_mmeadec`
- `mmhub_pctldec`
- `mmhub_l1tlb_mmvml1pfdec`
- `mmhub_l1tlb_mmvml1pldec`
- `mmhub_l1tlb_mmvml1prdec`
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

## Control Flow

There is no runtime control flow in this header. Control flow appears in consumers that use these constants as register-programming seeds.

The primary consumer in this source tree is `drivers/gpu/drm/amd/amdgpu/mmhub_v2_0.c`. That driver includes this header after the matching offset and bit-mask headers. It then uses selected defaults while enabling and configuring the MMHUB/GART path:

- `mmhub_v2_0_gart_enable()` sequences GART aperture setup, system aperture setup, L1 TLB setup, L2 cache setup, system-domain enablement, identity-aperture disablement, VMID context setup, and invalidation-engine programming.
- `mmhub_v2_0_init_cache_regs()` reads or builds L2 cache control values. It explicitly seeds `MMVM_L2_CNTL3`, `MMVM_L2_CNTL4`, and `MMVM_L2_CNTL5` from `mmMMVM_L2_CNTL3_DEFAULT`, `mmMMVM_L2_CNTL4_DEFAULT`, and `mmMMVM_L2_CNTL5_DEFAULT`, then applies bit-field overrides with `REG_SET_FIELD()` before writing registers.
- `mmhub_v2_0_setup_vmid_config()` relies on the per-context register layout supplied by the sibling offset header and on the default bit-field contract from the default/shift-mask pair. It enables VM contexts 1-15, configures fault controls, and programs page-table bounds.
- `mmhub_v2_0_program_invalidation()` programs all 18 invalidation engines, matching the `MMVM_INVALIDATE_ENG0` through `ENG17` default family in this header.
- `mmhub_v2_0_set_fault_enable_default()` toggles MMVM L2 protection fault default handling. The reset defaults in this header describe the initial value, while runtime policy is applied by field writes.
- `mmhub_v2_0_set_clockgating()` and `mmhub_v2_0_get_clockgating()` manipulate MMHUB clock-gating-related registers that have defaults here, notably ATC L2 and DAGB controls.

The header therefore participates in control flow as compile-time data: the consumer chooses a register, starts from a default where needed, patches hardware-specific fields, and writes the final value through SOC15 register accessors.

## State and Persistence Behavior

The constants describe hardware reset state, not software-owned persistent state. They are immutable at compile time and do not store runtime state in memory.

Runtime MMHUB state lives in GPU registers and in AMGPU device structures such as `adev->vmhub[AMDGPU_MMHUB0(0)]`, `adev->gmc`, and `adev->vm_manager`. The driver writes register state during GPU initialization, GART enable/disable, fault-policy updates, invalidation programming, and clock-gating transitions.

Persistence boundaries are hardware-driven:

- Power management and reset can return registers to these default values or require reprogramming from driver policy.
- PCTL state-save defaults, including `PCTL*_STCTRL_REGISTER_SAVE_RANGE*` and exclusion-set constants, describe which MMHUB register ranges are candidates for hardware save/restore behavior.
- SR-IOV virtual functions cannot access some MMHUB registers; `mmhub_v2_0.c` skips those writes for VFs and expects the physical function to program them. The VF-related defaults in this header document reset state for per-VF aperture and ATS controls, but policy still belongs to PF/VF orchestration.

## Dependencies

Direct dependencies are minimal because this is a pure preprocessor header:

- A C compiler/preprocessor.
- The include guard `_mmhub_2_0_0_DEFAULT_HEADER`.
- Consumers that know the `mm...` register naming convention.

Functional use depends on sibling generated headers:

- `mmhub_2_0_0_offset.h` supplies register offsets such as `mmMMVM_L2_CNTL3` and `mmMMVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32`.
- `mmhub_2_0_0_sh_mask.h` supplies field masks and shifts used by `REG_SET_FIELD()` and `REG_GET_FIELD()`.

Runtime integration depends on AMDGPU/SOC15 infrastructure:

- SOC15 register access macros such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_RLC`, and offset variants.
- AMDGPU VM/GMC data structures (`amdgpu_device`, `amdgpu_vmhub`, `adev->gmc`, `adev->vm_manager`).
- MMHUB function tables such as `amdgpu_mmhub_funcs` and `amdgpu_vmhub_funcs`.
- IP-version dispatch via `amdgpu_ip_version(adev, MMHUB_HWIP, 0)`.

## Integration Points

The principal integration point is MMHUB v2.0 support for Navi-generation AMD GPUs in `amdgpu/mmhub_v2_0.c`. The implementation registers `mmhub_v2_0_funcs`, whose methods initialize the VM hub, enable/disable GART, set fault-default policy, program page tables, and manage clock gating.

The default header is paired with generated offset and shift/mask headers for a specific hardware register model. Using a default from this file with a mismatched offset or mask header would silently produce bad hardware programming, because the macro names may still compile while bit meanings or register availability differ.

The file is also structurally aligned with other MMHUB default headers such as `mmhub_1_0_default.h`, `mmhub_2_3_0_default.h`, and `mmhub_9_4_1_default.h`. Those alternatives represent different IP versions and should be selected by the corresponding driver implementation, not mixed manually.

## Risks and Edge Cases

- Hardware-generation mismatch: these defaults are for MMHUB 2.0.0. Reusing them for a different MMHUB revision risks incorrect cache, VM, aperture, or power behavior.
- Silent compile-time misuse: macros are untyped numeric constants. The compiler cannot enforce that a default belongs to the same register as the offset being written.
- Reserved registers: `mmDAGB0_RESERVE*` defaults are `0xffffffff`. Treating these as safe writable values without hardware guidance could corrupt reserved state.
- Reset-default assumptions: a register default is not always the desired runtime policy. The driver deliberately overrides fields for cache enablement, fault handling, translation depth, page-table ranges, clock gating, and invalidation behavior.
- SR-IOV access constraints: several MMHUB registers are inaccessible from virtual functions. Code paths that blindly apply defaults from this header in VF mode can trigger access faults or ineffective writes.
- Fault-handling sensitivity: defaults around `MMVM_L2_PROTECTION_FAULT_*`, `MMVM_CONTEXT*_CNTL`, and dummy-page registers affect whether faults are redirected, retried, interrupted, or fatal. Incorrect defaults or overrides can cause VM fault storms, hidden data corruption, or GPU hangs.
- Address split fields: page-table, aperture, MARC, and default-address registers split addresses across low/high 32-bit register pairs with hardware-specific shifts. Using the default zero values as real configured values can unintentionally point contexts at address zero.
- Power management interactions: clock gating, light sleep, deep sleep, and PCTL save/restore defaults need to match firmware and platform expectations. Inconsistent programming may create resume failures or intermittent MMHUB hangs.

## Test Signals

Useful validation signals for changes touching this header or its consumers include:

- Build coverage for AMDGPU with MMHUB v2.0 support enabled. Because this is a macro header, many mistakes surface as compile failures in `mmhub_v2_0.c` or other register consumers.
- Boot or module-load logs on Navi/MMHUB 2.0 hardware with no MMHUB VM fault spam, no register access errors, and successful GART enablement.
- GPU VM workloads that exercise page-table setup, TLB invalidation, GART mappings, VRAM/AGP/system aperture access, and context switches.
- Fault-injection or negative tests that trigger MMVM L2 protection faults and confirm that `mmhub_v2_0_print_l2_protection_fault_status()` reports sane client IDs and fault fields.
- Suspend/resume, runtime power management, and clock-gating tests with `AMD_CG_SUPPORT_MC_MGCG` and `AMD_CG_SUPPORT_MC_LS` enabled.
- SR-IOV PF/VF testing that confirms VF paths skip inaccessible register programming while PF-side MMHUB setup remains correct.
- Register readback checks comparing expected reset/default values before driver override and expected programmed values after `gart_enable`, cache setup, VMID setup, and invalidation setup.

## Summary

`mmhub_2_0_0_default.h` is a generated register-default contract for AMD MMHUB 2.0.0. It contributes no runtime logic directly, but it is important to MMHUB initialization because consumers use selected constants as trusted starting points for hardware register programming. The key maintenance concern is keeping it synchronized with the matching ASIC register model and ensuring consumers treat defaults as hardware baselines, not universally safe runtime policy.
