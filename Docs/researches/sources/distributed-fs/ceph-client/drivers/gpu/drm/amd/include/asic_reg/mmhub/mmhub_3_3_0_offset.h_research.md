# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_3_0_offset.h

## Purpose

`mmhub_3_3_0_offset.h` is a generated-style AMDGPU ASIC register offset header for the MMHUB 3.3.0 register map. It exports compile-time constants for memory-hub, VM, ATC, TLB, power-control, invalidation, fault-reporting, aperture, and performance-counter registers used by the AMDGPU memory-management hub and display core resource code.

The file is C preprocessor data only. It contains AMD license text, an include guard, address-block comments, register offset `#define`s, and matching `*_BASE_IDX` macros. It defines no functions, structs, enums, executable logic, heap state, or static storage. Its importance is that all consumers use these symbolic offsets to access MMIO hardware state; an incorrect value can make otherwise valid driver code read or write the wrong MMHUB register.

## Exported API Surface

The exported surface is the set of `reg*` offset macros and their paired `reg*_BASE_IDX` macros. This revision has 1,281 `#define` lines: one include-guard macro plus 640 register-offset macros and 640 base-index macros. Every `*_BASE_IDX` value is `1`, so consumers must preserve the base-index macro instead of assuming the base segment used by other MMHUB generations.

Important macro families include:

- `regDAGB0_*`: read/write client slots, read/write controls, IO/GMI controls, virtual-channel controls, TLB/data/misc credits, pending-status registers, snoop and no-allocate overrides, FIFO status, DAGB delay/misc controls, SDP arbitration/priority/credits, and DAGB performance counters.
- `regPCTL_*`: MMHUB deepsleep, power-gating/deepsleep override, slice busy/deepsleep allow, RENG control/RAM access, state-controller register-save ranges and exclusions, status, and PCTL performance counters.
- `regMMMC_VM_MX_L1_*`: L1 TLB status and performance-counter configuration/result registers.
- `regMMVM_L2_SAW_*`: standalone-walker control, context-0 page-table base/start/end, context disable, pipe-busy, and SAW protection-fault status/address registers.
- `regMM_ATC_L2_*`: ATC L2 control/status/cache-data, clock-gating, memory-power, SDP-port, IOV-mode, and ATC L2 performance-counter registers.
- `regMMVM_L2_*` and `regMMVML2_*`: VM L2 cache/control/status, dummy-page and protection-fault controls/addresses, invalidation, identity aperture, bank selection, GCR, busy controls, PTE cache dump, per-PF/VF PTE fragment sizing, and credit-safety registers.
- `regMMVM_CONTEXT*_*`: VM context controls and 64-bit page-table base/start/end address pairs for contexts 0 through 15.
- `regMMVM_INVALIDATE_ENG*_*`: invalidation engine semaphore, request, acknowledgement, and address-range registers for engines 0 through 17.
- `regMMMC_VM_*`, `regMMMC_SHARED_*`, `regMMVM_PCIE_ATS_CNTL`, and `regMMVM_IOMMU_*`: memory aperture, AGP, framebuffer location/offset, system aperture default, local framebuffer/system memory ranges, active function ID, virtualization reset, ATS, IOMMU, and host translation controls.
- `regMMUTC_*` and `regMML2TLB_*`: translation-fault controls, GPUVA/VMID translation-assist controls and request/response registers, L2 TLB status/TMZ, and L2 TLB performance counters.

## Address Blocks

The hardware-generator comments split the register map into these address blocks:

