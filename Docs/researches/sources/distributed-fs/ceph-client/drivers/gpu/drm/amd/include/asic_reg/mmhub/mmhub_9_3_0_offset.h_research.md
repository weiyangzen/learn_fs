# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_3_0_offset.h

## Purpose

`mmhub_9_3_0_offset.h` is a generated-style AMDGPU ASIC register offset header for the MMHUB 9.3.0 register map. It provides symbolic C preprocessor constants for the memory hub's MMIO registers: DAGB request decode, memory arbitration and address decode, power/control state, L1 and L2 translation lookaside buffers, VM context programming, invalidation engines, aperture/shared-memory registers, IOMMU/ATS/virtualization controls, and performance counters.

The file is data-only. It contains AMD license text, an include guard, address-block comments, 951 register-offset macros, and 951 paired `*_BASE_IDX` macros. It defines no structs, enums, functions, inline helpers, runtime branches, storage, or executable code. Its operational value is that runtime AMDGPU code can pass names such as `mmVM_CONTEXT0_CNTL`, `mmVM_INVALIDATE_ENG0_REQ`, or `mmMC_VM_FB_LOCATION_BASE` to register-access helpers without hard-coding raw offsets.

## Exported API Surface

The exported API is the macro namespace. This revision has 1,903 `#define` lines: one include-guard macro, 951 register-offset macros, and 951 base-index macros. Every register macro has a matching `*_BASE_IDX` macro, and all base-index values in this file are `0`.

Important macro families include:

- `mmDAGB0_*`, `mmDAGB1_*`, `mmDAGB2_*`, and `mmDAGB3_*`: read/write client slots, read/write controls, GMI/address/data/output controls, clock-gating controls, virtual-channel controls, TLB/data/misc credits, pending-status registers, FIFO/full indicators, DAGB delay/misc controls, reserve slots, and DAGB performance counters. Each DAGB instance follows the same layout, offset by `0x80`.
- `mmMMEA0_*` and `mmMMEA1_*`: DRAM and IO client-to-group maps, group-to-VC maps, lazy timers, CAM/page-burst controls, priority age/queue/fixed/urgency/quantum registers, address normalization ranges, DRAM hole/trichannel/bank/hash/harvest controls, chip-select base/mask/config/select registers, SDP arbitration/priority/credits, latency sampling, error/status/EDC/DSM controls, clock-gating, and MMEA performance counters.
- `mmPCTL_*` and `mmPCTL0_*` through `mmPCTL2_*`: MMHUB deepsleep and override controls, power-gating ignore/DAGB controls, RENG RAM access/execute registers, PCTL misc registers, and state-controller register save range/exclusion registers.
- `mmMC_VM_MX_L1_TLB*_STATUS` and `mmMC_VM_MX_L1_PERFCOUNTER*`: L1 TLB status and L1 TLB performance-counter configuration/result registers.
- `mmATC_L2_*`: ATC L2 control/status/cache-data, clock-gating, memory light sleep, and ATC L2 performance-counter result/configuration registers.
- `mmVM_L2_*`: VM L2 controls/status, dummy-page and protection-fault control/address/default-address registers, context-1 identity aperture registers, identity physical offset, bank selection, parity, and clock-gating.
- `mmVM_CONTEXT*_*`: controls and page-table base/start/end address pairs for VM contexts 0 through 15.
- `mmVM_INVALIDATE_ENG*_*`: semaphore, request, acknowledgement, and address-range registers for invalidate engines 0 through 17.
- `mmMC_VM_*`, `mmMC_SHARED_*`, `mmVM_PCIE_ATS_CNTL*`, and `mmVM_IOMMU_*`: per-PF and per-VF PTE cache fragment sizes, framebuffer size offsets for VFs, MARC base/relocation/length ranges, IOMMU controls, PCIe ATS controls, active function ID, XGMI GPUIOV, NB PCI/MMIO/top-of-DRAM registers, framebuffer offset/location, system aperture defaults, AGP/system aperture ranges, cacheable DRAM, local HBM ranges, local-HBM lock control, and XGMI local-framebuffer controls.

## Address Blocks

The hardware-generator comments split the file into these address blocks:

