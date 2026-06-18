# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 53622-56063

## Scope

This chunk is a generated AMDGPU NBIO 7.2.0 shift/mask header segment. It contains 2,092 `#define` field-layout macros and 348 register or address-block comments across 2,442 source lines. There are no C functions, structs, enums, variables, locks, allocations, or executable statements in this range.

The range begins one line into the `BIF_CFG_DEV0_EPF1_0_PCIE_VC_ENH_CAP_LIST` macro family, then covers the rest of endpoint function 1's PCIe extended capability bit layout. It includes Virtual Channel, Device Serial Number, Advanced Error Reporting, resizable BAR, power budgeting, DPA, Secondary PCIe, 8 GT/s and 16 GT/s lane equalization, lane margining, ACS, ATS, PRI/page request, PASID, multicast, LTR, ARI, SR-IOV, TPH, Data Link Feature, VF resizable BAR, and AMD GPU IOV vendor-specific VSEC fields. Near the end it switches at `addressBlock: nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp` and starts endpoint function 2's conventional PCI configuration and PCIe capability masks through the first three `MSIX_MSG_CNTL` shift fields. The following chunk is needed for the matching `MSIX_MSG_CNTL` masks and later EPF2 capability fields.

## Purpose

`nbio_7_2_0_sh_mask.h` is the bitfield half of AMD's generated NBIO 7.2.0 register interface. For each hardware register or PCI configuration-space word it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used to encode or extract the field.
- `<REGISTER>__<FIELD>_MASK`, the encoded mask used to isolate, preserve, clear, or update that field.

