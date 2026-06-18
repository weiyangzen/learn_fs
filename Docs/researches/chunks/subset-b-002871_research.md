# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_1_sh_mask.h lines 8352-10281

## Scope

This chunk is the tail of AMDGPU's generated NBIF 6.1 register bitfield header. It contains C preprocessor `*_MASK` constants only; there are no functions, structs, enums, allocations, locks, or executable branches. The macros describe hardware register fields that driver code combines with companion register-address and shift definitions, normally through AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, and indirect MMIO accessors.

The range starts in the middle of the `RCCSTRAPRCCSTRAP_RCC_DEV0_EPF0_STRAP2` mask family and ends at the file's `#endif`, so adjacent chunks are needed for the matching shift definitions and the first masks in the same strap register.

## Purpose

The chunk maps NBIF register fields for PCIe endpoint strap configuration, BIF reset and interrupt control, BIF miscellaneous behavior, RAS reporting, PCI function-control restore state, MSI-X table entries, and System Hub indirect QoS/power-management controls. These masks let AMDGPU code program or decode 32-bit hardware registers without embedding raw bit constants in C logic.

Although the repository path is under `distributed-fs/ceph-client`, this source is Linux AMD GPU driver hardware-description data under `drivers/gpu/drm/amd/include/asic_reg/nbif`; it is not Ceph client protocol or filesystem logic.

## Important Macro Families

`RCCSTRAPRCCSTRAP_RCC_DEV0_EPF0_STRAP2` through `RCC_DEV1_EPF2_STRAP13` define PCI endpoint-function strap masks. They cover device/subsystem/vendor IDs, revision and class-code fields, function enable, legacy-device type, D1/D2 support, MSI/MSI-X, AER/ACS/ATS/PASID, atomics, FLR, PME, interrupt pin, BAR and aperture sizing, ROM and VGA disables, doorbell aperture sizing, SR-IOV VF mapping, VF aperture sizes, resize BAR support, and per-function capability toggles. The families repeat across device 0 functions 0-7 and device 1 functions 0-2, with function-specific omissions such as extra VF/doorbell fields on graphics-facing functions.

`HARD_RST_CTRL`, `RSMU_SOFT_RST_CTRL`, and `SELF_SOFT_RST` define reset enables or asserted reset bits for dispatch/config/private endpoint paths, sticky reset handling, SWUS shadow reset, strap reload, SDP port reset, and core reset. `GFX_DRV_MODE1_RST_CTRL` adds PF/VF driver-mode reset controls.

`DEV0_PF*_FLR_RST_CTRL` and `DEV0_PF*_D3HOTD0_RST_CTRL` describe which PF, VF, soft-PF, config, private, sticky, FLR-exception, and dummy-response behaviors participate in function-level reset or D3hot-to-D0 reset. PF0 has the broadest VF/soft-PF coverage; PF1-PF7 mostly carry PF reset enables plus FLR grace and dummy response status fields.

`BIF_INST_RESET_INTR_STS/MASK`, `BIF_PF_FLR_INTR_STS/MASK`, `BIF_D3HOTD0_INTR_STS/MASK`, `BIF_POWER_INTR_STS/MASK`, `BIF_PF_DSTATE_INTR_STS/MASK`, and `BIF_PF0_VF_FLR_INTR_STS/MASK` define interrupt status and mask bits for link reset, driver reset modes, PF FLR, D3hot-D0 transitions, PME turnoff, port D-state changes, PF D-state changes, and PF0 VF FLR events. Matching `BIF_PF_FLR_RST` and `BIF_PF0_VF_FLR_RST` masks trigger or represent PF/VF reset state.

`BIF_DEV0_PF*_DSTATE_VALUE` and `BIF_PORT0_DSTATE_VALUE` expose target and acknowledge D-state fields, with a per-PF `NEED_D3TOD0_RESET` bit. Callers use these when coordinating PCI power-state transitions with reset policy.

`BIF_RST_MISC_CTRL*` and `BIF_RST_GFXVF_FLR_IDLE` capture reset policy knobs and idle observability: error-status retention across PERST, driver reset mode, auto-clear behavior, link-reset grace timers, SR-IOV VF-save behavior, DMA dummy response behavior, reset transaction idle bits, strap reload delays, PME turnoff timeout/mode, and per-VF/soft-PF transaction-idle reporting.

