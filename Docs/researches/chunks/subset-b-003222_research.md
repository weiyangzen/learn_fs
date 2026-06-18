# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 150913-152483

## Scope

This chunk is the tail of AMDGPU's generated NBIO 7.2.0 shift/mask header. It contains C preprocessor constants for bit positions and masks in NBIO/BIF PCIe configuration registers. There are no functions, structs, typedefs, enums, variables, allocations, locks, or executable statements in this range.

The range starts inside the `BIF_CFG_DEV2_EPF1_1_PCIE_TPH_ST_TABLE_13` register, after its shift definitions and at its mask definitions. It then completes `BIF_CFG_DEV2_EPF1_1_PCIE_TPH_ST_TABLE_14` through `_63`, opens the `nbio_nbif0_bif_cfg_dev2_epf2_bifcfgdecp` address block, describes the full `BIF_CFG_DEV2_EPF2_1_*` PCIe endpoint-function configuration surface, and ends with the header's closing `#endif`.

## Purpose

`nbio_7_2_0_sh_mask.h` supplies the field geometry that AMDGPU code uses when reading or modifying NBIO 7.2 hardware registers. This chunk focuses on the device 2 endpoint-function 1 and endpoint-function 2 PCIe configuration decode blocks, especially the endpoint-function 2 conventional PCI header, PCIe capability chain, interrupt capabilities, AER fields, BAR enhanced capability, power budget, DPA, ACS, PASID, ARI, TPH requester controls, and TPH steering-tag table fields.

These definitions are the shift/mask half of a generated register API. Callers pair the `BIF_CFG_DEV2_EPF2_1_*__FIELD__SHIFT` and `BIF_CFG_DEV2_EPF2_1_*__FIELD_MASK` macros with register offsets from `nbio_7_2_0_offset.h`, then use AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, or SOC15 offset helpers.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public surface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: starting bit for a field inside a hardware register.
- `<REGISTER>__<FIELD>_MASK`: register-positioned bit mask for that field.

Important macro families in this chunk are:

