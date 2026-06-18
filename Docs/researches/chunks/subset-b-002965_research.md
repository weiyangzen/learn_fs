# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 10030-12477

## Scope

This chunk covers generated AMD NBIO 4.3.0 shift and mask macros for two adjacent PCIe configuration-space decode regions. It starts in the root-complex function `BIF_CFG_DEV0_RC0` extended PCIe capability area, beginning at the tail of `PCIE_VC1_RESOURCE_STATUS`, and continues through device serial number, Advanced Error Reporting, secondary PCIe, ACS, Data Link Feature, 16 GT/s and 32 GT/s PHY/equalization, lane margining, Alternate Protocol, and Reset Time Reporting fields. The range then crosses into `addressBlock: nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` and covers the beginning of endpoint function 0 (`BIF_CFG_DEV0_EPF0_0`) configuration space through `DATA_LINK_FEATURE_STATUS`.

The file is a generated hardware register bitfield header. This range defines C preprocessor constants only; it has no C functions, structs, variables, executable branches, loops, allocation, locking, I/O calls, or direct register accesses.

## Purpose

The purpose of this header segment is to publish the bit-level ABI for NBIO/NBIF PCIe configuration-space registers on NBIO 4.3.0 hardware. Each field is represented as the usual generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset for packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate, clear, preserve, or compose the field.

The companion NBIO 4.3.0 offset header supplies the register addresses. Runtime AMDGPU and PCIe/NBIO code can combine those offsets with these masks through register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, SOC15 register accessors, and PCIe/NBIO indirect config-space accessors, without hard-coding bit positions.

## Important Macro Families

### RC0 Extended PCIe Capabilities

The opening RC0 portion is rooted under `BIF_CFG_DEV0_RC0_*`. It finishes `PCIE_VC1_RESOURCE_STATUS`, then defines the device serial number enhanced capability (`PCIE_DEV_SERIAL_NUM_ENH_CAP_LIST`, `PCIE_DEV_SERIAL_NUM_DW1`, and `DW2`).

The AER block defines:

- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST` for capability ID, version, and next pointer.
- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY` for DLP, surprise-down, poisoned TLP, flow-control protocol, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned-TLP egress blocked conditions.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK` for receiver error, bad TLP, bad DLLP, replay rollover, replay timer timeout, advisory non-fatal, corrected internal error, and header-log overflow.
- `PCIE_ADV_ERR_CAP_CNTL`, `PCIE_HDR_LOG0..3`, and `PCIE_TLP_PREFIX_LOG0..3` for first-error pointer, ECRC controls, multi-header recording, completion-timeout logging, and captured packet/header diagnostics.

The secondary PCIe and lane-equalization section includes `PCIE_SECONDARY_ENH_CAP_LIST`, `PCIE_LINK_CNTL3`, `PCIE_LANE_ERROR_STATUS`, and `PCIE_LANE_0_EQUALIZATION_CNTL` through `LANE_15_EQUALIZATION_CNTL`. These fields describe perform-equivalent-control, link equalization request interrupt enable, lane error status, and Gen3 8 GT/s upstream/downstream preset and hint fields.

The RC0 access/isolation and data-link groups include `PCIE_ACS_ENH_CAP_LIST`, `PCIE_ACS_CAP`, `PCIE_ACS_CNTL`, `PCIE_DLF_ENH_CAP_LIST`, `DATA_LINK_FEATURE_CAP`, and `DATA_LINK_FEATURE_STATUS`. ACS fields cover source validation, translation blocking, peer-to-peer redirection, upstream forwarding, egress control, direct translated P2P, I/O request blocking, memory target access controls, and unclaimed request redirection. DLF fields cover local and remote data-link feature support plus validity and exchange-enable bits.

The high-speed PHY sections define 16 GT/s and 32 GT/s capability/control/status layouts:

- `PCIE_PHY_16GT_ENH_CAP_LIST`, reserved `LINK_CAP_16GT` and `LINK_CNTL_16GT`, `LINK_STATUS_16GT`, local/RTM parity mismatch status, and per-lane `LANE_0..15_EQUALIZATION_CNTL_16GT` fields for DSP/USP presets.
- `PCIE_MARGINING_ENH_CAP_LIST`, `MARGINING_PORT_CAP`, `MARGINING_PORT_STATUS`, and per-lane `MARGINING_LANE_CNTL`/`STATUS` pairs for lanes 0 through 15, carrying receiver number, margin type, usage model, and payload/status fields.
- `PCIE_PHY_32GT_ENH_CAP_LIST`, `LINK_CAP_32GT`, `LINK_CNTL_32GT`, `LINK_STATUS_32GT`, received/transmitted modified training sequence data, and per-lane `LANE_0..15_EQUALIZATION_CNTL_32GT` DSP/USP presets.

The RC0 tail covers `PCIE_AP_ENH_CAP_LIST`, `AP_CAP`, `AP_CNTL`, `AP_DATA1`, `AP_DATA2`, `AP_SEL_EN_MASK`, plus `PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2`. These encode alternate protocol negotiation metadata, selected protocol masks, vendor/usage information, and reset/link-up/FLR/D3hot-to-D0 timing values.

### EPF0 Configuration Space

After the address-block marker, the chunk starts the endpoint function 0 config decoder `BIF_CFG_DEV0_EPF0_0_*`.

The conventional PCI header section covers identity and base configuration fields: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, `BASE_ADDR_1..6`, `CARDBUS_CIS_PTR`, `ADAPTER_ID`, `ROM_BASE_ADDR`, `CAP_PTR`, interrupt line/pin, min grant, max latency, vendor capability list, and writable adapter ID. `COMMAND` exposes I/O, memory, bus master, parity, SERR, and interrupt disable bits; `STATUS` exposes capability-list presence, interrupt status, target/master aborts, system error, parity error, and related status.

The PM and PCIe capability portions include `PMI_CAP_LIST`, `PMI_CAP`, `PMI_STATUS_CNTL`, `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`. These masks describe max payload and read request sizes, relaxed ordering, no-snoop, error-reporting enables, FLR, completion timeout controls, ARI forwarding, atomic operation controls, LTR/OBFF, 10-bit tags, TLP prefix controls, link speed/width, ASPM, retrain, common clock, bandwidth interrupts, target link speed, compliance/de-emphasis controls, equalization status, RTM presence, DRS, and downstream component presence.

The interrupt capability section defines MSI and MSI-X state: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, MSI address/data fields, extended MSI data, mask and pending fields, 64-bit aliases, `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`. These fields are used to describe interrupt enablement, table/PBA placement, vector masking, pending state, address, and data payloads.

The endpoint extended capability groups include vendor-specific capability metadata and scratch dwords, virtual channel capability/control/resource registers for VC0 and VC1, device serial number, AER status/masks/severity/logs, resizable BAR capability/control registers for BAR1 through BAR6, power budget data selection/data/capability, DPA capability/status/control and eight substate power allocation dwords, secondary PCIe link/lane equalization fields, ACS capability/control, PASID capability/control, multicast capability/control/address/receive/block registers, LTR, ARI, SR-IOV capability/control/status and VF BAR/page-size/count/stride fields, and finally DLF capability/status. The assigned range stops after `BIF_CFG_DEV0_EPF0_0_DATA_LINK_FEATURE_STATUS`; the following EPF0 16 GT/s PHY fields are outside this work item.

## Control Flow

There is no executable control flow in this header. Runtime code uses these constants in a simple pattern:

1. Select the matching `cfg...` register offset from the NBIO 4.3.0 offset header.
2. Read or compose a PCIe configuration-space dword or word through AMDGPU's NBIO/register access layer.
3. Apply this header's `__SHIFT` and `_MASK` macros directly or via field helper macros.
4. Write controls, poll hardware status, clear sticky diagnostics, decode PCIe capability state, or expose values through PCIe/SR-IOV/error handling paths.

All sequencing, access rights, polling, write-one-to-clear behavior, and reset ordering are defined outside this file by PCIe rules, AMD hardware behavior, firmware/platform policy, and the consuming driver code.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes hardware-backed PCIe configuration and status state.

The RC0 portion describes root-complex-side capability, error, lane, margining, alternate protocol, and reset timing state. Some fields are static capabilities, some are software-programmed policy bits, and others are hardware-updated or sticky status/log fields.

The EPF0 portion describes endpoint function state: PCI identity, class, command/status, BARs, ROM BAR, PM state, PCIe device/link capabilities, MSI/MSI-X programming, vendor-specific scratch state, virtual channels, serial number, AER logs and masks, resizable BAR controls, power budget/DPA state, ACS/PASID/multicast/LTR/ARI/SR-IOV controls, VF BAR metadata, and data-link feature negotiation state. The macros do not encode whether a field is read-only, write-once, volatile, sticky, write-one-to-clear, PF-only, firmware-owned, or safe for guest/VF access.

## Dependencies And Integration Points

The direct dependencies are the generated NBIO 4.3.0 register headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h` for matching register offsets.
- Any matching default/reset-value header generated for NBIO 4.3.0, where present.
- AMDGPU register helper macros and NBIO/PCIe accessors that consume generated `__SHIFT` and `_MASK` constants.

