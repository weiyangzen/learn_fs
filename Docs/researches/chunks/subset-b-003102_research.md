# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 83012-85506

## Scope

This chunk is a generated AMD NBIO 7.0 register shift/mask header segment. It contains only C preprocessor constants; there are no functions, structs, variables, allocation paths, locks, branches, loops, direct MMIO accesses, or persistence paths in this range.

The slice starts inside the `nbio_iohub_iommu_l2indx_l2indxcfg` address block, at the tail of L2B IOMMU controls. It then covers L2B shadow bus-number registers, L2B PSP hardware-error reporting, NB IOAPIC routing and shadow remap registers, two mirrored IOMMU L1 register sets for `PCIE0` and `IOAGR`, their L1 shadow and L1 PSP sub-blocks, the L2A IOMMU block and L2A shadow block, and finally the first `SMMU_IDR0` shift definitions through `PRI`. The remainder of `SMMU_IDR0` and its masks continue after this chunk.

Although this file is under a local `ceph-client` source mirror, this header is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header range is to publish bit positions for NBIO 7.0 IOMMU, IOAPIC, PSP-error, and SMMU capability registers. Each generated hardware field is represented as:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when packing or extracting the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, clear, preserve, or update the field.

The companion address file, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_offset.h`, provides the matching `mm`, `ix`, or `smn` register locations. Runtime AMDGPU code combines those offsets with this shift/mask header through register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and `SOC15_REG_OFFSET`.

## Important Macro Families

The opening L2B fragment completes part of `nbio_iohub_iommu_l2indx_l2indxcfg`. It includes L2B memory-power-gating thresholds and maintain counters, performance counter controls/counts for events 4 through 7, DVM request and invalidation page-size controls, SDP max-credit and parity-error-enable bits, and an ECO control dword. Earlier L2B cache, credit, error-rule, page-size, and power-gate enable fields are outside this chunk.

The `nbio_iohub_iommu_l2bshdw_l2bshdw` block defines shadowed subordinate bus-number fields for `PCIE0` ports 0 through 7 and `NBIF1` ports 0 through 1. These macros expose secondary and subordinate bus-number fields used when the hardware mirrors or consumes PCI bridge bus-range configuration.

The `nbio_iohub_iommu_l2bpsp_l2bpsp` block defines PSP-visible L2B hardware-error reporting. It includes enable/support bits, hardware-error valid/overflow status, lower and upper event-code capture registers, and a high-register `EV_CODE` nibble. This is diagnostic metadata for hardware errors; the header does not define status clear semantics.

The IOAPIC configuration block defines feature enables, bridge interrupt routing for bridge groups `BR0` through `BR8`, serial interrupt status, scratch registers, clock-gating controls, SDP port disconnect hysteresis, four IOAPIC performance counters with upper dwords, and page-slave hysteresis. The matching IOAPIC shadow block defines programmed device/function remap fields for `PBr0` through `PBr8`.

The `nbio_iohub_iommu_l1_PCIE0_iommul1cfg` and `nbio_iohub_iommu_l1_IOAGR_iommul1cfg` blocks are mirrored IOMMU L1 front-end definitions for the PCIe0 path and IOAGR path. Each block defines four L1 performance counters, sideband location, L1 control registers, bank select/disable fields, 32 work-queue entry-status fields plus invalidation status, debug sticky bits, program-memory power-gating controls, clock-gating controls, guest-address checking, feature support reporting, page-slave status, ATS response timers, traffic-stall controls for DMA and host request/response channels, SDP credit limits, and ECO control.

The L1 control families are the densest part of the chunk. `L1_CNTRL_0` covers unfilter/fragment behavior, read/write-only cache modes, L2 credits, L1 bank and entry sizing, error-event detect disable, host response pass behavior, and interrupt half-dword handling. `L1_CNTRL_1` covers cache bypass, cache and general parity enablement, DTE disable, work-queue entry disable mask, send-filter disable, ordering, global cache invalidation, timeout pulse selection, cache selection policy, pretranslation/untranslated filters, strict VC ordering, and chained DMA use. `L1_CNTRL_2` includes L1 disable, MSI-to-HT remap disable, ATS abort behavior, ATS/data error signaling, CPD response mode, SDP parity, and VC flush invalidation controls. `L1_CNTRL_4` covers multiple ATS responses, timeout pulse extension, ATS response memory-type sending, and internal graphics unit ID validity.

The L1 shadow blocks for `PCIE0` and `IOAGR` expose the IOMMU MMIO view seen through shadow registers. Both include device-table size fields for banks 0 through 7, MMIO control enables for IOMMU/event logging/interrupts/command buffer/PPR/GT/GA/TLPT, DTE segment enablement, exclusive base and limit windows, counter bank locks, and repeated performance counter match programming for two banks by four counters. Each counter instance has source, count-unit, and counter-active-control bits, plus optional PASID, domain, and device-id match/mask and enable fields.

The L1 PSP blocks for `PCIE0` and `IOAGR` define CPD error reporting and request capture: CPD support, valid/overflow status, request stream ID, request address low/high dwords, and an `AbortPreTrans` request-control bit. These fields are PSP/error-reporting integration points, not regular software state containers.

The `nbio_iohub_iommu_l2a_l2acfg` block defines the L2A side of the IOMMU cache/control plane. It includes performance counters 0 through 3, an L2 status dword, L2 controls for L1 cache acceptance, side PTE behavior, FIFO priorities, sequential invalidation burst limits, DTC/ITC/PTC-A cache controls, hash masks, way disable/access-disable controls, L2 credit controls, update-filter behavior, error-rule disable controls, clock gating, page-size controls, memory power gating thresholds/maintain counters, IP power-gate threshold/status/busy/firmware-exit fields, and an ECO dword.

The `nbio_iohub_iommu_l2ashdw_l2ashdw` block exposes L2A shadowed IOMMU MMIO control. It includes device-table sizes, IOMMU/GT/GA/SMIF/SMIF-log/GAM enables, DTE segment/privileged-abort/EPH controls, exclusive windows, four SMI filter registers with DID/valid/lock fields, capability mirrors, and writable capability/support fields such as IOTLB/EFR, PREF/PPR/NX/GT/GA/PC/HATS/US/GAM, PAS_MAX, DTE segment width, and EPH support.

The final `nbio_iohub_smmu_mmio_smmummiocfg` fragment only begins `SMMU_IDR0`. This assigned range includes shifts for S2P, S1P, TTF, COHACC, BTM, HTTU, DORMHINT, Hyp, ATS, PERFCTRS, ASID16, MSI, SEV, ATOS, and PRI. The corresponding masks and later `SMMU_IDR0` fields start after line 85506 and are outside this chunk.

## Control Flow

There is no executable control flow in this header. Runtime behavior occurs only in code that includes these generated constants:

1. AMDGPU or related platform code selects a register offset from `nbio_7_0_offset.h`.
2. It reads, composes, or updates a 32-bit register value through the AMD register access layer.
3. It applies this header's `__SHIFT` and `_MASK` macros directly or through `REG_SET_FIELD` and `REG_GET_FIELD`.
4. It writes a control value, decodes a capability/status value, polls hardware-owned status, clears sticky diagnostics, or exposes decoded state to higher-level IOMMU, PCIe, IOAPIC, PSP, SMMU, power-management, or debugging code.

Typical consumers are initialization and tuning paths for NBIO/IOMMU cache hierarchy, PCIe/IOAGR translation front-ends, interrupt routing, power/clock gating, ATS and DVM invalidation, hardware error reporting, performance counter programming, and suspend/resume restoration.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed register state owned by the GPU, firmware/PSP, the NBIO/IOMMU blocks, IOAPIC routing hardware, and the host platform.

The represented state includes static capability bits, software-programmed control bits, hardware-updated status, sticky diagnostic/error captures, performance-counter selector/count state, bridge bus-number shadows, IOAPIC route/remap configuration, cache and translation-cache sizing/control, exclusive MMIO windows, PASID/domain/device-id performance-counter filters, SMI filter lock/valid state, power/clock-gating thresholds and status, and SMMU feature discovery. Some fields are read-only capabilities, some are writeable policy controls, some are volatile counters, and some may be write-one-to-clear or firmware-owned diagnostics. The generated masks do not encode access width, reset defaults, side effects, ordering requirements, or ownership rules.

Mirrored `PCIE0` and `IOAGR` L1 blocks should be treated as separate hardware instances with parallel layouts. The repeated shadow performance-counter match registers should be treated as bank/counter-indexed state rather than independent semantic features.

## Dependencies And Integration Points

The primary dependency is the generated NBIO 7.0 register database. This file must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_offset.h`, which supplies the matching register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h`, which supplies reset/default values where generated.
- AMDGPU register helper macros and accessors, including `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and `SOC15_REG_OFFSET`.