- `BIF_CFG_DEV2_EPF1_1_PCIE_TPH_ST_TABLE_13` through `_63`: the tail of endpoint-function 1's TPH steering-tag table field definitions. Table 13 is partial in this chunk; tables 14-63 each define `TPH_ST_LOWER_ENTRY` at shift `0x0` with mask `0x00FFL` and `TPH_ST_UPPER_ENTRY` at shift `0x8` with mask `0xFF00L`.
- `BIF_CFG_DEV2_EPF2_1_VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, `BASE_ADDR_1` through `_6`, `CARDBUS_CIS_PTR`, `ADAPTER_ID`, `ROM_BASE_ADDR`, `CAP_PTR`, interrupt line/pin, minimum grant, and maximum latency: conventional PCI endpoint configuration fields, including command enables, status bits, BAR values, class code, revision, and interrupt routing.
- `BIF_CFG_DEV2_EPF2_1_VENDOR_CAP_LIST`, `ADAPTER_ID_W`, `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`: vendor/subsystem and power-management capability fields, including capability IDs, next pointers, PME support, power state, PME enable/status, auxiliary power, clock power management, and data select/scale fields.
- `BIF_CFG_DEV2_EPF2_1_PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`: endpoint PCIe capability and PCIe 2.0/extended device/link controls. These cover max payload/read-request sizes, relaxed ordering, no-snoop, error enables, FLR, link speed/width, ASPM/L0s/L1 latency, clock configuration, target link speed, completion timeout policy, LTR/OBFF/atomic-operation support, ID-based ordering, emergency power reduction, and link equalization/status bits.
- `BIF_CFG_DEV2_EPF2_1_MSI_*` and `BIF_CFG_DEV2_EPF2_1_MSIX_*`: MSI and MSI-X capability fields for capability IDs, next pointers, MSI enable, multi-message control, 64-bit address capability, per-vector masking, message address/data, mask/pending registers, MSI-X table size, function mask, table BAR indicator/offset, and PBA BAR indicator/offset.
- `BIF_CFG_DEV2_EPF2_1_PCIE_VENDOR_SPECIFIC_*`: PCIe vendor-specific extended capability header and payload fields.
- `BIF_CFG_DEV2_EPF2_1_PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, `PCIE_UNCORR_ERR_SEVERITY`, `PCIE_CORR_ERR_STATUS`, `PCIE_CORR_ERR_MASK`, `PCIE_ADV_ERR_CAP_CNTL`, `PCIE_HDR_LOG0` through `_3`, and `PCIE_TLP_PREFIX_LOG0` through `_3`: Advanced Error Reporting field definitions for uncorrectable/correctable error status, masks, severities, first-error pointer, ECRC controls, header-log overflow, and captured TLP header/prefix logs.
- `BIF_CFG_DEV2_EPF2_1_PCIE_BAR_ENH_CAP_LIST`, `PCIE_BAR[1-6]_CAP`, and `PCIE_BAR[1-6]_CNTL`: BAR enhanced capability fields that report BAR index, total BAR count, supported BAR size, upper size bits, and selected BAR size.
- `BIF_CFG_DEV2_EPF2_1_PCIE_PWR_BUDGET_*`: PCIe power-budget capability fields for data selection, base power, data scale, PM substate, power rail, and system allocation status.
- `BIF_CFG_DEV2_EPF2_1_PCIE_DPA_*`: Dynamic Power Allocation enhanced capability, capability, latency indicator, status, control, and per-substate power allocation fields. The chunk includes `PCIE_DPA_SUBSTATE_PWR_ALLOC_0` through `_7`.
- `BIF_CFG_DEV2_EPF2_1_PCIE_ACS_*`: Access Control Services capability/control bits for source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, peer-to-peer egress control, direct translated peer-to-peer, and egress control vector size.
- `BIF_CFG_DEV2_EPF2_1_PCIE_PASID_*`: PASID capability/control fields for max PASID width, execute-permission support/enable, privileged-mode support/enable, and PASID enable.
- `BIF_CFG_DEV2_EPF2_1_PCIE_ARI_*`: Alternative Routing-ID Interpretation capability/control fields, including next function number, ACS and MFVC function group capability/enables, function group selection, and ARI forwarding.
- `BIF_CFG_DEV2_EPF2_1_PCIE_TPH_REQR_*` and `PCIE_TPH_ST_TABLE_0` through `_63`: TPH requester enhanced capability, requester capability/control, and steering-tag table fields. Each table register has an 8-bit lower entry and 8-bit upper entry.

## Control Flow And Runtime Behavior

This header has no local control flow. Runtime behavior is created by code that includes it, computes a register address from the companion offset header, and applies the field constants when reading or writing hardware.

The direct C include found for this NBIO generation is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, which includes both `nbio_7_2_0_offset.h` and `nbio_7_2_0_sh_mask.h`. That implementation uses the generated NBIO register metadata for revision straps, memory-size reads, frame-buffer access enablement, doorbell aperture setup, doorbell range programming, HDP flush remapping, interrupt control, medium-grain clock gating, and other NBIO 7.2 controls. The specific `BIF_CFG_DEV2_EPF2_1_*` macros in this chunk are not directly referenced by that C file in this tree; they remain part of the generated hardware contract for any code that needs to decode or program the device 2 endpoint-function 2 PCIe config surface.

Typical external flows are:

1. NBIO or PCIe-related driver code selects the NBIO 7.2 offset macro for a `BIF_CFG_DEV2_EPF2_1_*` register.
2. The caller reads the register or prepares a new register value through AMDGPU/SOC15 access helpers.
3. `REG_GET_FIELD` or `REG_SET_FIELD` uses the macros from this chunk to isolate or encode the target field.
4. Hardware observes the resulting PCIe config, MSI/MSI-X, AER, ACS, PASID, ARI, DPA, BAR, power-budget, or TPH state.