| Address block | Base address | Line range | Role |
| --- | ---: | ---: | --- |
| `mmhub_dagbdec` | `0x68000` | 28-408 | DAGB read/write clients, credits, pending/FIFO status, virtual channels, SDP controls, and DAGB performance counters |
| `mmhub_pctldec` | `0x68e00` | 412-528 | MMHUB deepsleep, PCTL slices, RENG, state-save ranges, status, and PCTL perf counters |
| `mmhub_l1tlb_mmutcl1pfdec` | `0x69600` | 532-548 | L1 TLB status registers |
| `mmhub_l1tlb_mmutcl1pldec` | `0x69670` | 552-562 | L1 TLB performance-counter configuration |
| `mmhub_l1tlb_mmutcl1prdec` | `0x69690` | 566-570 | L1 TLB performance-counter result registers |
| `mmhub_l1tlb_mmvmtlspfdec` | `0x696c0` | 574-614 | SAW/TLS fault, standalone-walker control, context-0 page-table, context-disable, and pipe-busy registers |
| `mmhub_mmutcl2_mmatcl2dec` | `0x69f00` | 618-648 | ATC L2 controls, cache data, status, clock-gating, memory power, and SDP-port control |
| `mmhub_mmutcl2_mmvml2pfdec` | `0x6a000` | 652-732 | VM L2 control/status, faults, invalidation, identity aperture, cache parity, GCR, PTE dump, and credit safety |
| `mmhub_mmutcl2_mmvml2vcdec` | `0x6a100` | 736-1176 | VM contexts, invalidate engines, context address ranges, and per-PF/VF PTE fragment sizes |
| `mmhub_mmutcl2_mmvml2pldec` | `0x6a490` | 1180-1208 | VM L2 and MMUTCL2 performance-counter configuration |
| `mmhub_mmutcl2_mmvml2prdec` | `0x6a4e0` | 1212-1220 | VM L2 and MMUTCL2 performance-counter result registers |
| `mmhub_mmutcl2_mmvmsharedhvdec` | `0x6a530` | 1224-1227 | Shared/hypervisor-facing PCIe ATS control |
| `mmhub_mmutcl2_mmvmsharedpfdec` | `0x6a740` | 1230-1284 | PF/shared MMIO, PCI, top-of-DRAM, FB offset, aperture, steering, reset, memory power, local memory, clock, and active function registers |
| `mmhub_mmutcl2_mmvmsharedvcdec` | `0x6a7b0` | 1288-1304 | FB location, AGP range, system aperture, and L1 TLB control |
| `mmhub_mmutcl2_mmatcl2pfcntrdec` | `0x6a800` | 1308-1312 | ATC L2 performance-counter result registers |
| `mmhub_mmutcl2_mmatcl2pfcntldec` | `0x6a820` | 1316-1322 | ATC L2 performance-counter configuration |
| `mmhub_mmutcl2_mmvml2pspdec` | `0x6ae50` | 1326-1340 | PSP-adjacent translation bypass, IOMMU, translation-fault, and VSCH power status registers |
| `mmhub_mmutcl2_mml2tlbpspdec` | `0x6ae80` | 1344-1346 | GPUVA/VMID translation-assist control |
| `mmhub_mmutcl2_mmatcl2pspdec` | `0x6ae90` | 1350-1352 | ATC L2 IOV mode control |
| `mmhub_mmutcl2_mml2tlbpfdec` | `0x6aec0` | 1356-1370 | L2 TLB status, TMZ, translation-assist request/response, and credit safety |
| `mmhub_mmutcl2_mml2tlbpldec` | `0x6af00` | 1374-1384 | L2 TLB performance-counter configuration |
| `mmhub_mmutcl2_mml2tlbprdec` | `0x6af20` | 1388-1392 | L2 TLB performance-counter result registers |

The macro values are register indices consumed by AMD SOC15 register helpers, not byte offsets for direct C pointer dereferences.

## Control Flow

There is no runtime control flow in this header. The effective control path is preprocessor expansion:

1. A generation-specific AMDGPU or DC source includes `mmhub_3_3_0_offset.h` with `mmhub_3_3_0_sh_mask.h`.
2. Register helper macros such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_OFFSET`, and `WREG32_SOC15_OFFSET` receive symbolic constants like `regMMVM_CONTEXT0_CNTL` or `regMMVM_INVALIDATE_ENG0_REQ`.
3. The SOC15 access layer combines the IP block, instance, base index, and offset into an absolute MMIO address.
4. Runtime driver code sequences MMHUB initialization, VM context programming, invalidation, fault handling, aperture setup, clock gating, and display-resource setup using those addresses.

The sequencing is supplied by consumers, especially `amdgpu/mmhub_v3_3.c`. That file programs GART page-table base/start/end registers, system and AGP apertures, L1/L2 TLB/cache controls, VM context controls, invalidation ranges for 18 engines, SAW context registers, protection-fault defaults, framebuffer location/offset reads, and ATC L2 clock-gating state.

## State and Persistence Behavior

The header has no software state or persistence behavior of its own. It describes hardware state that persists in MMHUB registers until reset, power transition, or driver reprogramming:

- VM context state covers context enablement, page-table depth, page-table base addresses, logical start/end ranges, and context disablement.
- TLB/cache invalidation state uses semaphore, request, acknowledgement, and address-range registers for invalidate engines 0 through 17.
- Fault state includes dummy-page fault registers, L2 protection-fault controls/status/address/default address registers, translation-fault controls, and L1/SAW fault status/address registers.
- Aperture and memory-routing state includes AGP range, FB base/top/offset, system aperture low/high/default address, top-of-DRAM, cacheable DRAM, local system memory, and local framebuffer ranges.
- Power-management state includes PCTL deepsleep controls, ATC/UTCL/MMUTCL2 clock-gating and memory-light-sleep registers, VSCH power status, and state-save ranges.
- Virtualization and isolation state includes PCIe ATS, IOMMU controls, active function ID, shared virtual reset, local framebuffer lock control, per-PF/VF PTE cache fragment sizing, IOV mode, and translation bypass by VMID.
- Diagnostic state includes DAGB, PCTL, L1, VM L2, MMUTCL2, ATC L2, and L2 TLB performance-counter configuration/result registers.

Because all behavior is indirect, persistence risks arise when a consumer writes a valid sequence to the wrong offset or assumes the wrong base index.

## Dependencies

Direct source dependencies are deliberately minimal:

- The include guard `_mmhub_3_3_0_OFFSET_HEADER` prevents duplicate macro definition.
- Consumers pair this file with `mmhub/mmhub_3_3_0_sh_mask.h` for register-field shifts and masks.
- AMDGPU consumers include common types and register helpers through files such as `amdgpu.h`, `soc15_common.h`, and generation-specific MMHUB glue.
- Display Core consumers include this header beside DCN and NBIO offset/shift-mask headers plus `reg_helper.h`.

This header does not depend on Linux kernel types, C library APIs, inline functions, generated C tables, or runtime initialization.

## Integration Points

Direct include sites in this source tree are:

- `drivers/gpu/drm/amd/amdgpu/mmhub_v3_3.c`
- `drivers/gpu/drm/amd/display/dc/resource/dcn35/dcn35_resource.c`
- `drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c`

`mmhub_v3_3.c` is the main runtime integration point. It uses these offsets to initialize `adev->vmhub[AMDGPU_MMHUB0(0)]`, calculate register spacing from adjacent macro values, program GART and VMID registers, configure MMHUB L1/L2 translation behavior, handle invalidation request construction and acknowledgement register addresses, log L2 protection faults, read framebuffer base/offset, and toggle ATC L2 clock-gating/light-sleep fields.

The DCN 3.5 and 3.5.1 resource files include this header so display register tables and VMID/resource helper code can reference MMHUB registers consistently with the matching DCN and NBIO generation headers. The path under `include/asic_reg/mmhub/` marks this file as an ASIC register contract shared by AMDGPU core and display code, not as an algorithmic module.

## Risks and Edge Cases

- Base-index mismatch: all MMHUB 3.3.0 offsets here use base index `1`; consumers that hard-code another generation's base index can address the wrong register segment.
- Register-map drift: MMHUB 3.3.0 differs from MMHUB 2.x and other 3.x headers. Copying offsets across generations can silently break GART, fault handling, display, or power-management paths.
- Token-pasted macro contracts: register helpers and tables rely on exact `reg...` and `reg..._BASE_IDX` names. Renaming or deleting macros can break builds, while introducing an incorrectly named compatible macro can compile but access wrong hardware.
- Register-spacing assumptions: `mmhub_v3_3.c` derives `ctx_distance`, `ctx_addr_distance`, `eng_distance`, and `eng_addr_distance` from adjacent macros. Non-contiguous generated layouts would break offset-based loops.
- 64-bit register pairs: page-table base/start/end, aperture, fault address, default address, translation-assist, and framebuffer-related registers are split into low/high halves. Consumers must preserve required write order and bit shifts; this header only supplies the addresses.
- Context and invalidation cardinality: the file exposes 16 VM contexts and 18 invalidate engines. Loop bounds in consumers must stay aligned with this hardware contract.
- Security-sensitive virtualization registers: ATS, IOMMU, IOV mode, PF/VF PTE fragment sizes, active function ID, virtual reset, and local framebuffer lock registers affect isolation boundaries.
- Power-management sensitivity: PCTL, clock-gating, memory-light-sleep, and register-save-range offsets can affect suspend/resume and display stability if programmed in the wrong sequence.
- Reserved or diagnostic registers: reserved-looking, perf-counter, and credit-safety registers should not be treated as scratch state. Some may have side effects or hardware-specific access rules.

## Test Signals

Useful validation signals for this header are mostly build-time and hardware/runtime checks:

- Build AMDGPU and DC code paths that include `mmhub_3_3_0_offset.h`; missing or renamed macros should fail in `mmhub_v3_3.c`, `dcn35_resource.c`, or `dcn351_resource.c`.
- Exercise ASICs using MMHUB IP versions 3.3.0, 3.3.1, 3.3.2, or adjacent v3.4 paths in `mmhub_v3_3.c` and check that VM hub initialization completes.
- Boot with GART enabled and verify page-table base/start/end programming for context 0 and VMID contexts 1-15.
- Trigger TLB/cache invalidation and confirm invalidate request/ack/semaphore registers progress without timeouts across all expected engines.
- Run display modeset and DCN 3.5/3.5.1 smoke tests to cover display-resource inclusion of the MMHUB register map.
- Check controlled or logged VM faults for meaningful `MMVM_L2_PROTECTION_FAULT_STATUS` client IDs, addresses, and fault-class bits.
- Run suspend/resume and runtime clock-gating tests to cover PCTL, ATC L2 clock-gating, memory-light-sleep, and register-save-related offsets.
- Validate SR-IOV or virtualization scenarios where supported, especially ATS/IOMMU, active function, local framebuffer lock, and PF/VF PTE fragment-size registers.
- Compare this generated offset file with the authoritative AMD register database when regenerating MMHUB 3.3.0 headers.

## Research Notes

The source file was read completely across all 1,395 lines. It is a generated-style register-offset header, so the substantive behavior is captured through its macro families, address-block layout, actual include sites, and the runtime AMDGPU/DC code paths that consume those offsets.
