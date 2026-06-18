# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 14863-17300

## Scope

This chunk covers a generated AMD NBIO 7.7.0 register shift/mask header segment. It starts in the `BIF_CFG_DEV1_EPF0_PMI_STATUS_CNTL` field definitions, covers the rest of the `BIF_CFG_DEV1_EPF0_*` PCIe endpoint-function capability block, then enters the `nbio_pcie0_bifplr0_cfgdecp` address block and covers `BIFPLR0_*` PCIe bridge/root-port configuration and extended-capability fields through the `BIFPLR0_LANE_6_MARGINING_LANE_CNTL` register comment. The actual lane 6 margining field definitions continue in the next chunk.

The range contains 2,156 preprocessor `#define`s. They are almost entirely paired field definitions:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset of a field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or compose that field.

There are no C functions, structs, variables, executable statements, allocation paths, or software-owned persistent objects in this chunk.

## Purpose

The purpose of this header section is to provide the bit-level ABI between AMDGPU NBIO 7.7.0 driver code and the ASIC's PCIe/NBIO configuration registers. The sibling `nbio_7_7_0_offset.h` header supplies register addresses such as `cfgBIF_CFG_DEV1_EPF0_0_PCIE_CAP`, `cfgBIF_CFG_DEV1_EPF0_0_MSIX_TABLE`, and `cfgBIFPLR0_PCIE_ADV_ERR_RPT_ENH_CAP_LIST`; this file supplies field positions and masks for those register values.

Driver code includes this header through `amdgpu/nbio_v7_7.c` and uses the wider generated-header convention with helpers such as `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and `SOC15_REG_OFFSET`. This particular chunk is mostly a declarative map for PCIe configuration-space layout and hardware status/control bits, so its value is correctness of encoded bit positions rather than runtime behavior in the header itself.

## Important Macro Families

### Endpoint Function PCIe Capability Fields

The opening `BIF_CFG_DEV1_EPF0_*` block describes device/function PCIe configuration-space capabilities for device 1 endpoint function 0. It includes:

- `PCIE_CAP_LIST` and `PCIE_CAP`, carrying standard capability IDs, next pointers, PCIe capability version, device type, slot-implemented bit, and interrupt message number.
- `DEVICE_CAP` and `DEVICE_CNTL`, covering maximum payload support/selection, phantom functions, extended tags, relaxed ordering, no-snoop, auxiliary power management, error-reporting enables, max read request size, and function-level reset initiation.
- `LINK_CAP` and `LINK_STATUS`, covering supported/current link speed, supported/negotiated link width, ASPM/PM support, L0s/L1 exit latency, link training, slot clock, data-link active, bandwidth-management status, and port number.

These fields mirror PCIe capability register semantics. They are used by driver and platform code to decode the device's negotiated PCIe state and to compose writes when enabling features such as error reporting, no-snoop, payload size, read request size, or FLR.

### MSI and MSI-X

The endpoint block defines MSI/MSI-X capability list fields and interrupt table metadata:

- `MSI_CAP_LIST`, `MSI_MSG_ADDR_LO`, `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, `MSI_MSG_DATA_64`, `MSI_PENDING`, and `MSI_PENDING_64`.
- `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`.

Important fields include MSI message address/data, pending bits, MSI-X table size, function mask, MSI-X enable, table BAR indicator, table offset, PBA BAR indicator, and PBA offset. Incorrect offsets or masks here would directly affect interrupt delivery setup and diagnostics for PCIe MSI/MSI-X capability state.

### Vendor, Virtual Channel, BAR, and Power Capabilities

The endpoint function also exposes PCIe extended capabilities for vendor-specific state, virtual channels, BAR sizing, power budgeting, and dynamic power allocation:

- `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, and `PCIE_VENDOR_SPECIFIC2`.
- `PCIE_VC_ENH_CAP_LIST`, `PCIE_PORT_VC_CAP_REG1/2`, `PCIE_PORT_VC_CNTL`, `PCIE_PORT_VC_STATUS`, and `PCIE_VC0/VC1_RESOURCE_*`.
- `PCIE_BAR_ENH_CAP_LIST` plus `PCIE_BAR1_CAP` through `PCIE_BAR6_CAP`.
- `PCIE_PWR_BUDGET_*` and `PCIE_DPA_*`, including data selection, base power, scale, PM state/substate, power rail, system allocation, DPA substate max, transition latency, substate status/control, and eight substate power-allocation bytes.

The VC resource control fields include command-like load bits and status bits for arbitration tables and VC negotiation. The BAR and power fields are capability descriptors; they should match hardware-advertised resource size and platform power policy rather than be treated as arbitrary driver state.

### Endpoint AER, ACS, PASID, LTR, ARI, 16GT, and Margining

The endpoint block defines advanced PCIe features:

- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, `PCIE_CORR_ERR_STATUS`, `PCIE_HDR_LOG0..3`, and `PCIE_TLP_PREFIX_LOG0..3`.
- `PCIE_SECONDARY_ENH_CAP_LIST` and `PCIE_LANE_ERROR_STATUS`.
- `PCIE_ACS_ENH_CAP_LIST`, `PCIE_ACS_CAP`, and `PCIE_ACS_CNTL`, with source validation, translation blocking, P2P request/completion redirect, upstream forwarding, egress control, direct translated P2P, and egress vector size fields.
- `PCIE_PASID_ENH_CAP_LIST`, `PCIE_PASID_CAP`, and `PCIE_PASID_CNTL`, covering PASID width, execute permission, privileged mode, and enables.
- `PCIE_LTR_ENH_CAP_LIST` and `PCIE_LTR_CAP`, encoding maximum snooped and non-snooped latency values/scales.
- `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL`, describing alternate routing ID interpretation function grouping and next-function fields.
- `PCIE_PHY_16GT_ENH_CAP_LIST` and `PCIE_MARGINING_ENH_CAP_LIST`.

These fields matter for isolation, virtualization, latency management, PCIe error recovery, and high-speed link diagnostics. ACS and PASID are especially sensitive because they affect request routing and address-space tagging expectations.

### BIFPLR0 Legacy PCI/PCIe Bridge Configuration

After the `addressBlock: nbio_pcie0_bifplr0_cfgdecp` marker, the chunk switches to `BIFPLR0_*` fields for a PCIe bridge/root-port style configuration function. It includes conventional PCI configuration registers:

- Identity and class fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `HEADER`, `BIST`, `SSID_CAP`, and `ADAPTER_ID_W`.
- Command/status fields: `COMMAND`, `STATUS`, and `SECONDARY_STATUS`.
- Address-window fields: `BASE_ADDR_1/2`, `SUB_BUS_NUMBER_LATENCY`, `IO_BASE_LIMIT`, `MEM_BASE_LIMIT`, `PREF_BASE_LIMIT`, `PREF_BASE_UPPER`, `PREF_LIMIT_UPPER`, and `IO_BASE_LIMIT_HI`.
- Capability and interrupt fields: `CAP_PTR`, `INTERRUPT_LINE`, `INTERRUPT_PIN`, `EXT_BRIDGE_CNTL`, `VENDOR_CAP_LIST`, `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`.

These macros define how the bridge advertises bus ranges, memory windows, prefetchable windows, IO windows, command enables, and legacy error/status flags. Mis-encoding bridge windows can break PCIe enumeration, access routing, or hotplug/error reporting.

### BIFPLR0 PCIe Device, Link, Slot, and Root Port Control

The BIFPLR0 PCIe capability block includes device/link/slot/root-port fields:

- `PCIE_CAP_LIST` and `PCIE_CAP`.
- `DEVICE_CNTL`, `DEVICE_STATUS`, `DEVICE_CNTL2`, and `DEVICE_STATUS2`.
- `LINK_CAP`, `LINK_STATUS`, `LINK_STATUS2`, plus 16GT-specific `LINK_CAP_16GT` and `LINK_STATUS_16GT`.
- `SLOT_CAP`, `SLOT_CNTL`, `SLOT_STATUS`, and reserved second-generation slot fields.
- `ROOT_CNTL`, `ROOT_CAP`, and `ROOT_STATUS`.

Device control fields include error enables, relaxed ordering, payload/read request sizing, no-snoop, and bridge configuration retry. Device control 2 covers completion timeout, ARI forwarding, atomic operations, ID-based ordering, LTR, OBFF, emergency power reduction, 10-bit tags, and TLP-prefix blocking. Slot and root fields connect to hotplug, PME, system-error signaling, command completion, and presence/power-fault status.

### BIFPLR0 Virtual Channel, Device Serial Number, and AER

BIFPLR0 repeats several extended capability families at bridge scope:

- `PCIE_VC_ENH_CAP_LIST`, `PCIE_PORT_VC_CAP_REG1/2`, `PCIE_PORT_VC_CNTL`, `PCIE_PORT_VC_STATUS`, and VC0/VC1 resource capability/control/status registers.
- `PCIE_DEV_SERIAL_NUM_ENH_CAP_LIST` plus serial number low/high dwords.
- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, `PCIE_UNCORR_ERR_SEVERITY`, `PCIE_CORR_ERR_STATUS`, `PCIE_CORR_ERR_MASK`, `PCIE_ADV_ERR_CAP_CNTL`, `PCIE_HDR_LOG0..3`, `PCIE_ROOT_ERR_CMD`, `PCIE_ERR_SRC_ID`, and `PCIE_TLP_PREFIX_LOG0..3`.

The AER fields include data link protocol, surprise down, poisoned TLP, flow control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, uncorrectable internal error, MC blocked TLP, atomic egress blocked, TLP prefix blocked, and poisoned TLP blocked statuses/masks/severity. Correctable status/mask fields cover receiver errors, bad TLP/DLLP, replay timeout/rollover, advisory non-fatal, correctable internal error, and header log overflow. Root error command/source fields drive root-port AER interrupt routing and source attribution.

### Equalization, ACS/MC/LTR/ARI, DPC, RP PIO, and ESM

The BIFPLR0 secondary capability region includes:

- Per-lane 8GT equalization controls `PCIE_LANE_0_EQUALIZATION_CNTL` through `PCIE_LANE_15_EQUALIZATION_CNTL`, with downstream/upstream port preset and hint fields.
- ACS list marker, multicast (`PCIE_MC_*`) capability/control/address/receive/block/overlay fields, LTR capability, and ARI capability/control fields.
- Downstream Port Containment (`PCIE_DPC_*`) capability, status, and error-source fields.
- Root-port PIO status/mask/severity/system-error/exception fields plus PIO header and prefix logs.
- Emergency service or enhanced speed mode style capability fields under `PCIE_ESM_*`, including `PCIE_ESM_STATUS`, `PCIE_ESM_CTRL`, and large `PCIE_ESM_CAP_1` through `PCIE_ESM_CAP_7` bitmaps.

The DPC/RP PIO fields are error-containment and diagnostics registers. They include trigger status/reason, busy state, interrupt status, first-error pointers, and per-error policy fields. The `PCIE_ESM_CAP_*` registers enumerate many supported data-rate steps, with bit names such as `ESM_8P0G`, `ESM_10P5G`, and higher speed buckets. These fields are descriptive capability bitmaps and control/status bits for link training or service-mode negotiation.

### Data Link Feature, 16GT PHY, and Lane Margining

Near the end, the chunk defines:

- `PCIE_DLF_ENH_CAP_LIST`, `DATA_LINK_FEATURE_CAP`, and `DATA_LINK_FEATURE_STATUS`, covering local/remote data-link feature support, scaled flow-control support, DLF exchange enable, remote support, and remote-valid status.
- `PCIE_PHY_16GT_ENH_CAP_LIST`, `LINK_CAP_16GT`, `LINK_STATUS_16GT`, parity mismatch status registers, and lane 0 through lane 15 16GT equalization preset fields.
- `PCIE_MARGINING_ENH_CAP_LIST`, `MARGINING_PORT_CAP`, `MARGINING_PORT_STATUS`, and lane margining control/status fields for lanes 0 through 5. The chunk ends at the `BIFPLR0_LANE_6_MARGINING_LANE_CNTL` comment before lane 6 fields are listed.

Margining lane control/status fields are regular per-lane encodings for receiver number, margin type, usage model, and margin payload. They describe software-assisted PCIe link margining state; consumers must honor the port readiness and software-ready bits before issuing margining operations.

## Control Flow and State Behavior

This header has no runtime control flow. It affects executable behavior only at compile time by giving C code the constants needed to compose and decode PCIe/NBIO MMIO or configuration-space values.

The state described by the chunk lives in hardware registers. Some fields are relatively static capability descriptors, such as supported payload sizes, link width/speed, BAR size support, power budget entries, serial number fields, ACS/PASID/LTR/ARI support, DPC capabilities, ESM speed bitmaps, DLF support, and 16GT lane equalization capability fields. Other fields are mutable control bits, such as MSI-X enable/function mask, device control enables, VC arbitration load/enable fields, ACS/PASID/ARI control bits, DPA substate control, AER masks/severity, root error command bits, DPC trigger-related state, DLF exchange enable, and margining control payloads.

Several fields are status, sticky status, or hardware-log fields rather than configuration. Examples include link status/training bits, MSI pending bits, correctable/uncorrectable error status, AER header/TLP-prefix logs, device/slot/root status, DPC status/error-source, RP PIO status/logs, ESM status, parity mismatch status, DLF remote-valid status, and margining lane status. Driver code must use the owning PCIe/NBIO access path's ordering, clear, and polling rules; the masks do not encode whether a status bit is write-one-to-clear, sticky-until-reset, read-only, or latched by hardware.

## Dependencies and Integration Points

The direct header dependencies are the generated NBIO 7.7.0 register set:

- `nbio_7_7_0_offset.h` for the matching register addresses/base indices.
- Other generated NBIO mask/default/SMN headers for adjacent register families not covered in this chunk.
- AMDGPU register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and `SOC15_REG_OFFSET`.

Observed integration in this source tree includes `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes both `nbio_7_7_0_offset.h` and this mask header. That NBIO implementation uses the same generated field convention to program HDP remaps, revision ID extraction, framebuffer access enablement, SDMA/VCN/IH doorbell windows, doorbell apertures, interrupt dummy-read behavior, PCIe index/data register offsets, HDP flush masks, max read request behavior, and BIF clock-gating/light-sleep state.