The header does not encode ordering, read-only/write-one-to-clear semantics, capability ownership, polling rules, or reset defaults. Those behaviors must come from hardware documentation, generated default/access metadata where available, and the driver flows using the fields.

## State And Persistence Behavior

The chunk owns no mutable software state and persists nothing. It describes hardware-visible state inside NBIO's PCIe endpoint-function configuration decode.

State represented by the macros includes:

- PCI identity and enumeration state: vendor/device IDs, revision, class code, header type, BAR values, ROM base, capability pointers, adapter/subsystem IDs, interrupt line/pin, and BIST fields.
- PCI command/status state: I/O and memory access enables, bus mastering, parity/SERR behavior, fast back-to-back support, interrupt disable/status, target/master abort state, parity error state, and capability-list presence.
- Power-management state: PM capability support, selected power state, no-soft-reset behavior, PME support/enables/status, auxiliary power, clock power management, and PM data select/scale.
- PCIe link and device state: payload size, read request size, relaxed ordering/no-snoop, phantom functions, extended tags, error enables, FLR, LTR/OBFF/atomic-operation capabilities, completion timeout settings, link speed/width, ASPM-related latencies, clock configuration, retraining, link disable, equalization/compliance state, and link bandwidth notifications.
- Interrupt routing state: MSI/MSI-X capability, enablement, message count, message address/data, mask and pending bits, MSI-X table and PBA locations, and function masking.
- Error-reporting state: AER uncorrectable/correctable status, mask, severity, ECRC controls, first-error pointer, header logs, and TLP prefix logs.
- Resource and power budgeting state: BAR size/support metadata, power budget selectors/data, DPA substate controls, DPA status, and per-substate power allocations.
- Isolation and virtualization-adjacent state: ACS, PASID, ARI, peer-to-peer routing controls, egress control sizing, direct translated peer-to-peer enables, and function group controls.
- TPH state: requester capability/control fields and 64 steering-tag table entries, plus the preceding EPF1 steering-tag table tail.

Persistence across GPU reset, function-level reset, secondary bus reset, suspend/resume, runtime power management, BACO, or PCIe hot reset is not defined here. Some fields are capability read-only, some are OS/driver policy, and some status bits may be sticky or clear-on-write; the shift/mask header intentionally does not distinguish those access classes.

## Dependencies And Integration Points

Primary dependencies and integration points are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h`, which provides the register offsets that pair with these field definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, the direct NBIO 7.2 include site in this tree.
- AMDGPU register helper macros such as `REG_GET_FIELD`, `REG_SET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`.
- Linux PCIe concepts and core expectations for conventional PCI config headers, PCI power management, MSI/MSI-X, PCIe device/link capability registers, AER, ACS, PASID, ARI, TPH, DPA, and power-budgeting capabilities.
- Adjacent chunks of this same generated header. The previous chunk owns the beginning of EPF1 TPH table 13, and this chunk owns the rest of the file through `#endif`.

Because this is generated metadata, exact symbol spelling is the integration contract. A caller must pair `BIF_CFG_DEV2_EPF2_1_*` field macros with the matching DEV2 EPF2 register offsets, and must not accidentally use similar DEV0, DEV1, EPF0, EPF1, or root-complex field macros.

## Risks And Edge Cases