| Address block | Base address | Starts at line | Role |
| --- | ---: | ---: | --- |
| `mmhub_dagbdec` | `0x68000` | 26 | Four DAGB instances for client read/write routing, credits, pending/FIFO status, VC controls, misc delay/control, reserves, and DAGB perf counters |
| `mmhub_ea_mmeadec` | `0x68400` | 542 | MMEA DRAM/IO arbitration, address normalization/decoding/hash/harvest, chip-select mapping, SDP controls, EDC/DSM, errors, and MMEA perf counters |
| `mmhub_pctldec` | `0x68e00` | 1130 | MMHUB deepsleep/power-gating controls, RENG RAM interface, and PCTL register-save ranges/exclusions |
| `mmhub_l1tlb_vml1dec` | `0x69600` | 1210 | L1 TLB status registers |
| `mmhub_l1tlb_vml1pldec` | `0x69650` | 1230 | L1 TLB performance-counter configuration registers |
| `mmhub_l1tlb_vml1prdec` | `0x69670` | 1244 | L1 TLB performance-counter result registers |
| `mmhub_utcl2_atcl2dec` | `0x69900` | 1252 | ATC L2 control, cache data, status, clock-gating, and memory-light-sleep registers |
| `mmhub_utcl2_vml2pfdec` | `0x69a00` | 1278 | VM L2 controls/status, fault handling, identity aperture, bank selection, parity, and clock-gating |
| `mmhub_utcl2_vml2vcdec` | `0x69b00` | 1338 | VM contexts, invalidate engines, invalidate ranges, context page-table ranges, per-PF/VF PTE fragment sizes, VF framebuffer size offsets, IOMMU, MARC, ATS, and XGMI/active-function controls |
| `mmhub_utcl2_vml2pldec` | `0x69e90` | 1748 | VM L2 performance-counter configuration |
| `mmhub_utcl2_vml2prdec` | `0x69ee0` | 1770 | VM L2 performance-counter result registers |
| `mmhub_utcl2_vmsharedhvdec` | `0x69f30` | 1778 | Hypervisor/shared VM aperture and virtualization registers |
| `mmhub_utcl2_vmsharedpfdec` | `0x6a040` | 1908 | PF/shared NB MMIO/PCI/top-of-DRAM, framebuffer offset, aperture defaults, steering/reset, memory power, cacheable DRAM, local HBM, and XGMI LFB controls |
| `mmhub_utcl2_vmsharedvcdec` | `0x6a0b0` | 1954 | Framebuffer location, AGP range, system aperture bounds, and L1 TLB control |
| `mmhub_utcl2_atcl2pfcntrdec` | `0x6a100` | 1974 | ATC L2 performance-counter result registers |
| `mmhub_utcl2_atcl2pfcntldec` | `0x6a120` | 1982 | ATC L2 performance-counter configuration and result-control registers |

The macro values are register indices consumed by AMD SOC/register helper code, not byte offsets intended for direct pointer arithmetic.

## Control Flow

There is no runtime control flow in this header. The effective flow is compile-time substitution:

1. A generation-specific AMDGPU source includes this header and, when fields are needed, the matching `mmhub_9_3_0_sh_mask.h`.
2. Driver code passes symbolic register names and their `*_BASE_IDX` partners into AMDGPU/SOC register access helpers.
3. The helper layer combines the IP block, instance, base index, and offset into a concrete MMIO address.
4. Runtime code then sequences hardware initialization, VM context setup, TLB/cache invalidation, fault handling, aperture programming, clock-gating, virtualization, and performance-counter access.

The sequencing is intentionally outside this file. For example, adjacent macros such as `mmVM_CONTEXT0_CNTL` through `mmVM_CONTEXT15_CNTL`, `mmVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32` through high/start/end pairs, and `mmVM_INVALIDATE_ENG0_*` through `mmVM_INVALIDATE_ENG17_*` are designed so consumers can compute register strides and loop over hardware contexts or invalidate engines.

## State and Persistence Behavior

The header owns no software state and persists nothing. It names hardware registers whose contents persist according to MMHUB reset, power, virtualization, and driver-programming rules:

- VM state includes context enablement, page-table base/start/end ranges, identity aperture bounds, physical offsets, per-PF/VF PTE cache fragment sizing, and context-disable state.
- TLB/cache invalidation state is represented by per-engine semaphore, request, acknowledgement, low-address, and high-address registers for 18 invalidation engines.
- Fault state includes dummy-page fault controls/addresses, L2 protection-fault control/status/address/default-address registers, and L1 TLB status registers.
- Aperture and memory-routing state includes framebuffer location/top/offset, AGP top/bottom/base, system aperture low/high/default addresses, NB top-of-DRAM and PCI/MMIO windows, cacheable DRAM bounds, local HBM address ranges, MARC ranges, and XGMI local-framebuffer controls.
- Power and clock state includes MMHUB deepsleep, power-gating overrides, PCTL register-save ranges, DAGB/ATC/L1/L2 clock-gating controls, memory light sleep, DSM, and EDC-related controls.
- Virtualization/isolation state includes IOMMU control registers, PCIe ATS controls for PF and VFs, active function ID, shared virtual reset request, local-HBM lock control, XGMI GPUIOV, and VF framebuffer size offsets.
- Diagnostic state includes DAGB, MMEA, L1, VM L2, and ATC L2 performance-counter configuration and result registers, plus status/error/credit/FIFO indicators.

Because all behavior is indirect, persistence bugs usually come from consumers using the wrong offset, wrong generation header, wrong base index, or wrong write/read ordering for split low/high registers.

## Dependencies

Direct dependencies are minimal:

- The include guard `_mmhub_9_3_0_OFFSET_HEADER` prevents duplicate macro definitions.
- The file is normally paired conceptually with `mmhub_9_3_0_sh_mask.h`, which defines field shifts and masks for the same registers.
- Consumers depend on AMDGPU register-access infrastructure to interpret the offset and base-index macros; this file does not include that infrastructure itself.
- It uses no Linux kernel types, no C library APIs, no inline helpers, and no generated C tables.