The fields in this chunk are also implicitly tied to PCI core, platform firmware, interrupt setup, error reporting, virtualization/isolation, and link-training flows. Standard PCIe capabilities such as MSI/MSI-X, AER, ACS, PASID, LTR, ARI, DPC, DLF, 16GT PHY, and lane margining may be read or programmed through generic PCI config-space paths, AMDGPU NBIO indirect accessors, or firmware/BIOS initialization rather than by direct use of every macro in `nbio_v7_7.c`.

## Risks

- Register-family mismatch is the highest risk: NBIO 7.7.0 masks must be paired with NBIO 7.7.0 offsets. Using similarly named fields from `nbio_7_0`, `nbio_7_2_0`, `nbio_7_9_0`, or `nbio_7_11_0` can silently program the wrong bits.
- The chunk mixes endpoint-function and bridge/root-port namespaces. `BIF_CFG_DEV1_EPF0_*` and `BIFPLR0_*` fields may have similar PCIe capability names but belong to different configuration functions/address blocks.
- Some fields are narrower than normal C integer expectations. MSI/MSI-X, PCI command/status, slot, root, and margining registers include 8-bit or 16-bit style masks inside generated 32-bit constants; access width and address alignment must match the register accessor's expectations.
- AER, DPC, RP PIO, and margining fields include status/log/clear semantics that are not visible from the mask names. Blind read-modify-write on sticky status registers can lose diagnostic state or acknowledge errors unexpectedly.
- ACS, PASID, ARI, and VC control fields affect isolation, routing, traffic class mapping, and address-space tagging. A bad mask or wrong enable sequence can produce IOMMU isolation failures, malformed routing, or link/traffic negotiation issues.
- Link training, 16GT equalization, DLF, ESM, and lane margining controls are tightly coupled to hardware timing and PCIe specification sequencing. Treating these as ordinary software flags can destabilize the link.
- Generated headers are usually not hand-edited; manual changes to this chunk risk diverging from ASIC register specifications and from sibling offset/default headers.