The meaningful integration surfaces are AMDGPU NBIO setup, GPU IOMMU/SMMU configuration, PCIe and IOAGR translation front-end policy, ATS/DVM invalidation handling, PPR/CPD and PSP error reporting, IOAPIC interrupt routing and bridge swizzling, performance monitoring, clock and memory power gating, page-size and exclusive-window programming, and debug or RAS-style hardware diagnostics.

These definitions also overlap generic platform domains: PCI bridge bus-number assignment, IOAPIC interrupt delivery, IOMMU translation and invalidation, PASID/domain/device matching, ATS/PRI capability discovery, MSI-capable SMMU behavior, power-management clock gating, and firmware-owned error capture. Consumers must pair each mask with the correct offset, instance, and access protocol.

## Risks And Edge Cases

- The chunk boundaries are artificial. It starts after the beginning of the L2B indexed block and ends before the `SMMU_IDR0` register definition is complete, so adjacent chunks are required for full L2B and SMMU analysis.
- These are untyped preprocessor constants. A stale shift or mask compiles cleanly while decoding or programming the wrong hardware bit.
- `PCIE0` and `IOAGR` L1 blocks are mechanically mirrored. Copy/paste mistakes can silently target the wrong instance or use the wrong prefix while producing plausible register values.
- L1 and L2 controls include translation, cache, ordering, parity, ATS, DVM, and flush behavior. Incorrect values can cause stale translations, DMA faults, ordering violations, missed invalidations, or hangs under load.
- Work-queue status and invalidation status fields are hardware-owned and may be transient. Generic read/modify/write treatment can mis-handle live status or poll the wrong completion condition.
- PSP CPD and L2B hardware-error status fields may be sticky, overflow-sensitive, firmware-owned, or write-one-to-clear. Careless updates can lose first-error evidence or mask later diagnostics.
- IOAPIC bridge routing and shadow remap fields are interrupt-delivery sensitive. Incorrect group, swizzle, internal map, or DevFn remap values can misroute INTx-style interrupts or break platform enumeration assumptions.
- Power and clock gating fields interact with idle detection and wakeup. Aggressive threshold, hysteresis, or gate-enable programming can create intermittent access failures or resume/runtime-PM regressions.
- Counter match registers combine source selection, PASID/domain/device-id filters, masks, enables, locks, and active-control bits. Partial updates can collect misleading performance data or leave counters locked to stale filters.
- Reserved fields are explicitly named in many masks. Consumers must preserve reserved bits according to hardware guidance; generated masks alone do not tell whether writing zero is safe.
- Capability mirrors such as IOMMU, SMMU, ATS, PRI, MSI, GT/GA, PPR, EFR, HATS, and GAM should not be treated as independent software policy without checking hardware/firmware ownership and platform support.

