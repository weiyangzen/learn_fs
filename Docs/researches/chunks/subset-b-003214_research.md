# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 131175-133632

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.2.0 register field mask header. It defines C preprocessor constants for bit shifts and masks in NBIO/PCIe configuration-space registers. The range is not executable code; it is a hardware layout contract used by driver code that reads, decodes, or composes PCIe/NBIO register values for this ASIC generation.

The slice has two main regions. It begins in the tail of `BIF_CFG_DEV2_RC1`, a root-complex/root-port style PCIe capability block, covering lane equalization, Access Control Services, Data Link Feature, 16 GT/s PHY, and lane margining fields. It then switches at the `addressBlock: nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` marker to the start of the `BIF_CFG_DEV0_EPF0_1` endpoint-function PCI configuration block. That endpoint block runs from conventional PCI header fields through standard PCI/PCIe capabilities, PCIe enhanced capabilities, SR-IOV, lane training/margining, VF resizable BAR, and the first GPUIOV vendor-specific capability-list fields.

These definitions pair with generated register offset headers, especially the matching NBIO 7.2.0 offset file. Offsets identify where a register is located; this header identifies how each named field is packed inside the register.

## Major Register Groups

The `BIF_CFG_DEV2_RC1` section starts mid-register with the remaining masks for `PCIE_LANE_11_EQUALIZATION_CNTL`, then completes `PCIE_LANE_12_EQUALIZATION_CNTL` through `PCIE_LANE_15_EQUALIZATION_CNTL`. Each lane's 8 GT/s equalization control exposes downstream and upstream transmit presets plus receive preset hints using the same four nibble-sized fields.

The following `DEV2_RC1` enhanced capability blocks define:

- `PCIE_ACS_ENH_CAP_LIST`, `PCIE_ACS_CAP`, and `PCIE_ACS_CNTL` for Access Control Services capability metadata and enable bits such as source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, egress control, and direct translated P2P.
- `PCIE_DLF_ENH_CAP_LIST`, `DATA_LINK_FEATURE_CAP`, and `DATA_LINK_FEATURE_STATUS` for data-link feature capability metadata, locally supported features, remote supported features, exchange enablement, and validity state.
- `PCIE_PHY_16GT_ENH_CAP_LIST`, `LINK_CAP_16GT`, `LINK_CNTL_16GT`, `LINK_STATUS_16GT`, and local/retimer parity mismatch status registers for PCIe 4.0 16 GT/s capability reporting, equalization completion, per-phase equalization success, link equalization request, and parity mismatch diagnostics.
- `LANE_0_EQUALIZATION_CNTL_16GT` through `LANE_15_EQUALIZATION_CNTL_16GT`, each carrying downstream-port and upstream-port 16 GT/s transmit preset fields.
- `PCIE_MARGINING_ENH_CAP_LIST`, `MARGINING_PORT_CAP`, `MARGINING_PORT_STATUS`, and `LANE_0_MARGINING_LANE_CNTL/STATUS` through `LANE_15_MARGINING_LANE_CNTL/STATUS` for PCIe lane margining control/status. The per-lane control fields encode receiver number, margin type, usage model, and payload. The status mirrors those concepts for returned margining status.

The `BIF_CFG_DEV0_EPF0_1` address block starts with conventional PCI configuration header fields:

- Identity and class-code fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS`.
- Command/status and header operation fields: `COMMAND`, `STATUS`, `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, `CAP_PTR`, interrupt line/pin, minimum grant, and maximum latency.
- BAR and ROM decode fields: `BASE_ADDR_1` through `BASE_ADDR_6`, `ROM_BASE_ADDR`, and `CARDBUS_CIS_PTR`.
- Adapter and vendor capability fields: `ADAPTER_ID`, `VENDOR_CAP_LIST`, and `ADAPTER_ID_W`.

The standard and PCIe capability areas include:

- Power Management Interface: `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`, with version, PME clock/DSI/D1/D2 support, auxiliary current, PME support, power state, no-soft-reset, PME enable/status, B2/B3 support, data select/scale, and bridge extension fields.
- PCIe capability: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, plus `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`. These cover device/port type, slot implementation, MSI interrupt message number, payload sizes, error-report enables, relaxed ordering, no-snoop, max read request, function level reset, link speed/width, ASPM, retrain/common-clock/extended-sync controls, target link speed, equalization controls, and equalization status.
- MSI/MSI-X: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, message address/data/mask/pending fields including 64-bit variants, `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`.