This chunk describes software-visible PCIe configuration and virtualization layout for NBIO device 0 endpoint functions 1 and 2. AMDGPU code combines these masks with addresses from `nbio_7_2_0_offset.h` and register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`. Although the source tree is under a `ceph-client` mirror, this file is AMDGPU hardware metadata and has no direct distributed-filesystem behavior.

## Important Macro Families

The opening EPF1 Virtual Channel and AER section defines PCIe traffic-class/resource and error-reporting layout:

- `PCIE_PORT_VC_*` and `PCIE_VC0/VC1_RESOURCE_*` describe extended VC counts, arbitration tables, TC-to-VC maps, resource IDs, resource enablement, and negotiation/status bits.
- `PCIE_DEV_SERIAL_NUM_*` provides device serial-number capability and low/high serial-number fields.
- `PCIE_ADV_ERR_RPT_*`, `PCIE_UNCORR_ERR_*`, `PCIE_CORR_ERR_*`, `PCIE_ADV_ERR_CAP_CNTL`, `PCIE_HDR_LOG0..3`, and `PCIE_TLP_PREFIX_LOG0..3` define AER status, mask, severity, first-error pointer, ECRC and multi-header logging controls, and diagnostic header/prefix log words.

The EPF1 resource, power, and link-training section covers:

- `PCIE_BAR1..6_CAP/CNTL` and later `PCIE_VF_RESIZE_BAR1..6_CAP/CNTL`, which expose BAR-size support, selected BAR index, total BAR count, selected size, and upper size-supported bits for PF/VF resizable BAR handling.
- `PCIE_PWR_BUDGET_*` and `PCIE_DPA_*`, including power-budget data selection, base-power/data-scale/PM-substate fields, DPA transition latency, power allocation scale, substate maxes, enabled substate, and per-substate power allocation registers.
- `PCIE_SECONDARY_*`, `PCIE_LINK_CNTL3`, `PCIE_LANE_ERROR_STATUS`, `PCIE_LANE_0_EQUALIZATION_CNTL` through `LANE_15_EQUALIZATION_CNTL`, `PCIE_PHY_16GT_*`, and `LANE_0_EQUALIZATION_CNTL_16GT` through `LANE_15_EQUALIZATION_CNTL_16GT`, which describe link equalization controls/status and per-lane TX preset/RX hint fields for 8 GT/s and 16 GT/s operation.
- `PCIE_MARGINING_*` and `LANE_0_MARGINING_LANE_{CNTL,STATUS}` through `LANE_15_MARGINING_LANE_{CNTL,STATUS}`, which define software margining readiness plus per-lane receiver number, margin type, usage model, and payload/status fields.

The EPF1 isolation, address-translation, and virtualization capability section covers:

- `PCIE_ACS_*` fields for source validation, translation blocking, peer-to-peer request/completion redirection, upstream forwarding, egress control, direct translated P2P, and egress vector size.
- `PCIE_ATS_*`, `PCIE_PAGE_REQ_*`, and `PCIE_PASID_*` for ATS invalidate queue and ATC enablement, PRI enable/reset/status/capacity/allocation, PASID execution/privilege support, max PASID width, and PASID enables.
- `PCIE_MC_*` multicast capability/control/address/receive/blocking fields, including translated and untranslated blocking masks.
- `PCIE_LTR_*`, `PCIE_ARI_*`, and `PCIE_SRIOV_*` fields for latency tolerance, ARI grouping/function routing, SR-IOV VF enablement, VF migration, VF memory-space enable, initial/total/active VF counts, VF stride/offset/device ID, page sizes, VF BARs, and migration-state array location.
- `PCIE_TPH_REQR_*` and `DATA_LINK_FEATURE_*` fields for TPH requester modes/table location/enablement and Data Link Feature local/remote capability exchange.

The AMD-specific EPF1 GPU IOV VSEC block is the most device-specific part of this chunk:

- `PCIE_VENDOR_SPECIFIC_*_GPUIOV` supplies the VSEC capability/header layout and an SR-IOV shadow register with `VF_EN` and `VF_NUM`.
- `GPUIOV_INTR_ENABLE` and `GPUIOV_INTR_STATUS` define per-engine virtualization event bits for GFX, UVD, UVD1, and VCE command completion, self-recovered hangs, hangs requiring FLR, VM-busy transitions, and HVVM mailbox transmit-ack/receive-valid events.
- `GPUIOV_RESET_CONTROL` exposes `SOFT_PF_FLR`.
- `GPUIOV_HVVM_MBOX_DW0..2` define the hypervisor/VF mailbox view: selected VF index, transmit/receive message data and valid/ack bits, per-VF transmit-ack/receive-valid bits for VF0 through VF30, and per-VF function-level-reset notification bits.
- `GPUIOV_CONTEXT`, `TOTAL_FB`, `OFFSETS`, `REGION`, `P2P_OVER_XGMI_ENABLE`, and `VF0_FB` through `VF30_FB` expose virtualization context, total frame-buffer accounting, region/offset selectors, peer-to-peer-over-XGMI enablement, and per-VF framebuffer size/offset fields.
- `UVDSCH_DW0..8`, `VCESCH_DW0..8`, `GFXSCH_DW0..8`, and `UVD1SCH_DW0..8` provide full-width scheduler dword fields for engine-specific GPU IOV scheduling state.

The EPF2 section starts a second endpoint-function configuration image:

- Conventional PCI header fields include vendor/device ID, command, status, revision, class codes, cache-line/latency/header/BIST, BAR1 through BAR6, CardBus CIS, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, and min/max latency.
- Power Management and PCIe base capability fields include PM capability/status-control, PCIe capability metadata, device/link capability/control/status, completion timeout, ARI/atomic/IDO/LTR/OBFF/ten-bit-tag/end-to-end-prefix controls, link target speed/retrain/compliance/de-emphasis, equalization status, and bandwidth-management status.
- MSI/MSI-X fields begin with MSI capability metadata, message control, message address/data, extended data, mask and pending registers, 64-bit variants, and the start of MSI-X capability/message-control fields.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace. The constants are preprocessor integer literals, usually with an `L` suffix, and encode only field geometry.

These macros do not express register addresses, reset values, access widths, read/write permissions, write-one-to-clear behavior, privilege requirements, ordering constraints, or firmware ownership. Those details come from companion generated files, hardware documentation, PCIe rules, firmware/BIOS initialization, and the AMDGPU access path. The direct source include for this generated header in this tree is `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, which also includes `nbio_7_2_0_offset.h` and uses the shared AMDGPU field/register helper conventions.

## Control Flow

This header has no local runtime control flow. Runtime flow is external:

1. AMDGPU, virtualization, PCIe, interrupt, reset, or diagnostic code selects an NBIO register/config offset from the companion generated offset header.
2. The code reads a hardware/config value and extracts fields with the `__SHIFT` and `_MASK` constants, or composes an updated value while preserving unrelated fields.
3. Hardware observes the resulting PCIe configuration, error-reporting, interrupt, link-training, SR-IOV, or GPU IOV state.

Likely flows represented by these fields include PCI capability enumeration, endpoint resource assignment, BAR and VF BAR sizing, MSI/MSI-X programming, AER collection/masking/clearing, PCIe link equalization and lane margining diagnostics, ACS/ATS/PRI/PASID/ARI setup, SR-IOV VF creation and resource exposure, PF/VF reset handling, hypervisor-to-VF mailbox exchange, virtual engine scheduling, and GPU IOV framebuffer partitioning.

## State And Persistence Behavior

The header owns no state and persists nothing. It names hardware-visible state in NBIO PCIe endpoint configuration and AMD GPU IOV vendor-specific registers. Persistence depends on the PCIe/config reset domain, GPU/NBIO reset, PF/VF FLR, SR-IOV enable/disable sequencing, suspend/resume save-restore, firmware initialization, hypervisor policy, and explicit driver writes.

