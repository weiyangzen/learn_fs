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
