# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_0_0_offset.h

## Purpose

`mmhub_2_0_0_offset.h` is an AMDGPU/DC ASIC register offset header for the MMHUB 2.0.0 block. It contributes the compile-time register address map for memory hub, VM, ATC, TLB, power-control, performance-counter, and virtualization-related MMHUB registers. Driver code includes this file together with `mmhub_2_0_0_sh_mask.h` so register helper macros can combine an offset macro such as `mmMMVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32` with matching field shift/mask macros.

The file is data-only C preprocessor surface. It has an include guard, AMD's MIT-style license text, address-block comments, and `#define` pairs. There are no functions, structs, enums, executable branches, or local storage. Its correctness is still critical because these constants address MMIO hardware state.

## Exported API Surface

The exported API is the set of `mm*` register offset macros and their corresponding `*_BASE_IDX` macros. The header defines 1,711 macros total: 855 register offset macros, 855 matching base-index macros, and the include guard symbol. All `*_BASE_IDX` values in this revision are `0`, meaning consumers expect these MMHUB 2.0.0 registers to be addressed through base segment 0 when constructing absolute SOC15/DC register addresses.

Important register families:

- `mmDAGB0_*`: data/address gateway block registers for read/write clients, virtual channels, credits, pending status, FIFO status, GPU snoop override, clock-gating controls, delays, reserves, and DAGB performance counters.
- `mmMMEA0_*`: memory-mapping/address engine registers for DRAM and IO client-to-group maps, group-to-VC maps, lazy timers, CAM/page burst and priority controls, address normalization, DRAM hole handling, bank/hash/channel configuration, harvested address ranges, chip-select address decode tables, SDP arbitration/priority/credits, EDC/DSM status and controls, and MMEA perf counters.
- `mmPCTL*`: MMHUB power/deepsleep and state-control registers, including register-save ranges for PCTL0, PCTL1, and PCTL2, RENG RAM access, and PCTL performance counters.
- `mmMMMC_VM_MX_L1_*`: L1 TLB status and performance-counter registers.
- `mmMM_ATC_L2_*`: ATC L2 control, status, cache data, power/clock gating, SDP port, and ATC L2 perf-counter registers.
- `mmMMVM_L2_*` and `mmMMVML2_*`: VM L2 control/status, dummy page fault, invalidation, protection fault, identity aperture, cache parity, interrupt-handler logging, GCR, and page-walker throttle registers.
- `mmMMVM_CONTEXT*_*`: VM context control and 64-bit page-table base/start/end ranges for contexts 0 through 15.
- `mmMMVM_INVALIDATE_ENG*_*`: invalidation engine semaphore, request, acknowledgement, and address-range registers for engines 0 through 17.
- `mmMMMC_VM_L2_PERFCOUNTER*` and `mmMMMC_VM_L2_PERFCOUNTER_*`: VM L2 performance counter configuration and result registers.
- `mmMMMC_VM_FB_SIZE_OFFSET_VF*`, `mmMMVM_PCIE_ATS_CNTL_VF_*`, and related `mmMMMC_SHARED_*` / `mmMMVM_IOMMU_*`: SR-IOV or virtualization-facing frame-buffer offset, ATS, IOMMU, active-function, and reset controls.
- `mmMMMC_VM_*`: shared VM aperture and memory mapping registers for MMIO base/limit, PCI control, top-of-DRAM, FB offset, system aperture default, cacheable DRAM range, local HBM range, FB location, AGP range, and MX L1 TLB control.

## Address Blocks

The header preserves the hardware generator's address-block structure:

| Address block | Base address | Line range | Role |
| --- | ---: | ---: | --- |
| `mmhub_dagbdec` | `0x68000` | 26-541 | DAGB read/write clients, credits, FIFO/pending status, virtual channels, snoop override, and perf counters |
| `mmhub_mmea_mmeadec` | `0x68400` | 542-847 | MMEA DRAM/IO arbitration, address normalization/decode, SDP, EDC/DSM, and perf counters |
| `mmhub_pctldec` | `0x68e00` | 848-937 | MMHUB power/deepsleep, register-save, RENG, PCTL misc, and perf counters |
| `mmhub_l1tlb_mmvml1pfdec` | `0x69600` | 938-957 | L1 TLB status registers |
| `mmhub_l1tlb_mmvml1pldec` | `0x69650` | 958-971 | L1 TLB performance-counter configuration |
| `mmhub_l1tlb_mmvml1prdec` | `0x69670` | 972-979 | L1 TLB performance-counter results |
| `mmhub_mmutcl2_mmatcl2dec` | `0x69900` | 980-1007 | ATC L2 controls/status/cache/power/clock |
| `mmhub_mmutcl2_mmvml2pfdec` | `0x69a00` | 1008-1085 | VM L2 control, faults, invalidation, identity aperture, logging, cache parity, and throttling |
| `mmhub_mmutcl2_mmvml2vcdec` | `0x69b00` | 1086-1495 | VM contexts, invalidate engines, and context page-table ranges |
| `mmhub_mmutcl2_mmvml2pldec` | `0x69e90` | 1496-1517 | VM L2 performance-counter configuration |
| `mmhub_mmutcl2_mmvml2prdec` | `0x69ee0` | 1518-1525 | VM L2 performance-counter results |
| `mmhub_mmutcl2_mmvmsharedhvdec` | `0x69f30` | 1526-1717 | VF FB offsets, MARC ranges, IOMMU/ATS controls, per-VF ATS, MMUTCL2 clock, and active function ID |
| `mmhub_mmutcl2_mmvmsharedpfdec` | `0x6a140` | 1718-1761 | PF/shared MMIO, PCI, top-of-DRAM, aperture default, steering, reset, memory power, cacheable DRAM, APT, and local HBM controls |
| `mmhub_mmutcl2_mmvmsharedvcdec` | `0x6a1b0` | 1762-1781 | FB location, AGP range, system aperture, and MX L1 TLB control |
| `mmhub_mmutcl2_mmatcl2pfcntrdec` | `0x6a200` | 1782-1789 | ATC L2 performance-counter results |
| `mmhub_mmutcl2_mmatcl2pfcntldec` | `0x6a220` | 1790-1798 | ATC L2 performance-counter configuration |

The offset macro values are register indices relative to the ASIC register base scheme used by AMD's SOC15/display register helpers, not byte offsets to be directly dereferenced by ordinary C code.

## Control Flow

There is no runtime control flow in this file. The effective flow is preprocessor expansion:

1. A DC or AMDGPU source file includes this offset header and the matching shift/mask header.
2. Resource or block-specific macros such as `SR`, `SRI`, `SRI2`, `REG`, `REG_SET`, `REG_UPDATE`, and `REG_READ` paste a register name into `mm<register>` and `mm<register>_BASE_IDX`.
3. Static register tables or direct MMIO helper calls receive the numeric offset and base index.
4. Runtime driver code reads or writes the underlying MMHUB register through the shared MMIO accessor layer.

The header itself never sequences register programming. Sequencing is supplied by consumers such as DCN resource, VMID, hubp, hubbub/mmhubbub, and clock-manager code.

## State and Persistence Behavior

This header does not allocate memory or persist software state. It describes persistent and volatile hardware state exposed by MMHUB registers:

- VM context state, including page-table bases and logical address ranges, persists in hardware registers until reset or reprogrammed.
- Invalidation engine request/ack/semaphore registers represent transient synchronization state for TLB/cache invalidation.
- Protection fault and dummy fault registers expose fault status/address state that driver code can log or clear according to hardware rules.
- Aperture, FB, AGP, top-of-DRAM, local-HBM, and cacheable-DRAM registers define memory routing state used by display and GPU memory transactions.
- Power, deepsleep, clock-gating, register-save, and memory-power registers affect low-power behavior across runtime power-management transitions.
- Performance-counter configuration/result registers are diagnostic state and may be used by profiling, debug, or validation flows.
- Virtualization registers, including per-VF FB offsets and PCIe ATS controls, affect PF/VF isolation and I/O translation behavior.

Because the file is compile-time data, persistence risks come from consumers writing the wrong physical register if a macro value or base index is wrong.

## Dependencies

Direct dependencies are minimal:

- The include guard `_mmhub_2_0_0_OFFSET_HEADER` prevents duplicate macro definitions.
- Consumers normally include `mmhub/mmhub_2_0_0_sh_mask.h` for field-level shifts and masks.
- Display/resource consumers also include IP base-offset headers such as `navi10_ip_offset.h` or `sienna_cichlid_ip_offset.h` and common register helpers like `reg_helper.h`.
- AMDGPU core consumers rely on SOC15 register-access macros to combine base indices, per-IP base addresses, and register offsets.

The header has no dependency on Linux kernel types, AMDGPU structs, compiler extensions, or generated tables at runtime.

## Integration Points

Observed direct include sites include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`
- `drivers/gpu/drm/amd/display/dc/resource/dcn201/dcn201_resource.c`
- `drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`
- `drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`

These files include the header beside DCN, DPCS, NBIO, and MMHUB shift/mask headers. The pattern lets register-list macros initialize per-generation register tables with entries such as:

- `BASE(mm ## reg_name ## _BASE_IDX) + mm ## reg_name` in display clock/resource code.
- `REG_SET`, `REG_UPDATE`, `REG_GET`, and similar helpers in VMID, hubp, hubbub/mmhubbub, and clock code.

The broader integration is the AMD display core and AMDGPU register access layer. The source file's path under `include/asic_reg/mmhub/` indicates it is an ASIC-family hardware contract, not a hand-authored algorithmic module.

## Risks and Edge Cases

- Register offset drift: MMHUB 2.0.0 differs from neighboring generations. Copying offsets from `mmhub_1_0_offset.h`, `mmhub_9_4_1_offset.h`, or another ASIC generation can silently program the wrong hardware register.
- Base-index mismatch: all base indices are `0` here. If future generated data needs another base segment, consumers that assume base index 0 rather than using `*_BASE_IDX` would break.
- Macro-name contract: many consumers construct names through token pasting. Renaming a macro without updating register-list macros and shift/mask fields causes compile failures; worse, adding a similarly named wrong macro can make an incorrect register compile.
- 64-bit register pairs: page-table, aperture, fault-address, MARC, AGP, and FB range registers often have low/high halves. Consumers must preserve hardware-required write order and width semantics; this header only supplies offsets.
- Context/engine cardinality assumptions: the header exposes 16 VM contexts and 18 invalidate engines. Consumers with hard-coded loop bounds must match this generation.
- Virtualization isolation: per-VF FB offset and ATS control registers are security-sensitive. Wrong offsets or field masks could affect PF/VF memory isolation or address translation.
- Power-management sensitivity: deepsleep, clock-gating, memory-power, and register-save ranges can affect resume/display stability if accessed with wrong offsets or in wrong sequences.
- Generated reserved ranges: `mmDAGB0_RESERVE*` macros occupy many offsets. Treating reserved registers as safe scratch registers would be unsafe.

## Test Signals

Useful validation signals for this header are mostly build-time, hardware bring-up, and register-access behavior:

- Compile display and AMDGPU code for ASICs that include MMHUB 2.0.0; token-pasted register table macros should resolve every required `mm*` and `*_BASE_IDX` symbol.
- Include-order builds should catch accidental macro collisions with other ASIC register headers.
- Boot or smoke-test supported DCN 2.x/3.0 hardware that selects this header; failures can appear as display initialization issues, page faults, VMID setup failures, clock-manager register access faults, or power-management resume problems.
- Exercise VMID programming and memory aperture setup paths that write page-table base/start/end, FB/AGP/system aperture, and default aperture registers.
- Exercise TLB invalidation paths and confirm invalidate request/ack registers make progress without timeouts.
- Check GPU/display page fault logging and protection fault status reporting after controlled fault injection if the platform supports it.
- Run suspend/resume and display modeset tests to cover PCTL, deepsleep, register-save, and memory-power registers.
- Compare generated offsets against the authoritative AMD register database for MMHUB 2.0.0 when regenerating the header.

## Research Notes

The source was read completely across its full 1,799 lines. It is a generated-style register-offset header with no executable logic. Substantive behavior is therefore captured through its macro families, address-block organization, integration into AMD register helper code, and the hardware state those offsets allow consumers to access.
