# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 80664-83095

## Scope

This chunk is a generated AMDGPU NBIO 7.2 shift/mask header segment. It contains 2,432 source lines with 1,075 `__SHIFT` definitions, 1,123 `_MASK` definitions, and 270 register/comment markers. It does not contain C functions, structs, enums, variables, executable statements, locks, memory ownership, or algorithms.

The range starts in the tail of `BIFPLR3_0_PCIE_ESM_CAP_2`, covers the rest of the `BIFPLR3_0` ESM/data-link/16GT/lane-margining/CCIX tail, then enters `addressBlock: nbio_pcie0_bifplr4_cfgdecp`. The `BIFPLR4_0` portion covers a PCIe bridge/root-port configuration-space map from standard PCI identity and bridge registers through many PCIe capability and extended capability registers, ending at the start of `BIFPLR4_0_PCIE_ESM_STATUS`.

Although the repository path is under `ceph-client`, this file is AMD GPU/NBIO hardware metadata. It has no Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_2_0_sh_mask.h` supplies the bitfield-layout half of the NBIO 7.2 register ABI. Each macro follows the generated AMD convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for extracting or placing a field.
- `<REGISTER>__<FIELD>_MASK` gives the encoded mask in the raw register value.

This chunk lets AMDGPU code decode or compose fields in NBIO PCIe configuration registers when paired with register addresses from `nbio_7_2_0_offset.h`. The constants describe field geometry only; they do not encode reset values, access permissions, side effects, valid value combinations, or required sequencing.

## Covered Register Areas

The `BIFPLR3_0` tail covers high-speed PCIe/CCIX capability fields:

- `PCIE_ESM_CAP_2` tail and `PCIE_ESM_CAP_3..7` define bitmaps for supported Extended Speed Mode rates from the 13.x GT/s tail through 28.0 GT/s. These are one-bit rate-presence fields laid out across sequential capability dwords.
- `PCIE_DLF_ENH_CAP_LIST`, `DATA_LINK_FEATURE_CAP`, and `DATA_LINK_FEATURE_STATUS` describe the Data Link Feature extended capability header, local scaled-flow-control/support bits, DLF exchange enable, remote support, and remote-support-valid status.
- `PCIE_PHY_16GT_ENH_CAP_LIST`, `LINK_CAP_16GT`, `LINK_CNTL_16GT`, `LINK_STATUS_16GT`, local/retimer parity mismatch status, and `LANE_0..15_EQUALIZATION_CNTL_16GT` describe PCIe 16GT link equalization status and per-lane downstream/upstream transmit presets.
- `PCIE_MARGINING_ENH_CAP_LIST`, `MARGINING_PORT_CAP`, `MARGINING_PORT_STATUS`, and `LANE_0..15_MARGINING_LANE_CNTL/STATUS` describe lane margining capability, readiness, per-lane receiver selection, margin type, usage model, and payload/status fields.
- `PCIE_CCIX_CAP_LIST`, `PCIE_CCIX_HEADER_1/2`, `PCIE_CCIX_CAP`, `PCIE_CCIX_ESM_REQD_CAP`, `PCIE_CCIX_ESM_OPTL_CAP`, `PCIE_CCIX_ESM_STATUS`, `PCIE_CCIX_ESM_CNTL`, `ESM_LANE_0..15_EQUALIZATION_CNTL_20GT`, `ESM_LANE_0..15_EQUALIZATION_CNTL_25GT`, `PCIE_CCIX_TRANS_CAP`, and `PCIE_CCIX_TRANS_CNTL` describe CCIX vendor capability metadata, required/optional ESM support, ESM current rate/calibration/control fields, per-lane 20GT/25GT presets, and optimized CCIX TLP format support/enable.

The `BIFPLR4_0` block begins a new PCIe root-port/bridge configuration address block:

- Standard PCI bridge config fields: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, revision/class-code bytes, cache line, latency, header type, BIST, bus-number/latency fields, IO/memory/prefetchable window bases and limits, secondary status, ROM base, capability pointer, interrupt line/pin, IRQ bridge control, and extended bridge control.
- Vendor, adapter, PM, and PCIe base capabilities: `VENDOR_CAP_LIST`, `ADAPTER_ID_W`, `PMI_CAP_LIST`, `PMI_CAP`, `PMI_STATUS_CNTL`, `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, slot/root controls/status, and second-generation device/link/slot capability/control/status registers.
- Interrupt and identity capabilities: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, MSI message address/data fields, `SSID_CAP_LIST`, `SSID_CAP`, `MSI_MAP_CAP_LIST`, and `MSI_MAP_CAP`.
- PCIe extended capabilities: vendor-specific extended capability, virtual-channel capability/control/status for VC0 and VC1, device serial number, Advanced Error Reporting, secondary PCIe capability, per-lane equalization controls, ACS, multicast, L1 PM substates, DPC, RP PIO diagnostics, and the first ESM capability header fields.
- Error and diagnostic logs: AER uncorrectable/correctable status/mask/severity, AER capability/control, PCIe header logs, root error command/status/source ID, TLP prefix logs, DPC status/source ID, RP PIO status/mask/severity/system-error/exception, RP PIO header logs, and RP PIO prefix logs.

## Important APIs, Types, and Functions

There are no callable APIs or C types in this chunk. Its public interface is the macro namespace consumed by driver code. Masks are integer literals, often with an `L` suffix, and some are full-width `0xFFFFFFFFL` masks for payload/log dwords such as header logs, serial number words, TLP prefixes, or reserved register bodies.

