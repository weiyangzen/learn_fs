# Research: subset-b-001467

Grouped research for AMDGPU ATHUB ASIC register headers. Each section is keyed by the original source path and is intended to split directly into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_1_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_1_0_sh_mask.h

## Purpose
This generated-style header defines the shift and mask constants for ATHUB 1.0 hardware registers used by the AMDGPU driver. It is not executable code; it is the bitfield contract that lets register helper macros compose, update, and decode 32-bit ATHUB register values without open-coded literals.

The covered hardware blocks are `athub_atsdec`, `athub_xpbdec`, and `athub_rpbdec`. Together they describe address translation service controls, PCIe PASID/PRI/ATS enablement, VMID-to-PASID mappings, fault reporting, performance counters, crossbar/routing and peer-to-peer BAR mappings, clock/power gating, queue arbitration, credit handling, and RPB request scheduling.

## Important APIs, Types, and Macros
The file exports preprocessor constants only. Every field follows the same pattern: `REGISTER__FIELD__SHIFT` gives the bit offset and `REGISTER__FIELD_MASK` gives the corresponding masked bit range. Consumers typically use these through AMDGPU register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `REG_UPDATE`, or generated mask/shift tables in ASIC-specific code.

Important ATSDEC groups include:
- `ATC_ATS_CNTL`, `ATC_ATS_STATUS`, and `ATC_ATS_FAULT_*` fields for enabling/disabling ATC, PRI, PASID, tracking busy/crash/deadlock state, and decoding fault type, VMID, invalidation/page-request status, and fault address.
- `ATC_TRANS_FAULT_RSPCNTRL` and `ATC_VMID_PASID_MAPPING_UPDATE_STATUS` per-VMID bitmaps for controlling fault response behavior and tracking VMID remapping completion across VMID 0-31.
- `ATC_VMID0_PASID_MAPPING` through `ATC_VMID31_PASID_MAPPING`, each exposing `PASID`, `NO_INVALIDATION`, and `VALID` fields used to bind a GPU VMID to a process address-space identifier.
- `ATC_ATS_VMID_STATUS`, GFX/MMHUB ATCL2 status, VMID snapshot status registers, and `ATC_ATS_SDPPORT_CNTL` for outstanding translation state, power-down status, snapshot bits, and SDP/UTCL2 communication tuning.
- `ATHUB_PCIE_ATS_CNTL`, `ATHUB_PCIE_PASID_CNTL`, `ATHUB_PCIE_PAGE_REQ_CNTL`, `ATHUB_PCIE_ATS_CNTL_VF_0` through `_VF_15`, shared virtualization reset/active-function fields, memory light sleep, and interrupt-handler credit fields.

Important XPBDEC groups include:
- Router source aperture registers `XPB_RTR_SRC_APRTR*` and `XPB_XDMA_RTR_SRC_APRTR*`.
- Destination maps `XPB_RTR_DEST_MAP*` and `XPB_XDMA_RTR_DEST_MAP*`, with `NMR`, `DEST_OFFSET`, destination selection, RPB destination selection, and aperture size fields.
- Cache/lookup grouping fields such as `XPB_CLG_CFG*`, `XPB_CLG_EXTRA*`, GFX/MM match and mask registers, and GFX/MM unit-ID mapping registers.
- Peer-to-peer BAR and peer system BAR fields, including BAR validity, address, send/disable/compression flags, register and memory system BAR selectors, and delta-above/below controls.
- Interface, pipe, sticky, sub-block reset/stall, clock-gating, and performance knob fields such as `XPB_INTF_CFG`, `XPB_INTF_STS`, `XPB_PIPE_STS`, `XPB_SUB_CTRL`, `XPB_CLK_GAT`, and `XPB_PERF_KNOBS`.

Important RPBDEC groups include:
- PassPW and block-level override fields in `RPB_PASSPW_CONF` and `RPB_BLOCKLEVEL_CONF`.
- Tag, arbitration, BIF, VC switch, switch count, queue-mapping, deinterleave/combine, and ATS command fields.
- RPB performance counter select/mode/enable/clear and result controls.
- Read/write queue controls and queue pattern masks for queues 4 and 5, plus `RPB_EA_QUEUE_WR` and `RPB_SDPPORT_CNTL` fields for EA queue assignment and NBIF/DF SDP-port behavior.