## Test Signals

Useful validation is primarily build-time and hardware-integration oriented:

- Build AMDGPU with NBIO 7.0 support enabled; missing, renamed, or duplicated macros should surface in NBIO/IOMMU/SOC15 include paths that consume this generated header.
- Compare this range against `nbio_7_0_offset.h` and `nbio_7_0_default.h` to confirm register names, address blocks, repeated `PCIE0`/`IOAGR` layouts, L1 shadow bank/counter strides, and L2A/L2B naming remain synchronized.
- Boot affected hardware and confirm IOMMU enablement, ATS/DVM invalidation, DMA workloads, and PCIe/IOAGR request paths operate without translation faults or hangs.
- Exercise suspend/resume and runtime power-management flows while monitoring L1/L2 page-slave status, clock-gating, memory-power-gating, and power-gate busy/status fields.
- Validate IOAPIC bridge interrupt routing by exercising INTx/MSI-adjacent paths and checking for lost, swizzled, or misrouted interrupts on bridge groups `BR0` through `BR8`.
- Use available hardware diagnostics or error-injection paths to verify L2B PSP hardware-error valid/overflow/event-code fields and L1 PSP CPD request capture fields behave as expected.
- Program and read L1/L2/IOAPIC performance counters where supported; counter selection, upper/lower count fields, PASID/domain/device-id filters, and lock bits should match expected traffic.
- Run IOMMU stress with PASID, ATS, PRI, and invalidation-heavy workloads; stale translations, CPD/PPR events, or unexpected work-queue/invalidation status values can indicate mask/offset drift.
- Confirm reserved bits are preserved in read/modify/write users and that control writes do not change hardware-owned status or sticky diagnostic fields unexpectedly.

## Chunk Notes

- Lines 83012-83104 are a tail fragment of `nbio_iohub_iommu_l2indx_l2indxcfg`, focused on L2B memory power gating, performance counters, DVM controls, SDP credits/parity, and ECO state.
- Lines 83105-83157 cover L2B shadowed bus-number fields for `PCIE0` ports 0-7 and `NBIF1` ports 0-1.
- Lines 83158-83189 cover L2B PSP hardware-error reporting.
- Lines 83190-83367 cover IOAPIC feature/routing/performance/power controls and IOAPIC shadow DevFn remap fields.
- Lines 83368-85091 cover mirrored `PCIE0` and `IOAGR` IOMMU L1, L1 shadow, and L1 PSP blocks.
- Lines 85092-85489 cover L2A IOMMU configuration and shadow MMIO/capability fields.
- Lines 85490-85506 only begin the SMMU MMIO `SMMU_IDR0` register; masks and remaining fields are outside this work item.
