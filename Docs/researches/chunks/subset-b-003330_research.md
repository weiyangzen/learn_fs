# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 7453-9894

## Scope

This chunk covers lines 7453-9894 of AMDGPU's generated NBIO 7.9.0 shift/mask header. It contains C preprocessor constants only: no functions, structs, enums, variables, allocations, locks, persistence code, or direct register reads/writes.

The range starts at the `BIF_CFG_DEV0_RC0_MSI_MSG_ADDR_LO__MSI_MSG_ADDR_LO_MASK` line, immediately after the matching shift definition in the previous line/chunk. It then covers PCIe configuration-space field geometry for the `BIF_CFG_DEV0_RC0_*` root-complex/root-port-style block through Gen4/Gen5 link-extension fields. The chunk then enters `addressBlock: aid_nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` and covers most of the embedded physical function 0 configuration-space image, from base PCI identity fields through the `BIF_CFG_DEV0_EPF0_0_PCIE_SRIOV_FIRST_VF_OFFSET__SRIOV_FIRST_VF_OFFSET__SHIFT` line. The matching first-VF-offset mask and the rest of the SR-IOV register set continue after this chunk.

Although this repository path is under a `ceph-client` mirror, the content is AMD GPU NBIO/PCIe register metadata. There is no Ceph or distributed-filesystem runtime behavior in this file section.

## Purpose

`nbio_7_9_0_sh_mask.h` is the generated bitfield-definition companion for NBIO 7.9.0 registers. Each exported macro provides one piece of hardware field geometry:

- `REGISTER__FIELD__SHIFT`: the least-significant bit index of a field.
- `REGISTER__FIELD_MASK`: the bit mask for the field inside the containing register.

Driver code combines these definitions with `nbio_7_9_0_offset.h` register addresses, reset/default headers, and AMDGPU register helper macros such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`. The header lets NBIO and PCIe code use symbolic field names instead of hard-coded bit positions when decoding or composing PCI configuration-space and NBIO register values.

This chunk is primarily a PCIe capability-surface map. It describes MSI, subsystem/vendor-specific capabilities, virtual channels, device serial number, AER, secondary PCIe capability, per-lane equalization, ACS, data link feature, 16 GT/s and 32 GT/s link extensions, EPF0 standard PCI header fields, EPF0 PM/PCIe/MSI/MSI-X capability fields, EPF0 resizable BAR and power/DPA fields, ATS/PRI/PASID, multicast, LTR, ARI, and the beginning of EPF0 SR-IOV.

## Important Macro Families

### RC0 MSI, SSID, Vendor-Specific, and Virtual Channel Fields

The opening lines finish part of the `BIF_CFG_DEV0_RC0_MSI_MSG_ADDR_LO` field set and then define RC0 MSI address/data fields:

- `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, `MSI_EXT_MSG_DATA`, `MSI_MSG_DATA_64`, and `MSI_EXT_MSG_DATA_64` provide 32-bit and 64-bit message-address/data encodings.
- `SSID_CAP_LIST` and `SSID_CAP` expose capability ID, next pointer, subsystem vendor ID, and subsystem ID fields.
- `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, and scratch VSEC words provide PCIe vendor-specific enhanced capability metadata.
- `PCIE_VC_ENH_CAP_LIST`, `PCIE_PORT_VC_CAP_REG1/2`, `PCIE_PORT_VC_CNTL`, `PCIE_PORT_VC_STATUS`, and VC0/VC1 resource capability/control/status registers encode virtual-channel count, arbitration tables, TC-to-VC maps, VC IDs, enable bits, and negotiation/status bits.

These root-complex-style fields describe the PCIe configuration image that software or firmware may expose for the RC0 function. The MSI and VC fields are not executable APIs; they are masks used by code that reads or programs those PCIe capability registers.

### RC0 Device Serial Number and AER

The RC0 device serial number and advanced error reporting block includes:

- `PCIE_DEV_SERIAL_NUM_ENH_CAP_LIST`, `PCIE_DEV_SERIAL_NUM_DW1`, and `PCIE_DEV_SERIAL_NUM_DW2`.
- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`.
- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY`.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK`.
- `PCIE_ADV_ERR_CAP_CNTL`, `PCIE_HDR_LOG0..3`, `PCIE_ROOT_ERR_CMD`, `PCIE_ROOT_ERR_STATUS`, `PCIE_ERR_SRC_ID`, and `PCIE_TLP_PREFIX_LOG0..3`.