- A wrong shift or mask can compile cleanly while setting or reading the wrong PCIe config bit. In this chunk that can affect bus mastering, memory decoding, interrupt delivery, link retraining, error handling, power management, ACS isolation, PASID, ARI routing, BAR sizing, or TPH steering.
- DEV2 EPF1 and DEV2 EPF2 appear adjacent and have highly repetitive TPH table definitions. Mixing EPF1 table macros with EPF2 offsets, or vice versa, can silently target the wrong endpoint-function's steering tags.
- The chunk starts in the middle of `BIF_CFG_DEV2_EPF1_1_PCIE_TPH_ST_TABLE_13`; a per-file report must merge with the preceding chunk before treating the EPF1 TPH table family as complete.
- The generated TPH table fields are mechanically repeated for 64 entries. A single generator drift in one table entry is easy to miss unless validation checks every index and both lower/upper fields.
- MSI/MSI-X fields are interrupt-routing surfaces. Incorrect address/data, mask, table, PBA, or function-mask programming can lose interrupts or route them to the wrong vector.
- AER status/mask/severity fields are dense and similarly named. Confusing status with mask or severity can suppress real PCIe errors, report false failures, or clear sticky status unexpectedly.
- PCIe device/link controls can be disruptive. Incorrect max payload, max read request, completion timeout, LTR, OBFF, target speed, retrain, link disable, or compliance bits can reduce performance or drop the link.
- ACS, PASID, ARI, and peer-to-peer controls affect isolation and address routing. Bad programming can break virtualization assumptions, peer-to-peer behavior, or requester identity handling.
- BAR enhanced capability and BAR base fields influence resource decode. Misdecoding size or supported-size fields can cause invalid aperture sizing in debug or low-level setup paths.
- DPA and power budget fields describe power policy and substate allocations. Writes without platform-specific sequencing may conflict with firmware or power-management policy.
- The final `#endif` is in this chunk. Accidental edits around the tail could break every includer of the NBIO 7.2 register header, not just this endpoint-function metadata.

## Test And Validation Signals

Useful validation is mostly generated-header consistency plus hardware-level PCIe coverage:

- Build AMDGPU configurations that include `nbio_v7_2.c` to catch syntax errors, missing macros, and broken include guards in `nbio_7_2_0_sh_mask.h`.
- Mechanically verify that each complete register in this range has paired `__SHIFT` and `_MASK` definitions for every field, while allowing the intentional partial start at EPF1 TPH table 13.
- Cross-check `BIF_CFG_DEV2_EPF2_1_*` field macros against `nbio_7_2_0_offset.h` so every field family has a corresponding register offset and the EPF2 names are not mismatched with EPF1 or root-complex offsets.
- Run symmetry checks for repeated fields: EPF1 TPH tables 14-63, EPF2 TPH tables 0-63, BAR1-6 capability/control entries, DPA substate allocations 0-7, MSI 32-bit versus 64-bit data/mask/pending fields, and PCIe header/prefix log dwords.
- Compare decoded PCIe config-space values on NBIO 7.2 hardware against Linux PCI core views for vendor/device ID, class code, command/status, BARs, MSI/MSI-X, link speed/width, payload/read-request sizes, and capability-list traversal.
- Exercise interrupt enable/disable and MSI/MSI-X paths on supported hardware and confirm masks, pending bits, table/PBA location decoding, and message data/address fields behave as expected.
- Exercise PCIe AER test or diagnostic paths where available and confirm uncorrectable/correctable status, masks, severities, ECRC controls, first-error pointer, header logs, and TLP prefix logs decode correctly.
- Exercise suspend/resume, FLR, reset, and runtime power-management paths to ensure writable endpoint policy fields are restored by the owning driver/firmware flows rather than relying on undefined persistence.
- For validation platforms that expose ACS/PASID/ARI/TPH/DPA controls, compare capability bits against expected hardware support and verify driver policy does not write reserved or unsupported bits.

## Chunk Boundary Notes

The range begins at line 150913 with only the mask definitions for `BIF_CFG_DEV2_EPF1_1_PCIE_TPH_ST_TABLE_13`; its shift definitions live in the preceding chunk. Lines 150915-151164 finish EPF1 TPH steering-tag table entries 14-63. Lines 151167-152480 cover the full `nbio_nbif0_bif_cfg_dev2_epf2_bifcfgdecp` block from `BIF_CFG_DEV2_EPF2_1_VENDOR_ID` through `BIF_CFG_DEV2_EPF2_1_PCIE_TPH_ST_TABLE_63`. Lines 152482-152483 close the generated header with `#endif`.