The endpoint enhanced capabilities in this chunk include:

- Vendor-specific capability list/header and two early vendor-specific data registers.
- Virtual Channel capability and resource controls for VC0/VC1.
- Device serial number registers.
- Advanced Error Reporting: uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, header logs, and TLP prefix logs.
- Resizable BAR for physical function BAR1 through BAR6, including supported sizes, selected size, BAR index, and total BAR count fields.
- Power Budgeting and Dynamic Power Allocation capability/control/status/substate allocation fields.
- Secondary PCIe capability, lane error status, and 8 GT/s lane equalization control for lanes 0 through 15.
- ACS, ATS, Page Request Interface, PASID, Multicast, Latency Tolerance Reporting, Alternative Routing-ID Interpretation, SR-IOV, TPH requester, Data Link Feature, 16 GT/s PHY, 16 GT/s lane equalization, lane margining, and VF Resizable BAR capabilities.
- The final visible group begins `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST_GPUIOV`, providing the GPUIOV vendor-specific enhanced capability ID/version/next-pointer masks. The next register group starts after this requested range.

## Important APIs, Types, And Functions

There are no functions, structs, enums, or runtime APIs in this chunk. The public interface consists of generated macros with two naming patterns:

- `REGISTER__FIELD__SHIFT`: the bit position of a field inside the register.
- `REGISTER__FIELD_MASK`: the bitmask covering the field inside the register.

Driver consumers combine these constants with register offsets and register-access helpers. A typical consumer reads a 16-bit or 32-bit PCIe/NBIO register, extracts a field with `(value & FIELD_MASK) >> FIELD__SHIFT` or a local AMDGPU helper macro such as `REG_GET_FIELD`, and composes writable fields by clearing `FIELD_MASK` and OR-ing the shifted field value before writing back.

The exact macro names are part of the compile-time API for NBIO 7.2.0 register code. Compatibility depends on generated names remaining synchronized with AMD's hardware register database and with call sites that include this header.

## Control Flow

This header adds no control flow by itself. Runtime control flow occurs in AMDGPU code that uses these constants while enumerating capabilities, initializing PCIe/NBIO state, handling reset, or diagnosing link and error conditions.

A representative decode path is:

1. ASIC-specific code selects NBIO 7.2.0 headers for the detected GPU.
2. The driver reads a PCI config, MMIO, or indirect NBIO register using an offset from the matching offset header.
3. The masks and shifts in this header decode capability, status, error, or control fields.
4. For writable controls, the driver performs a read-modify-write sequence that preserves unrelated and reserved bits.

For link-management paths, fields such as target link speed, link width, equalization request/status, per-lane 8 GT/s and 16 GT/s presets, lane error status, data-link feature exchange, and margining status influence higher-level decisions in code outside this header. For virtualization paths, SR-IOV, VF BAR, PASID, ATS, PRI, ARI, and GPUIOV-related capability fields feed enumeration, capability advertisement, interrupt routing, and function configuration code.

## State And Persistence

The file itself is immutable compile-time metadata and stores no runtime state.

The represented state lives in NBIO/PCIe hardware registers. Some fields describe static or firmware-programmed capabilities, including capability IDs, versions, next pointers, supported speeds, max payload/read-request limits, ACS/ATS/PASID/PRI support, SR-IOV totals, VF BAR size support, DPA support, TPH requester support, data-link feature support, and lane margining capability. Other fields describe live hardware state, such as command enables, status/error bits, negotiated link speed/width, equalization completion, margining results, MSI/MSI-X enablement, AER logs, and SR-IOV configured VF counts.

Writable fields persist only as hardware register contents within the relevant reset and power domain. PCI reset, GPU reset, FLR, suspend/resume, or firmware reinitialization can reset or rewrite command/control registers, BAR sizing state, MSI/MSI-X setup, AER masks/severity, ACS controls, SR-IOV controls, VF BAR controls, and link controls. Sticky status fields may retain error information until cleared according to hardware-defined semantics; this header identifies bit positions but does not encode clear-on-read or write-one-to-clear behavior.

## Dependencies And Integration Points

The direct dependency is the generated NBIO 7.2.0 register offset mapping. The masks in this chunk are only meaningful when applied to the corresponding register addresses. The same generated naming style also assumes AMDGPU's ASIC register include conventions and helper macros.