## Control Flow
There is no runtime control flow, branching, function dispatch, or initialization in this header. Its "flow" is compile-time inclusion: AMDGPU source that needs ATHUB 1.0 register bitfields includes this file, then uses the constants to generate bit values for memory-mapped register reads and writes.

The ordering inside the file mirrors the hardware register address blocks and repeated register families. That ordering matters for human auditability and generator diffs, but not for C execution.

## State and Persistence Behavior
The header itself stores no state. The constants describe persistent hardware state in memory-mapped ATHUB registers. Writes performed by consumers can persist until reset, power-gating transitions, GPU reset, VMID remapping, or explicit driver reprogramming, depending on the underlying register.

State-sensitive areas are ATS/PASID enablement, VMID-PASID validity bits, outstanding invalidation and translation status, fault log/register routing, virtualization reset request bits, P2P BAR validity and address fields, XPB sticky status/write-one-to-clear bits, RPB arbitration and queue mapping, and clock/power gating controls.

## Dependencies and Integration Points
This header has only an include guard and no C includes. It depends on the AMDGPU register-generation naming convention and on matching offset headers that provide register addresses, such as ATHUB offset headers in the same directory. It integrates with DRM AMDGPU low-level register access code, GPU memory-management and HMM/SVM paths using PASID/ATS/PRI, SR-IOV virtualization paths using PF/VF fields, interrupt/fault handling, power management, and performance counter/debug code.

Because it is a generated hardware contract, correctness depends on alignment with ASIC documentation and sibling generated headers. Register names must match whatever code assembles `reg*`, mask, and shift tables for a particular ASIC generation.

## Risks
The main risk is silent hardware misprogramming from an incorrect mask or shift. A one-bit error in PASID, VMID, ATS, PRI, fault, P2P BAR, queue, or reset fields can produce address-translation failures, bad process isolation, lost fault reporting, hangs, data corruption, or broken SR-IOV behavior.

Repeated families are another risk. VMID 0-31 mappings, VF 0-15 ATS controls, route maps, BARs, queue controls, and performance counter fields are structurally repetitive, so generator or manual-copy drift can affect only one lane and remain hard to spot. The file also mixes full-width fields such as `0xFFFFFFFFL` with signed-looking long constants such as `0x80000000L`; consumers must treat register values as unsigned 32-bit quantities.

## Test Signals
Useful validation signals are compile coverage for all ASIC files that include this header, generated-header diff checks against the authoritative register database, boot and GPU reset on ATHUB 1.0 hardware, SVM/PASID workloads, ATS/PRI enable-disable paths, VMID remapping and invalidation tests, GPU fault injection and fault log decode, SR-IOV PF/VF reset and ATS enable tests, P2P/XDMA BAR routing tests, performance counter readback, power/clock-gating smoke tests, and stress tests that exercise RPB queue arbitration under concurrent DMA and GPU memory traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_1_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_1_8_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_1_8_0_offset.h

## Purpose
This generated-style header defines register offsets and base-index selectors for the ATHUB 1.8.0 hardware block in AMDGPU. It does not define bitfields; it maps symbolic `reg*` names to register offsets within ATHUB address blocks and pairs each register with a `*_BASE_IDX` value so driver register helpers can choose the correct MMIO base.

The file covers three address blocks: `aid_athub_atsdec` at base address `0x3080`, `aid_athub_xpbdec` at base address `0x46000`, and `aid_athub_rpbdec` at base address `0x46200`.

## Important APIs, Types, and Macros
The exported API is a set of C preprocessor constants. Each register has a `regNAME` offset and a `regNAME_BASE_IDX` selector. Base index `0` is used for the ATSDEC block, while base index `1` is used for XPBDEC and RPBDEC registers in this header.