The macros are meant to be used with the sibling offset header and AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and `SOC15_REG_OFFSET`. Direct include search in this tree shows `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c` includes both `nbio_7_2_0_offset.h` and this shift/mask header; display resource files include the offset header but not this mask header.

## Control Flow

This header has no runtime control flow. Its effect is compile-time substitution:

1. AMDGPU code includes the generated NBIO 7.2 offset and shift/mask headers.
2. The code chooses a register address macro for a `BIFPLR3_0` or `BIFPLR4_0` register.
3. It reads a raw register/config dword, extracts fields with the matching `*_MASK` and `*__SHIFT`, or builds a new value while preserving unrelated bits.
4. Any runtime behavior comes from NBIO/PCIe hardware, firmware-initialized configuration state, PCI core policy, and the caller's read/modify/write sequence.

The field names imply external hardware flows rather than local code flow: PCI bridge enumeration, bus mastering and memory/IO aperture control, MSI routing, PCIe link training, equalization, lane margining, CCIX/ESM calibration, AER logging/clearing, DPC containment, RP PIO error logging, ACS/multicast routing policy, and L1 PM substate power management.

## State and Persistence Behavior

The header owns no state and persists nothing. It describes state stored in NBIO/PCIe configuration registers:

- Identity and capability fields are generally strap, firmware, or hardware capability reports.
- Control fields include command bits, bridge control, PM state, MSI enable/multiple-message control, PCIe device/link/slot/root controls, AER masks/severity/control, ACS control, multicast control, L1 PM substate controls, DPC control, lane equalization preset controls, lane margining controls, ESM/CCIX controls, and optimized CCIX TLP format enable.
- Status/log fields include PCI status, secondary status, PM status, device/link/slot/root status, 16GT equalization status, parity mismatch status, margining status, ESM calibration/current-rate status, AER status/logs, root error status/source ID, lane error status, DPC status/source ID, and RP PIO status/header/prefix logs.

Persistence is hardware-defined. Some values are reset by GPU reset, bus reset, function reset, suspend/resume, or firmware reinitialization. Error/status bits may be latched and write-one-to-clear, while capability fields may be read-only even though this header cannot express that.

## Dependencies and Integration Points

- `nbio_7_2_0_offset.h` is required to supply the matching `cfg...`/`reg...` addresses for these field layouts.
- `amdgpu/nbio_v7_2.c` is the direct NBIO 7.2 source-tree integration point that includes this header.
- AMDGPU SOC15/NBIO register access helpers provide the actual read/write path and field update mechanics.
- PCI and PCI Express architectural definitions provide the semantics for bridge config space, MSI, PM, PCIe device/link/slot/root capabilities, AER, ACS, multicast, L1 PM substates, DPC, data link feature, 16GT PHY, lane margining, and secondary PCIe extended capabilities.
- AMD NBIO 7.2 hardware documentation or generated register databases are the authoritative source for ASIC-specific register offsets, bit positions, masks, access permissions, and reset/side-effect behavior.

## Risks and Edge Cases

- The chunk starts mid-register at the tail of `BIFPLR3_0_PCIE_ESM_CAP_2` and ends at the first line of `BIFPLR4_0_PCIE_ESM_STATUS`; merge/reconciliation must include adjacent chunks before treating those boundary registers as complete.
- A wrong shift/mask can compile cleanly while corrupting PCIe behavior at runtime. High-impact areas include bus mastering, memory/IO aperture windows, MSI delivery, AER/DPC handling, ACS isolation, link control/equalization, L1 power states, and CCIX/ESM controls.
- Many register families are mechanically repeated across lanes 0 through 15 and across status/mask/severity variants. Review must compare full register prefixes (`BIFPLR3_0` vs `BIFPLR4_0`, 16GT vs 20GT/25GT, normal vs ESM equalization) rather than relying on similar field suffixes.
- Status, error, and log registers may have side effects or write-clear semantics. A mask macro alone does not mean a plain read/modify/write is safe.
- Some masks cover full dwords or wide payload fields. New code should avoid signed arithmetic, truncation-prone casts, or assuming all masks describe narrow booleans.
- The `BIFPLR4_0` standard PCI bridge fields share packed config-space words/dwords. Callers must preserve unrelated bits and use the correct access width/path.
- ACS, multicast, DPC, and AER fields affect error containment, traffic forwarding, and isolation. Incorrect programming can become a security, DMA-isolation, or system-stability issue rather than a local decode bug.

## Test Signals

- Build AMDGPU with NBIO 7.2 support enabled so include users catch missing or renamed macros.
- Run generated-header consistency checks: each `__SHIFT` should have a compatible `_MASK`, masks should align with shifts, fields in a register should not overlap unexpectedly, and repeated per-lane/per-status families should match intentionally.
- Cross-check this range against `nbio_7_2_0_offset.h` and the NBIO 7.2 register specification so every `BIFPLR3_0`/`BIFPLR4_0` field maps to the intended register address.
- On NBIO 7.2 hardware, compare decoded config space with `lspci -vvxxx`, PCIe capability dumps, AMDGPU debug register reads, and kernel PCI/AER logs for identity, bridge apertures, MSI, PM, link, AER, ACS, DPC, L1 substate, margining, ESM, and CCIX fields.
- Exercise suspend/resume, GPU reset, PCIe hot/reset paths, link retraining, MSI enable/disable, high-throughput DMA, and error-reporting paths to catch bad preservation of control/status bits.
- For AER/DPC/RP PIO changes, inject or observe PCIe errors and verify status, mask, severity, source ID, header log, and prefix log decoding.