Important integration points include:

- AMDGPU NBIO initialization and device-discovery paths that select `asic_reg/nbio/nbio_7_2_0_*` headers.
- PCI/PCIe config-space access code for endpoint function `DEV0_EPF0_1`, including BAR probing, capability-list walking, power management setup, MSI/MSI-X configuration, and PCIe capability decoding.
- PCIe link-management and diagnostics paths that decode link speed/width, ASPM, equalization, lane error, 16 GT/s PHY, retimer parity, Data Link Feature, and lane margining registers.
- RAS, AER, and reset/recovery paths that use correctable and uncorrectable error masks/status/severity, AER header/TLP-prefix logs, and PCIe status bits.
- IOMMU and virtualization-related flows that depend on ACS, ATS, PRI, PASID, ARI, SR-IOV, VF BAR, TPH requester, multicast, and GPUIOV capability fields.
- Power and performance management paths that inspect or program PMI, Power Budgeting, DPA, LTR, and device/link control fields.

The repeated lane and BAR families are source-tree aligned with corresponding AMDGPU PCIe/NBIO code rather than Ceph filesystem logic despite the repository path prefix. The path indicates a vendored or mirrored Linux driver tree under `sources/distributed-fs/ceph-client`, but the file content is AMD GPU register metadata.

## Risks

The primary risk is silent misdecode or misprogramming if a mask or shift is wrong. Because these constants are used near hardware, an incorrect bit can enable the wrong PCI command, advertise a capability incorrectly, fail to mask an AER condition, corrupt link-control state, select the wrong BAR size, or report the wrong SR-IOV/VF property.

The slice is highly repetitive. Per-lane equalization and margining fields repeat across lanes 0 through 15, and BAR/VF BAR fields repeat across BAR1 through BAR6. Generation or merge mistakes can affect only one lane or one BAR, producing failures that only appear with particular link widths, negotiated speeds, function configurations, or virtualization setups.

Mixed register widths are another hazard. Conventional PCI and PCIe config fields include 8-bit, 16-bit, and 32-bit concepts, but the macros are plain constants. Consumers must use the correct access width and preserve reserved bits. Applying a 32-bit write where a narrower config-space access is required, or clearing a reserved bit during read-modify-write, can cause hardware-visible side effects.

This header does not encode access semantics. Some hardware status fields are sticky, write-one-to-clear, reserved, read-only, or controlled by firmware. Code that treats every mask as freely writable can lose diagnostics or perturb PCIe link state.

The requested chunk starts and ends in the middle of larger generated groups: it begins with remaining lane 11 equalization masks and ends after GPUIOV capability-list masks. The reconciliation lane should preserve this boundary information so neighboring chunk reports are not assumed to contain complete file-level coverage on their own.

## Test Signals

Useful validation is mostly build-time and hardware/integration-facing:

- Kernel or module builds that include NBIO 7.2.0 headers complete without missing or duplicate macro-name issues.
- Capability walking on affected AMD GPUs reports coherent PCIe, ACS, ATS, PRI, PASID, ARI, SR-IOV, Resizable BAR, VF Resizable BAR, DLF, 16 GT/s PHY, lane margining, and GPUIOV capability chains, with valid `CAP_ID`, `CAP_VER`, and `NEXT_PTR` fields.
- `lspci -vv`, kernel PCIe logs, and AMDGPU debug output agree on device/link capabilities, negotiated link speed and width, MSI/MSI-X state, BAR sizing, power-management capabilities, AER status, and SR-IOV/VF properties.
- Link training/retraining tests show expected 8 GT/s and 16 GT/s equalization status, no lane swaps in per-lane preset fields, and plausible lane error/margining results across x1/x4/x8/x16 configurations.
- AER/RAS/fault-injection tests decode correctable and uncorrectable error status, masks, severity, header logs, and TLP prefix logs consistently with hardware documentation and Linux PCIe AER reporting.
- Virtualization tests exercise ACS isolation, ATS/PRI/PASID enablement, ARI routing, SR-IOV VF count and stride fields, VF BAR sizing, TPH requester controls, and GPUIOV discovery without regressions.
- Reset, FLR, suspend/resume, and GPU reset paths reinitialize writable command/control, link, MSI/MSI-X, AER, ACS, SR-IOV, BAR, VF BAR, and power-management fields as expected.