The ATSDEC block includes offsets for `ATC_ATS_CNTL` through `ATC_ATS_CNTL4`, miscellaneous and status controls, ATC performance counters, fault status registers `INFO` through `INFO4`, fault address/default-page registers, PCIe ATS/PASID/page-request controls, outstanding page request allocation, ATHUB command, per-VF ATS controls for VF 0-15, shared virtualization reset and active function ID, SDP port control, VMID/PASID mapping update status, VMID0-VMID15 PASID mappings, translation fault response control, VMID status, ATHUB miscellaneous and memory power controls, and IH credit.

The XPBDEC block includes router source aperture offsets, XDMA source apertures, router and XDMA destination maps, CLG configuration and extra/mask registers, LB and WCB status, host configuration, P2P BAR configuration and BAR0-BAR7, BAR setup and delta controls, peer system BAR0-BAR9, XDMA peer system BAR0-BAR3, clock gating, interface and pipe status/configuration, sub-block control, map invert flush LSB, performance knobs, sticky and sticky write-one-to-clear registers, miscellaneous config, readback variants of CLG extra/mask, GFX/MM match and mask registers, and GFX/MM unit-ID mapping registers.

The RPBDEC block includes passPW, block-level, tag, arbitration, BIF, performance counter, deinterleave/combine, VC switch, RPB performance counter low/high/config/result registers, ATS controls, and RPB SDP port control.

## Control Flow
There is no executable control flow. Consumers include this file to resolve symbolic register names into numeric offsets at compile time. Runtime control flow lives in the callers that issue MMIO reads/writes through AMDGPU register helper macros.

The source order is the logical register order within each address block. This helps pair offsets with matching shift/mask headers and supports generated table construction, but the C preprocessor does not impose runtime behavior.

## State and Persistence Behavior
The header has no software state or persistence. Its constants identify where persistent hardware state resides in the GPU MMIO register aperture. The actual state includes ATS/PASID enablement, fault logs, VMID mappings, per-VF ATS state, P2P routing windows, interface status, sticky status, performance counters, and RPB scheduling controls.

Incorrect offsets directly redirect register accesses to the wrong hardware location. That makes this header part of the persistence contract for reset, resume, VMID setup, virtualization setup, fault handling, and performance diagnostics on ATHUB 1.8.0 devices.

## Dependencies and Integration Points
This file has only an include guard and no C includes. It depends on sibling shift/mask headers for field definitions and on AMDGPU register access conventions that combine `reg*` offsets, `*_BASE_IDX` selectors, and mask/shift constants. It integrates with AMDGPU ASIC initialization, memory-management and address-translation paths, SR-IOV virtualization, PCIe ATS/PRI/PASID programming, XPB P2P routing, RPB queue/performance tuning, fault handling, and debug/performance counter tooling.

Compared with the ATHUB 1.0 mask file in this work item, this header represents a later hardware generation and only carries offsets. Correct driver use requires matching it with the ATHUB 1.8.0 shift/mask header, not with an older generation's field layout unless code has explicitly verified compatibility.

## Risks
The largest risk is offset/base-index drift. A wrong offset can make a valid register write hit an unrelated register, and a wrong base index can access the right offset in the wrong ATHUB address block. Either failure can break ATS setup, fault collection, SR-IOV VF control, P2P routing, or RPB scheduling in ways that are difficult to diagnose from software logs alone.

Generation skew is also important. The 1.8.0 ATSDEC block includes newer control and fault-info registers such as `ATC_ATS_CNTL2`, `ATC_ATS_CNTL3`, `ATC_ATS_CNTL4`, `ATC_ATS_MISC_CNTL`, and fault status `INFO3/INFO4`, while the VMID mapping list in this offset header runs through VMID15. Code shared with other ATHUB generations must not assume identical register presence or count.

## Test Signals
Useful signals include all-ASIC AMDGPU build coverage, generated-header consistency checks against the register database, register read/write smoke tests for base index 0 and 1, GPU reset and resume on ATHUB 1.8.0 hardware, ATS/PASID/PRI enablement tests, VMID mapping and invalidation tests, SR-IOV VF ATS control tests, fault injection with status/fault-address readback, XPB P2P/XDMA routing tests, sticky status write-one-to-clear checks, RPB performance counter readback, and tracing that confirms expected MMIO addresses are produced from `reg*` plus base index selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_1_8_0_offset.h -->