Represented state includes static capability data, command/status bits, BAR windows, interrupt routing state, MSI/MSI-X message state, AER status/masks/severity/logs, power-budget/DPA data, link/equalization/lane-margining status, ACS/PASID/ARI/SR-IOV controls, VF counts and strides, VF BARs and resizable BAR selections, GPU IOV interrupt enables/status, mailbox handshakes, per-VF framebuffer sizes/offsets, and scheduler dwords. Some fields are ordinary configuration; others are command or latch-like state, such as FLR triggers, link retrain/compliance controls, AER status/logs, PRI reset/status, MSI pending bits, mailbox valid/ack bits, and interrupt status fields.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.2.0 register database and must stay aligned with sibling generated headers:

- `nbio_7_2_0_offset.h` supplies matching `reg...`/`cfg...` offsets and base indices for the register names in this file.
- Other NBIO 7.2.0 generated files provide related defaults or address metadata where present.
- AMDGPU helper macros consume the generated `__SHIFT`/`_MASK` convention for field composition and extraction.

Direct integration in this source tree is through `amdgpu/nbio_v7_2.c`, which includes this header while implementing NBIO 7.2 register programming for revision ID, memory-size reads, framebuffer access enablement, doorbell apertures, interrupt setup, PCIe power/clock handling, and related NBIO operations. The specific EPF1/EPF2 PCIe and GPU IOV fields in this chunk are most relevant to PCIe configuration, SR-IOV/PF/VF management, virtualization mailbox handling, interrupt delivery, AER, link diagnostics, and resource exposure.

## Risks And Edge Cases

- Generated mask or shift drift can compile cleanly while causing software to read, preserve, clear, or set the wrong hardware bit. The highest-risk families here are PCI command/BAR, MSI/MSI-X, AER, ACS/ATS/PRI/PASID, ARI/SR-IOV, FLR/reset, link control/equalization, GPU IOV mailbox, interrupt status, and VF framebuffer partition fields.
- The chunk starts and ends mid-family. The previous chunk is needed for the first `PCIE_VC_ENH_CAP_LIST` shifts/masks, and the next chunk is needed to complete `BIF_CFG_DEV0_EPF2_0_MSIX_MSG_CNTL` and later EPF2 registers.
- AER fields may be sticky or write-one-to-clear, and logs are diagnostic evidence. Treating them as normal writable storage can lose error context or fail to clear a fault.
- ACS, ATS, PRI, PASID, ARI, and SR-IOV fields affect isolation, IOMMU address translation, peer-to-peer routing, VF discovery, and VF resource visibility. Incorrect masks can create security or data-routing failures, not just probe failures.
- MSI/MSI-X address/data/mask/pending fields affect interrupt delivery. Wrong field geometry can lead to lost, repeated, or misrouted interrupts.
- Link equalization and lane margining fields interact with live PCIe PHY/link state. Polling code needs timeouts and must handle transient or non-converged status.
- GPU IOV mailbox and interrupt fields are handshake-sensitive. Incorrect valid/ack/status handling can deadlock hypervisor/VF communication or misclassify engine hangs and FLR requests.
- VF framebuffer size/offset, region, total-FB, and P2P-over-XGMI fields are resource-isolation sensitive. Incorrect values can expose overlapping memory windows or break VF memory accounting.
- Repeated per-lane, per-VF, and per-engine scheduler definitions are mechanical. A single outlier can indicate generator drift, but chunk boundaries should not be mistaken for real hardware asymmetry.

## Test Signals

- Build AMDGPU with NBIO 7.2 support enabled. Direct macro users should catch missing or renamed generated symbols.
- Run generated-header consistency checks against the authoritative NBIO 7.2.0 register database: offset-to-field pairing, shift/mask width checks, non-overlap checks within registers, EPF1/EPF2 capability continuity, and repeated lane/VF field consistency.
- PCI probe validation should confirm stable vendor/device/class/capability data, sane BAR and VF BAR sizing, correct command-bit transitions, and correct MSI/MSI-X programming.
- AER tests should validate status/mask/severity/log decoding, clear behavior, and preservation of diagnostic logs until explicitly consumed.
- Link validation should cover negotiated speed/width, 8 GT/s and 16 GT/s equalization status, lane error status, retrain behavior, and lane margining readiness/status.
- Virtualization tests should cover ACS isolation, ATS/PRI/PASID enablement, ARI routing, SR-IOV VF counts/strides/page sizes/VF BARs, VF enumeration, PF/VF FLR behavior, and suspend/resume or reset restore.
- GPU IOV tests should exercise HVVM mailbox transmit/receive valid/ack paths, per-VF FLR notifications, GFX/UVD/UVD1/VCE event interrupts, VF framebuffer partitioning, P2P-over-XGMI enablement, and scheduler dword programming.
- Register-trace reviews for any code writing these fields should verify reserved bits are preserved, W1C fields are handled intentionally, and command-like bits such as FLR, link retrain, PRI reset, and mailbox valid/ack are sequenced with polling and timeouts.