## Test Signals

Useful validation signals for code depending on this chunk include:

- Build coverage for `amdgpu/nbio_v7_7.c` and any TU including `nbio_7_7_0_sh_mask.h`; compile failures catch renamed, removed, or malformed macro definitions.
- Static checks that every `REG_SET_FIELD`/`REG_GET_FIELD` use pairs a register name with fields from the same register namespace and the matching NBIO generation.
- PCIe enumeration and capability dumps on NBIO 7.7.0 hardware: vendor/device/class, bridge bus windows, MSI/MSI-X table/PBA pointers, PCIe capability, AER, ACS, PASID, LTR, ARI, DPC, DLF, 16GT, and margining capability chains should decode consistently with `lspci -vv` or kernel PCI debug output.
- Runtime AMDGPU smoke tests for device probe, doorbell setup, interrupt delivery, HDP flush completion, memory access enablement, PCIe link speed/width reporting, suspend/resume, and reset/FLR behavior.
- Error-path tests or fault injection for AER/DPC where available: correctable/uncorrectable status, masks, severity, root error command/source IDs, header logs, and RP PIO logs should behave as expected.
- Link diagnostics on capable systems: 16GT equalization status, DLF remote support/valid bits, ESM capability bitmaps, and lane margining ready/software-ready and lane payload/status fields should be readable without corrupting link state.