`MISC_SCRATCH`, `INTR_LINE_POLARITY`, `INTR_LINE_ENABLE`, and `OUTSTANDING_VC_ALLOC` provide scratch, interrupt-line routing, and outstanding-request allocation fields for DMA and host virtual channels.

`BIFC_MISC_CTRL0/1`, `BIFC_THT_CNTL`, `BIFC_HSTARB_CNTL`, `BIFC_GSI_CNTL`, `BIFC_PCIEFUNC_CNTL`, and `BIFC_SDP_CNTL_0` cover BIF client behavior: virtual-wire unit-ID checks, chain locking, DMA atomic checks, PCIe capability protection, VC7 DMA config disable, port D-state/PME modes, poison and ACS violation reporting, unsupported command status handling, ordering overrides, BME drop controls, credit allocation thresholds, host/GSI arbitration policy, completion interleaving, unsupported-request generation, non-PCIe bus/device/function mapping, and SDP disconnect hysteresis.

`BIFC_BME_ERR_LOG` and `BIFC_RCCBIH_BME_ERR_LOG` expose per-function "DMA or RCCBIH while BME low" status bits and corresponding clear bits. `BME_DUMMY_CNTL_0` controls dummy response status per function.

`BIFC_DMA_ATTR_OVERRIDE_DEV0_F0_F1` through `DEV0_F6_F7` define posted/non-posted override fields for ID-based ordering, relaxed ordering, and no-snoop attributes per PCI function. These masks are paired by two functions per register.

`NBIF_VWIRE_CTRL`, `NBIF_SMN_VWR_*`, and `NBIF_SDP_VWR_*` define virtual-wire reset delays, posted/block-level behavior, voltage-change disable sets, reset default or override values, and trigger bits for SMN and SDP virtual-wire paths.

`SMN_MST_CNTL0` and `SMN_MST_EP_CNTL1..4` configure SMN master behavior such as posted-mask enable, multi-transaction-ID disable, and zero byte-enable read/write handling for downstream and endpoint PF0-PF7 paths. `NBIF_REGIF_ERRSET_CTRL` controls whether non-PF MMREG requests set errors.

`BIFC_PERF_CNTL_0/1` and `BIFC_PERF_CNT_MMIO_RD/WR`, `BIFC_PERF_CNT_DMA_RD/WR` define enable, reset, select, and 32-bit value fields for MMIO and DMA read/write performance counters.

`BIF_RAS_LEAF0_CTRL` through `BIF_RAS_LEAF2_CTRL`, `BIF_RAS_MISC_CTRL`, `BIF_IOHUB_RAS_IH_CNTL`, and `BIF_RAS_VWR_FROM_IOHUB` describe RAS poison/parity detection, error-event generation, stall behavior, received/sent status, link-disable event reporting, IOHub RAS interrupt enable, and virtual-wire trigger status.

`RCC_PFC_*` and duplicated `RCCPFCAMDGFXAZ_RCC_PFC_*` masks cover PCI function-control latency tolerance reporting, PME restore state, sticky AER-style error restore fields, saved TLP header/prefix words, and auxiliary power override state for two related PFC decode blocks.

`PCIEMSIX_VECT0` through `PCIEMSIX_VECT31` define MSI-X table entry fields: low and high message address, message data, and vector mask bit. `PCIEMSIX_PBA` exposes the MSI-X pending-bit array.

`SYSHUBMMREGIND_*` masks define System Hub indirect controls for SOCCLK and SHUBCLK deep-sleep eligibility, deep-sleep timers, BGEN bypass/immediate enable, DMA switch QoS mode/min/max values, per-client reset-on-FLR/link-reset behavior, static QoS override, read/write weighted round-robin weights, clock gating, transaction-idle status for PF and VF0-VF15, a high-priority timer, and scratch storage.

## Control Flow and State

This header has no direct control flow. Its implicit runtime flow is imposed by the hardware protocols that callers implement:

1. Strap fields describe reset-sampled or firmware-provided PCI function capabilities that determine how Linux enumerates functions, BARs, MSI/MSI-X, SR-IOV, ATS/ACS/AER/PASID, atomics, and power-management capabilities.
2. Reset code selects hard, RSMU soft, self soft, FLR, link-reset, or D3hot-D0 reset masks, then observes idle, interrupt, D-state, or acknowledge-style fields before continuing.
3. Interrupt-handling code reads status masks, filters through matching mask registers, and clears or services PF, VF, power, D-state, and link/reset events.
4. BIF misc and virtual-wire setup code programs arbitration, attribute override, SMN/SDP virtual-wire, BME-dummy, and performance counter fields as ASIC initialization or debug policy requires.
5. RAS paths enable poison/parity detection and report/inspect error and stall status.
6. MSI-X setup treats each vector as a four-register table entry and uses the PBA masks to inspect pending vector bits.
7. System Hub power and QoS paths configure deep-sleep, clock gating, reset-on-FLR/link-reset, client QoS, and WRR weights, then may read transaction-idle fields during reset or power transitions.