The uncorrectable-error groups cover PCIe error bits such as data-link-protocol error, surprise down, poisoned TLP, flow-control protocol error, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC error, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic-op egress blocked, TLP prefix blocked, and poisoned-TLP egress blocked. The same conceptual bit positions recur across status, mask, and severity registers, but their semantics differ: one reports/clears state, one suppresses reporting, and one classifies severity.

The correctable-error groups include receiver error, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal, correctable internal error, header-log overflow, and integer-error status or mask fields. Header-log and TLP-prefix-log fields are full-width diagnostic words.

### RC0 Secondary PCIe, Lane Equalization, ACS, DLF, and High-Speed Link Extensions

The RC0 secondary PCIe capability portion defines:

- `PCIE_SECONDARY_ENH_CAP_LIST`, `PCIE_LINK_CNTL3`, and `PCIE_LANE_ERROR_STATUS`.
- `PCIE_LANE_0_EQUALIZATION_CNTL` through `PCIE_LANE_15_EQUALIZATION_CNTL`, each with downstream-port TX preset, downstream-port RX preset hint, upstream-port TX preset, and upstream-port RX preset hint fields.
- `PCIE_ACS_ENH_CAP_LIST`, `PCIE_ACS_CAP`, and `PCIE_ACS_CNTL`.
- `PCIE_DLF_ENH_CAP_LIST`, `DATA_LINK_FEATURE_CAP`, and `DATA_LINK_FEATURE_STATUS`.
- `PCIE_PHY_16GT_ENH_CAP_LIST`, `LINK_CAP_16GT`, `LINK_CNTL_16GT`, `LINK_STATUS_16GT`, local/RTM parity mismatch status registers, and per-lane `LANE_N_EQUALIZATION_CNTL_16GT` fields.
- `PCIE_MARGINING_ENH_CAP_LIST`, margining port capability/status, lane 0-15 margining control/status registers, and `LINK_CAP_32GT`, `LINK_CNTL_32GT`, `LINK_STATUS_32GT`.

These macros represent PCIe link-training and diagnostic surfaces. The regular lane-equalization groups are repetitive by lane and must remain lane-number aligned. The 16 GT/s block captures Gen4-style equalization completion/phase status, retimer presence, link equalization requests, and per-lane preset coefficients. The 32 GT/s block captures Gen5-style equalization bypass, modified TS usage, lane equalization controls, equalization phase status, link-flap status, precoding status, and downstream/upstream component presence.

ACS capability/control fields are security and routing sensitive: source validation, translation blocking, P2P request/completion redirect, upstream forwarding, egress control, direct translated P2P, and egress vector behavior affect peer-to-peer DMA and IOMMU isolation assumptions.

### EPF0 Base PCI Header and PM/PCIe Capabilities

The `aid_nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` address block starts in this chunk and maps the embedded physical function 0 PCI configuration-space image. The base header fields include:

- `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS`.
- `COMMAND` and `STATUS`, covering I/O enable, memory enable, bus master enable, special cycle, write-and-invalidate, VGA snoop, parity-response enable, stepping, SERR enable, fast-back enable, interrupt disable, capability-list status, interrupt status, DEVSEL timing, abort, parity, and system-error status bits.
- `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, `BASE_ADDR_1..6`, `CARDBUS_CIS_PTR`, `ADAPTER_ID`, `ROM_BASE_ADDR`, `CAP_PTR`, interrupt line/pin, `MIN_GRANT`, and `MAX_LATENCY`.
- Vendor capability and adapter ID write-alias fields.

The PM capability block includes `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`. These expose PCI PM capability metadata, supported D-states, PME support, current power state, no-soft-reset behavior, PME enable/status, data select/scale, bus power/clock control, B2/B3 support, and PM data fields.

The EPF0 PCIe capability block includes `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`. These fields describe endpoint/device type, payload and request sizes, error-reporting enables/status, relaxed ordering, no-snoop, extended tags, FLR, emergency power reduction, link speeds/widths, ASPM and link-management controls, data-link-active reporting, bandwidth notifications, completion-timeout policy, ARI/atomic/IDO/LTR/OBFF/10-bit-tag/TLP-prefix support, target link speed, compliance/deemphasis settings, equalization phase status, retimer presence, crosslink status, and DRS message receipt.

### EPF0 MSI, MSI-X, Vendor-Specific, VC, Serial Number, and AER

EPF0 interrupt-related capability fields include:

- `MSI_CAP_LIST`, `MSI_MSG_CNTL`, `MSI_MSG_ADDR_LO/HI`, 32-bit and 64-bit message data, extended data, mask, and pending fields.
- `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`, with table size, function mask, MSI-X enable, BIR, and table/PBA offset fields.

The EPF0 vendor-specific and virtual-channel groups mirror the RC0 capability families, using the `BIF_CFG_DEV0_EPF0_0_*` prefix and the EPF0 offset range. The same caveats apply: VSEC capability IDs, versions, lengths, next pointers, scratch words, VC arbitration fields, TC-to-VC maps, VC IDs, enable bits, and negotiation status are field geometry only.

EPF0 also has its own device serial number and AER block:

- `PCIE_DEV_SERIAL_NUM_ENH_CAP_LIST`, serial number low/high words.
- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, uncorrectable status/mask/severity, correctable status/mask, advanced error capability/control, header logs, and TLP prefix logs.

Unlike RC0, the EPF0 AER portion in this chunk does not include root error command/status or error source ID fields, which are root-port-specific in the RC0 section.

### EPF0 Resizable BAR, Power Budget, DPA, Secondary PCIe, and Lane Equalization

The EPF0 resizable BAR extended capability defines `PCIE_BAR_ENH_CAP_LIST` plus BAR1 through BAR6 capability/control pairs:

- `BAR_SIZE_SUPPORTED` fields advertise supported sizes.
- `BAR_INDEX`, `BAR_TOTAL_NUM`, `BAR_SIZE`, and `BAR_SIZE_SUPPORTED_UPPER` fields select and control resizable BAR size information.

The power budget and dynamic power allocation fields include `PCIE_PWR_BUDGET_ENH_CAP_LIST`, data select/data/capability registers, `PCIE_DPA_ENH_CAP_LIST`, DPA capability, latency indicator, status/control, and substate power allocation registers 0 through 7. These fields are part of the PCIe power-management surface exposed by the device.

EPF0 secondary PCIe and per-lane equalization definitions mirror the RC0 structure: secondary enhanced capability header, link control 3, lane error status, and lane 0-15 equalization control fields. This gives software symbolic masks for EPF0 link training, error visibility, and equalization preset programming/status decode.

### EPF0 ACS, ATS, PRI, PASID, Multicast, LTR, ARI, and SR-IOV Start

The later EPF0 portion covers isolation, address translation, virtualization, and latency reporting capabilities:

- `PCIE_ACS_ENH_CAP_LIST`, `PCIE_ACS_CAP`, and `PCIE_ACS_CNTL` define ACS support and control bits for source validation, translation blocking, P2P request/completion redirect, upstream forwarding, egress control, direct translated P2P, and egress vector capacity/control.
- `PCIE_ATS_ENH_CAP_LIST`, `PCIE_ATS_CAP`, and `PCIE_ATS_CNTL` cover ATS invalidation queue depth, page-aligned requests, global invalidation support, relaxed ordering support, STU, and ATC enable.
- `PCIE_PAGE_REQ_ENH_CAP_LIST`, `PCIE_PAGE_REQ_CNTL`, `PCIE_PAGE_REQ_STATUS`, `PCIE_OUTSTAND_PAGE_REQ_CAPACITY`, and `PCIE_OUTSTAND_PAGE_REQ_ALLOC` represent PRI/page-request enable/reset, response failure, unexpected page-request group/index, stopped status, PASID-required status, and outstanding request capacity/allocation.
- `PCIE_PASID_ENH_CAP_LIST`, `PCIE_PASID_CAP`, and `PCIE_PASID_CNTL` describe PASID execute permission, privileged mode, max PASID width, and enable bits.
- `PCIE_MC_ENH_CAP_LIST`, `PCIE_MC_CAP`, `PCIE_MC_CNTL`, multicast address, receive, block-all, and untranslated-block fields describe PCIe multicast support and filtering.
- `PCIE_LTR_ENH_CAP_LIST` and `PCIE_LTR_CAP` expose maximum snoop and no-snoop latency values and scales.
- `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL` expose ARI function-group support/enables, function group selection, and next function number.
- `PCIE_SRIOV_ENH_CAP_LIST`, `PCIE_SRIOV_CAP`, `PCIE_SRIOV_CONTROL`, `PCIE_SRIOV_STATUS`, `PCIE_SRIOV_INITIAL_VFS`, `PCIE_SRIOV_TOTAL_VFS`, `PCIE_SRIOV_NUM_VFS`, `PCIE_SRIOV_FUNC_DEP_LINK`, and the first line of `PCIE_SRIOV_FIRST_VF_OFFSET` begin the SR-IOV capability field set.

The SR-IOV fields are privilege and resource sensitive. This chunk includes VF migration capability/status, ARI hierarchy preservation/control, VF 10-bit tag support/enable, VF enable, VF migration enable/interrupt enable, VF memory-space enable, initial/total/active VF counts, function dependency link, and the shift for first VF offset. The first-VF-offset mask plus VF stride, VF device ID, supported/system page size, VF BARs, and migration-state-array fields are outside this exact range.

## APIs, Types, and Functions

There are no callable APIs, C types, or functions in this chunk. The exported interface is the generated macro namespace. Consumer code includes this header together with `nbio_7_9_0_offset.h` and uses field helper macros to isolate or compose values.

The file supplies field geometry only. It does not encode reset values, register offsets, read/write permissions, reserved-bit policy, write-one-to-clear behavior, side effects, firmware ownership, ordering requirements, or polling/timeout rules. Those semantics come from the matching offset/default headers, AMDGPU NBIO code, PCIe specification semantics, firmware policy, and ASIC documentation.

AMDGPU NBIO 7.9 code includes this header in files such as `drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c` and NBIO RAS support. The visible NBIO 7.9 implementation uses generated masks for register-field composition and extraction through `REG_GET_FIELD` and `REG_SET_FIELD`, while this chunk's PCIe configuration macros are part of the same generated field namespace.

## Control Flow

This header has no local runtime control flow. Runtime use is external and generally follows this pattern:

1. Driver, firmware-facing, or diagnostic code selects an NBIO 7.9 register offset from `nbio_7_9_0_offset.h`.
2. It reads or prepares a register value through the appropriate AMDGPU access path, PCI configuration-space path, or generated SOC15 helper.
3. It extracts a field with `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`, or uses a read-modify-write helper that preserves unrelated bits.
4. Hardware applies the relevant PCIe/NBIO behavior: interrupt delivery, capability advertisement, link training, AER reporting, ACS routing/isolation, ATS/PRI/PASID translation services, multicast filtering, LTR reporting, ARI function enumeration, SR-IOV VF enumeration, or resource sizing.

The order in this file follows the generated register database and PCI capability layout. It is not an execution sequence. Repeated status, mask, severity, and control bit names can share positions while requiring different software handling.

## State and Persistence Behavior

The chunk owns no software state and persists nothing. It names fields whose state lives in NBIO hardware registers or the PCIe configuration-space image for RC0 and EPF0. Persistence depends on PCIe reset rules, GPU/NBIO reset domains, function-level reset, firmware initialization, runtime power management, suspend/resume restore, SR-IOV state transitions, and explicit driver writes.

Represented state includes:

- Configuration state: PCI command bits, BAR and ROM BAR values, MSI/MSI-X enables/masks/address/data, PM state, PME enable, PCIe device/link controls, VC controls, AER masks/severity, ACS controls, ATS/PRI/PASID enables, multicast controls, ARI controls, DPA controls, resizable BAR controls, and SR-IOV VF enable/count controls.
- Capability and identity state: vendor/device/class IDs, capability IDs and next pointers, subsystem IDs, VSEC metadata, device serial number, PCIe device/link capabilities, VC capabilities, AER capabilities, resizable BAR support, power budget and DPA capabilities, ACS/ATS/PRI/PASID capabilities, multicast/LTR/ARI capabilities, and SR-IOV capability fields.
- Status and diagnostic state: PCI status, PM/PME status, PCIe device/link status, VC status, AER correctable/uncorrectable status, header logs, TLP prefix logs, lane error status, per-lane equalization status, data link feature exchange status, 16 GT/s and 32 GT/s link/equalization/parity status, PRI status, SR-IOV migration status, and MSI pending bits.

Callers must distinguish writable controls from read-only capabilities, sticky/W1C status bits from ordinary status, command-like bits from persistent configuration, and reserved bits from valid fields. The mask names alone do not provide those behavioral rules.

## Dependencies and Integration Points

This chunk depends on the generated NBIO 7.9.0 register-header set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_offset.h` supplies matching `regBIF_CFG_DEV0_RC0_*` and `regBIF_CFG_DEV0_EPF0_0_*` offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_default.h`, where present, supplies generated default/reset values.
- AMDGPU NBIO 7.9 source, RAS source, SOC15 register helpers, and PCI/NBIO code consume the shift/mask naming convention when building and decoding register values.

Practical integration points include:

- GPU PCIe enumeration and capability-chain decoding for RC0 and EPF0.
- Interrupt setup and diagnostics through MSI/MSI-X fields.
- PCIe link management, equalization, margining, high-speed link extension status, retimer/precoding visibility, and lane error diagnostics.
- AER diagnostics and recovery, including uncorrectable/correctable status, masks, severity, header logs, TLP prefix logs, and root-port reporting fields for RC0.
- Resource sizing and exposure through EPF0 BARs, resizable BAR registers, and ROM BAR fields.
- Power management through PCI PM, LTR, power budget, and DPA fields.
- IOMMU, peer-to-peer DMA, VFIO, and virtualization behavior through ACS, ATS, PRI, PASID, ARI, multicast, and SR-IOV fields.
- GPU reset and SR-IOV transitions where PF/VF configuration, VF enablement, VF counts, and memory-space enable state must be preserved, restored, or intentionally reinitialized.

## Risks and Edge Cases

- The range starts and ends mid-register. `BIF_CFG_DEV0_RC0_MSI_MSG_ADDR_LO__MSI_MSG_ADDR_LO__SHIFT` is on the previous line, and `BIF_CFG_DEV0_EPF0_0_PCIE_SRIOV_FIRST_VF_OFFSET__SRIOV_FIRST_VF_OFFSET_MASK` is on the next line after this chunk. The merge lane must reconcile adjacent chunks before describing those registers as complete.
- Bitfield drift is high impact. A wrong shift or mask can compile cleanly while decoding the wrong PCIe bit, corrupting adjacent fields, breaking MSI/MSI-X setup, misadvertising capabilities, changing link behavior, or writing reserved bits.
- AER status, mask, and severity registers intentionally reuse many field names and bit positions. Copying handling between them can accidentally clear diagnostics, suppress errors, or change fatal/non-fatal classification.
- PCI status, device/link status, AER status, lane error status, PRI status, SR-IOV migration status, MSI pending bits, and similar fields can be sticky, W1C, or side-effectful depending on the hardware specification. Generic read-modify-write operations can lose diagnostics.
- ACS, ATS, PRI, PASID, ARI, multicast, and SR-IOV fields are virtualization and isolation sensitive. Incorrect masks can affect IOMMU group isolation, peer DMA routing, VF enumeration, address translation, page-request behavior, and passthrough assumptions.
- MSI and MSI-X address/data/mask/pending fields overlap in the PCI capability layout depending on 32-bit versus 64-bit forms. Callers must use the capability control bits and matching offsets; the masks alone do not enforce layout selection.
- Repeated lane 0-15 equalization and margining groups are copy-error prone. Prefix or lane-number mix-ups may compile if the target macro exists but decode or program the wrong lane.
- RC0 and EPF0 define many similar capability names under different prefixes and offset ranges. Prefix mix-ups can target the wrong PCIe function or root-complex image.
- Resizable BAR and SR-IOV resource fields affect memory aperture sizing and VF layout. Incorrect writes can break PCI enumeration, VF BAR placement, firmware resource accounting, or guest-visible device configuration.
- High-speed 16 GT/s and 32 GT/s link extension fields are generation-specific. Treating them like older PCIe link fields can misread equalization, retimer, precoding, or link-flap state.
- The header provides masks and shifts, not access ordering. Link retrain/equalization, FLR, SR-IOV enablement, PRI reset, and mailbox-like fields in nearby capability spaces require sequencing and timeout policy from driver or hardware documentation.

## Test Signals

- Build AMDGPU configurations that include NBIO 7.9.0 support. Compile failures catch malformed generated symbols or mismatches between generated headers and driver users.
- Run generated-header consistency checks against the authoritative NBIO 7.9.0 register database: every field should have the expected shift and mask, every register in this chunk should have a matching offset, and defaults should align where generated.
- Cross-check `BIF_CFG_DEV0_RC0_*` and `BIF_CFG_DEV0_EPF0_0_*` repeated capability families for expected common layouts and intentional root-port-versus-endpoint differences, especially AER root-error fields and SR-IOV-only endpoint fields.
- Validate PCIe enumeration on matching hardware with tools such as `lspci -vv`: vendor/device/class IDs, BARs, PM/PCIe/MSI/MSI-X/AER/ACS/ATS/PRI/PASID/LTR/ARI/SR-IOV capability chains, link capabilities, and resizable BAR information should decode coherently.
- Exercise MSI and MSI-X setup paths, interrupt masking/unmasking, and pending-bit diagnostics to catch address/data/mask field mismatches.
- Exercise PCIe link behavior at supported speeds: negotiated speed/width, link retraining, equalization phase status, per-lane equalization controls, lane error reporting, 16 GT/s parity/equalization status, 32 GT/s retimer/precoding/link-flap status, and margining status where available.
- Exercise AER paths where hardware and platform support allow: correctable/uncorrectable status, mask/severity policy, header logs, TLP prefix logs, root-port error command/status/source IDs for RC0, and clearing behavior.
- Validate ACS/IOMMU and peer-to-peer DMA behavior on systems exposing these registers, especially for VFIO or passthrough deployments.
- Validate ATS/PRI/PASID operation with IOMMU-enabled workloads where supported: translation enablement, page request capacity/allocation, response-failure status, PASID width, and PASID privilege/execute permission behavior.
- Validate SR-IOV transitions on supported devices: initial/total/active VF counts, VF enable, VF memory-space enable, ARI hierarchy, first VF offset continuity with the following chunk, and reset/suspend/resume restoration.
- Run suspend/resume and GPU reset recovery tests to verify hardware state represented by these masks is restored or intentionally reinitialized according to AMDGPU policy.