Integration points include AMDGPU NBIO initialization, PCIe config-space access, PCIe link training and speed management, AER diagnostics and recovery, SR-IOV/VF provisioning, MSI/MSI-X interrupt setup, ACS/PASID/ARI/LTR/multicast policy, resizable BAR and VF BAR exposure, DPA/power-budget handling, lane margining/equalization diagnostics, alternate protocol negotiation, and reset/link-up timing reporting.

Although the source lives under a `ceph-client` mirror path in this repository, this header is AMDGPU hardware metadata. It does not implement distributed filesystem behavior.

## Risks And Edge Cases

- The chunk boundaries are artificial. It starts at the last masks of `BIF_CFG_DEV0_RC0_PCIE_VC1_RESOURCE_STATUS` and stops immediately before EPF0 16 GT/s PHY definitions, so neighboring chunks are required for complete whole-register and whole-address-block conclusions.
- These macros are hardware ABI. A stale shift or mask can compile cleanly while silently reading or programming the wrong PCIe field.
- RC0 and EPF0 prefixes are both present. Applying an endpoint mask to a root-complex offset, or vice versa, can produce plausible bit operations against the wrong register family.
- AER status, severity, masks, header logs, and TLP prefix logs are diagnostic and policy-sensitive. Generic read/modify/write treatment can clear evidence, leave errors masked, or misclassify fatal versus non-fatal errors.
- Link equalization, lane margining, 16/32 GT/s status, and modified training sequence fields are interoperability-sensitive. Incorrect sequencing can cause link instability, failed speed changes, or misleading training diagnostics.
- ACS, PASID, ARI, multicast, SR-IOV, and VF BAR fields affect isolation, address translation, enumeration, and resource exposure. Incorrect masks or writes can break VF creation, DMA isolation, interrupt routing, or PCIe request routing.
- MSI/MSI-X fields have interrupt-delivery side effects. Wrong address/data, mask, pending, table, or PBA decoding can cause lost or misrouted interrupts.
- Reserved fields such as RC0 `LINK_CAP_16GT`/`LINK_CNTL_16GT` still have full-width masks in the generated file; consumers should not infer that all bits are writable or meaningful.
- Generated-file maintenance is fragile. Manual edits should be avoided unless cross-checked against the authoritative register database, offset header, and hardware documentation.

## Test Signals

Useful validation signals are mostly build-time and hardware-integration oriented:

- Build AMDGPU with NBIO 4.3.0 headers enabled and confirm no missing, renamed, or duplicate `BIF_CFG_DEV0_RC0_*` or `BIF_CFG_DEV0_EPF0_0_*` macros.
- Compare this shift/mask range against the matching `nbio_4_3_0_offset.h` names and any generated defaults to catch register-name drift or field-order mismatches.
- Exercise PCI enumeration on affected hardware and compare decoded EPF0 config-space fields with `lspci -vv`, especially command/status, BARs, PM, PCIe capability, link capability/status, MSI/MSI-X, AER, ACS, PASID, ARI, SR-IOV, LTR, and DLF exposure.
- Run PCIe link-management tests that retrain links, change target speed where supported, and observe 8 GT/s, 16 GT/s, and 32 GT/s equalization/status fields.
- Use AER injection or platform error-observation paths to verify uncorrectable/correctable status, masks, severity, header logs, TLP prefix logs, and first-error pointer decoding.
- In SR-IOV configurations, create/remove VFs, validate VF BAR sizing and page-size fields, exercise FLR/reset paths, and confirm isolation-related ACS/PASID/ARI fields behave as expected.
- Verify MSI and MSI-X interrupt delivery under load, including enable/disable, vector masking, pending bits, MSI-X table/PBA placement, and reset/rebind behavior.
- Where hardware and platform support it, run lane margining/equalization diagnostics and confirm per-lane control/status masks decode lane number, receiver, margin type, payload, and preset fields consistently.

## Chunk Notes

Lines 10030-11080 remain in the `BIF_CFG_DEV0_RC0` root-complex config-space block and cover RC0 extended PCIe capability, AER, ACS, DLF, high-speed PHY, lane margining, alternate protocol, and reset-time reporting masks.

Lines 11081-12477 start `addressBlock: nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` and cover the beginning of endpoint function 0 through `BIF_CFG_DEV0_EPF0_0_DATA_LINK_FEATURE_STATUS`. The next chunk continues with EPF0 16 GT/s PHY fields.