State represented by these masks lives in GPU hardware registers, strap latches, MSI-X table storage, status latches, counters, or scratch registers. Some fields are durable configuration until reset or later writes; others are event/status/clear bits, reset triggers, performance counter reset bits, or transient idle indicators. This file does not enforce ordering, polling, locking, or persistence semantics; callers must sequence MMIO writes and reads according to NBIF hardware requirements.

## Dependencies and Integration Points

The macros depend only on the C preprocessor, but they are useful only with the generated NBIF 6.1 register address and shift headers. In AMDGPU they integrate with:

- ASIC initialization code that programs NBIF, PCIe, reset, power, and virtualization registers.
- PCI/SR-IOV setup paths that interpret endpoint-function capabilities, BAR/aperture sizing, VF mapping, ATS/ACS/AER/PASID, and MSI/MSI-X support.
- GPU reset and recovery paths that handle FLR, link reset, hard/soft reset, D3hot-D0 transitions, and transaction-idle polling.
- Interrupt paths for PF/VF FLR, link reset, power, PME, and D-state events.
- RAS code that enables or reads poison/parity error reporting from BIF leaves and IOHub interrupt wiring.
- Debug/perf code that selects and reads BIFC MMIO/DMA counters or scratch registers.
- Power-management code that programs NBIF clock gating, SOCCLK/SHUBCLK deep sleep, and System Hub transaction-idle checks.

## Risks

Bitfield accuracy is critical. A wrong mask can silently write the wrong hardware bit, causing PCI enumeration failures, incorrect BAR sizing, broken MSI/MSI-X delivery, bad SR-IOV VF isolation, ATS/ACS/AER/PASID capability mismatches, reset hangs, missed interrupts, RAS under-reporting, or performance/power regressions.

The chunk is highly repetitive across functions, VFs, vectors, and client lanes. Copy-generation mistakes are plausible around suffixes such as `DEV0_F*`, `DEV1_EPF*`, `PF0_VF*`, `PCIEMSIX_VECT*`, and `DMA_CLK*_SW*_CL*`. The line-range boundary also starts mid-register-family, so reconciliation with the previous chunk should confirm no `STRAP2` masks are dropped.

Several fields are security or isolation sensitive: SR-IOV VF mapping, VF aperture sizes, ATS/ACS/PASID enables, function enable bits, PCIe capability protection disable, non-PF MMREG request error handling, and SMN/SDP virtual-wire controls. Misprogramming them can expose memory or configuration state across PF/VF boundaries.

Reset and power fields are stateful and timing-sensitive. Incorrect grace timers, auto-clear settings, strap reload delays, dummy responses, transaction-idle checks, or D3hot-D0 reset participation may produce intermittent hangs that appear only under FLR, suspend/resume, hot reset, or virtualization teardown.

Performance and QoS masks can degrade behavior without obvious functional failure. Bad WRR weights, static QoS overrides, outstanding VC allocation, arbitration modes, or deep-sleep timers can surface as latency spikes, throughput loss, or power-state instability.

## Test Signals

Useful validation signals are build-time and hardware-facing rather than unit-level:

- The AMDGPU driver should compile with this generated header and companion offset/shift headers without duplicate or missing macro errors.
- PCI enumeration should expose expected device IDs, class codes, BARs, MSI/MSI-X, SR-IOV, ATS/ACS/AER/PASID, FLR, and PME capabilities for NBIF 6.1 ASICs.
- GPU reset tests should cover FLR, VF FLR, link reset, driver reset modes, D3hot-D0 transitions, suspend/resume, and transaction-idle polling without timeouts.
- Interrupt tests or logs should show expected PF/VF FLR, power, D-state, and link-reset interrupt status/mask behavior.
- RAS injection or error-reporting tests should confirm poison/parity enable and status fields are decoded correctly.
- MSI-X tests should confirm all 32 vector table entries and pending bits behave as expected.
- Power/performance telemetry should be checked after QoS, clock-gating, SOCCLK/SHUBCLK deep-sleep, and BIFC counter programming changes.