The header follows the same generated ASIC-register pattern as neighboring `mmhub_*_offset.h` files, but this source snapshot does not show a C file directly including `mmhub_9_3_0_offset.h`.

## Integration Points

The file lives under `drivers/gpu/drm/amd/include/asic_reg/mmhub/`, which marks it as an AMD ASIC register contract shared by MMHUB-capable driver code. Search results in this repository show only the header itself and the matching `mmhub_9_3_0_sh_mask.h` referencing the `mmhub_9_3_0` version string; no visible `.c` consumer directly includes this header in the current snapshot.

Expected integration is still clear from the macro names and adjacent MMHUB generations:

- MMHUB runtime code would use `mmVM_L2_*`, `mmVM_CONTEXT*_*`, `mmVM_INVALIDATE_ENG*_*`, and `mmMC_VM_*` macros during GART setup, VMID/context programming, aperture programming, invalidate request/ack handling, and protection-fault logging.
- Power-management paths would use `mmPCTL_*`, DAGB/ATC/L1/L2 `*_CGTT_CLK_CTRL`, memory-light-sleep, register-save range, DSM, and EDC controls.
- Virtualization or SR-IOV paths would use `mmVM_PCIE_ATS_CNTL*`, `mmVM_IOMMU_*`, `mmMC_SHARED_ACTIVE_FCN_ID`, `mmMC_SHARED_VIRT_RESET_REQ`, `mmMC_VM_XGMI_GPUIOV_ENABLE`, VF PTE fragment-size macros, and VF framebuffer size-offset macros.
- Diagnostics and performance tooling would use DAGB/MMEA/L1/VM L2/ATC L2 performance-counter config/result registers and status/credit/fault macros.

## Risks and Edge Cases

- Register-map drift: MMHUB 9.3.0 has its own offsets and block names. Reusing offsets from MMHUB 1.x, 2.x, 3.x, or GC VM headers can silently target the wrong hardware registers.
- Base-index assumptions: all `*_BASE_IDX` values are `0` here. Consumers should still use the paired macro instead of assuming every generation or IP block uses the same base index.
- Macro-name contract: AMDGPU register helpers and tables often rely on exact generated macro names. Renames break builds; mistaken compatibility aliases can compile while accessing the wrong MMIO location.
- Stride assumptions: repeated sequences for four DAGBs, two MMEAs, 16 VM contexts, 18 invalidate engines, PF/VF fragment sizes, and VF ATS/framebuffer offsets invite looped consumers. If a future regenerated layout stops being contiguous, stride-derived register addressing can fail.
- Split 64-bit state: page-table base/start/end, fault addresses, dummy/default addresses, MARC ranges, aperture bounds, and some framebuffer/system ranges are split into low/high halves. This header cannot enforce write order, masking, or atomicity requirements.
- Security-sensitive registers: IOMMU, ATS, active function ID, virtual reset, GPUIOV, local-HBM lock, VF fragment sizing, and framebuffer/VF offset registers influence isolation boundaries.
- Power-transition sensitivity: PCTL save ranges/exclusions, deepsleep, power gating, clock gating, memory light sleep, DSM, and EDC controls may affect suspend/resume or runtime power management if used against the wrong offset.
- Reserved-looking registers: `RESERVE*`, credit-safety, status, and diagnostic registers should not be treated as scratch registers; generated names can still map to hardware with side effects.

## Test Signals

Useful validation signals for this header are mostly compile-time, register-map, and hardware/runtime checks:

- Build any AMDGPU target that selects MMHUB 9.3.0 or includes this header; missing generated macros should fail at compile time.
- Compare the 951 register-offset macros and 951 `*_BASE_IDX` macros against the authoritative AMD register database when regenerating headers.
- Confirm every `mm...` register macro has a paired `mm..._BASE_IDX` macro and that all base-index values remain expected for this IP revision.
- On hardware using this MMHUB map, verify VM hub initialization, GART page-table programming, context 0 through 15 setup, and page-table base/start/end address programming.
- Exercise TLB/cache invalidation and check request/ack/semaphore progress for invalidate engines 0 through 17.
- Trigger controlled VM protection faults and confirm status/address/default-address registers report coherent information.
- Run suspend/resume and runtime power-management tests to cover PCTL, clock-gating, memory-light-sleep, and register-save-range offsets.
- Exercise SR-IOV or virtualization flows where supported, especially ATS, IOMMU, active-function, VF PTE fragment sizing, virtual reset, and XGMI GPUIOV registers.
- Validate performance-counter programming for DAGB, MMEA, L1 TLB, VM L2, and ATC L2 counters.

## Research Notes

The source file was read completely across all 1,991 lines. It is a generated-style register-offset header, so the substantive behavior is captured through its macro families, address-block layout, hardware state contracts, likely AMDGPU integration points, and risks around consumers interpreting the offsets incorrectly.
