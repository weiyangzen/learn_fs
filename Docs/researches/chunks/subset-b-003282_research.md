# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 56189-58624

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.7.0 shift/mask header. It defines C preprocessor constants for fields in PCIe configuration-space register images exposed through the NBIO/BIF configuration decode path. The constants describe bit positions and masks only; the matching register offsets live in the paired `nbio_7_7_0_offset.h` header and the operational semantics come from the ASIC hardware.

The requested range starts in the tail of `BIF_CFG_DEV0_EPF7_0_DBESL_DBESLD`, then covers the remainder of the `BIF_CFG_DEV0_EPF7_0` endpoint-function PCIe capability and enhanced-capability space. At line 56974 it switches to `addressBlock: nbio_nbif0_bif_cfg_dev1_epf0_bifcfgdecp`, beginning the `BIF_CFG_DEV1_EPF0_0` endpoint-function configuration image. The chunk ends inside `DEV1_EPF0_0` lane margining fields at `LANE_14_MARGINING_LANE_STATUS`; lane 15 and subsequent groups, if any, are outside this chunk.

## Major Register Groups

The `BIF_CFG_DEV0_EPF7_0` portion includes:

- PCIe capability-list, capability, device/link capability, control, and status fields, including payload/read-request sizing, FLR, error-reporting enables, relaxed ordering, no-snoop, link speed/width, ASPM/PM, retrain, data-link active, and PCIe Capability 2 controls.
- MSI and MSI-X capability fields, including message control, address/data, mask/pending registers, MSI-X table and PBA BIR/offset fields, and enable/function-mask bits.
- Vendor-specific enhanced capability fields with VSEC header metadata and scratch payload fields.
- Advanced Error Reporting fields for uncorrectable status/mask/severity, correctable status/mask, ECRC controls, first-error pointer, header logs, and TLP prefix logs.
- Enhanced BAR capability/control groups for BAR1 through BAR6, power-budgeting capability/data, Dynamic Power Allocation capability/status/control and per-substate power allocation, ACS capability/control, PASID capability/control, and ARI capability/control.

The `BIF_CFG_DEV1_EPF0_0` portion restarts from a conventional endpoint PCI configuration header and then expands into a richer endpoint-function capability image:

- Conventional PCI config fields: vendor/device ID, command/status, revision/class code, cache/latency/header/BIST, BAR1 through BAR6, CardBus CIS pointer, subsystem IDs, ROM BAR, capability pointer, interrupt line/pin, grant/latency, vendor capability, PM capability/status-control, SBRN, FLADJ, and DBESL/DBESLD.
- PCIe device/link capability, control, and status fields, PCIe Capability 2 controls/status, and Link Capability/Control/Status 2 fields.
- MSI/MSI-X, vendor-specific enhanced capability, and Virtual Channel capability/control/status for port VC state plus VC0 and VC1 resource controls.
- AER fields mirroring the DEV0 endpoint-function error model: uncorrectable/correctable status and masks, severity selection, ECRC controls, header logs, and TLP prefix logs.
- Enhanced BAR, power-budgeting, DPA, ACS, PASID, LTR, ARI, Data Link Feature, PCIe PHY 16GT, and PCIe margining capability groups.
- Per-lane controls for 8 GT/s equalization lanes 0-15, 16 GT/s equalization presets lanes 0-15, and margining control/status pairs for lanes 0-14 in this chunk.

## Important APIs, Types, And Functions

There are no functions, structs, enums, or runtime APIs in this range. Its exported interface is a generated macro namespace:

- `BIF_CFG_DEV0_EPF7_0_<REGISTER>__<FIELD>__SHIFT` and `BIF_CFG_DEV1_EPF0_0_<REGISTER>__<FIELD>__SHIFT` define the zero-based bit position of a field.
- `BIF_CFG_DEV0_EPF7_0_<REGISTER>__<FIELD>_MASK` and `BIF_CFG_DEV1_EPF0_0_<REGISTER>__<FIELD>_MASK` define the field mask in the containing register.
- Full-register payload fields use 32-bit masks such as `*_TLP_HDR_MASK`, `*_TLP_PREFIX_MASK`, `*_SCRATCH_MASK`, and `*_MSI_PENDING_64_MASK`.

The range is generated data, not hand-written logic. Most fields appear as a shift/mask pair, but the chunk boundaries are partial: the `DBESL_DBESLD` group starts before line 56189, and the last visible group, `BIF_CFG_DEV1_EPF0_0_LANE_14_MARGINING_LANE_STATUS`, continues only through its field definitions within this range while later lane groups are outside the requested slice.

## Control Flow

This header has no executable control flow. Runtime behavior is supplied by AMDGPU code that includes the generated NBIO headers, selects the NBIO 7.7.0 register map for the detected ASIC, reads or writes the paired register offset, and applies these masks and shifts.

Typical consumer flow is:

1. Select the matching register offset from `nbio_7_7_0_offset.h`, such as a `regBIF_CFG_DEV0_EPF7_0_*` or `regBIF_CFG_DEV1_EPF0_0_*` definition.
2. Read the NBIO/BIF config register through the driver MMIO or indexed-register access path.
3. Decode fields with `value & *_MASK`, shifted by the corresponding `*__SHIFT`.
4. For writable controls, preserve unrelated and reserved bits, insert the shifted field value under the mask, and write the register back.

The hardware flows described by these fields include PCIe capability discovery, link training and retraining, payload/read-request negotiation, MSI/MSI-X interrupt delivery, AER/RAS error reporting, BAR sizing and control, DPA/power-budget reporting, ACS/PASID/ARI isolation and function-routing features, LTR latency reporting, DLF negotiation, 8 GT/s and 16 GT/s equalization, and software-driven lane margining.

## State And Persistence

The header itself is stateless and persists no data. It is a compile-time description of hardware register layouts.

The state described by these macros lives in NBIO PCIe configuration registers. Capability fields such as supported link speed/width, maximum payload support, FLR capability, BAR size support, ACS/PASID/ARI support, LTR support, DPA support, data-link feature support, 16 GT/s capability, and margining capability are generally hardware- or firmware-defined for the ASIC.

Control fields such as `DEVICE_CNTL`, `DEVICE_CNTL2`, `LINK_CNTL`, `LINK_CNTL2`, MSI/MSI-X enables and masks, AER masks/severity/ECRC enables, BAR controls, DPA controls, ACS/PASID/ARI controls, VC resource controls, data-link feature exchange enable, 16 GT/s link controls, equalization presets, and margining lane controls are writable hardware state. Their lifetime depends on PCIe reset, function reset, GPU reset, suspend/resume, and power-management domains.

Status and log fields such as device/link status, AER status, AER header and prefix logs, MSI pending bits, DPA status, VC status, lane error status, DLF remote-support status, 16 GT/s link/equalization status, parity mismatch status, and lane margining status are live hardware observations. This generated header does not encode reset defaults, access permissions, write-one-to-clear behavior, latching behavior, or whether a status read has side effects.

## Dependencies And Integration Points

These macros are meaningful only when paired with the NBIO 7.7.0 offset and access machinery. A field macro such as `BIF_CFG_DEV1_EPF0_0_PCIE_UNCORR_ERR_STATUS__CPL_TIMEOUT_STATUS_MASK` does not identify an address by itself; it must be used with the corresponding `regBIF_CFG_DEV1_EPF0_0_PCIE_UNCORR_ERR_STATUS` offset and the correct NBIO instance/base.

Integration points include:

- AMDGPU ASIC register headers under `drivers/gpu/drm/amd/include/asic_reg/nbio`, especially `nbio_7_7_0_offset.h`.
- NBIO and PCIe configuration code that reads or writes BIF config-space images for endpoint functions.
- PCIe enumeration and diagnostics paths that inspect endpoint vendor/device/class, BAR, PM, PCIe capability, MSI/MSI-X, and enhanced capability state.
- Interrupt setup and debug code that programs MSI/MSI-X message address/data, enable, mask, pending, table, and PBA fields.
- RAS/AER code that decodes correctable and uncorrectable errors, masks, severity policy, first-error pointers, ECRC configuration, header logs, and TLP prefix logs.
- Link-management and diagnostics code that decodes negotiated link speed/width, retraining, Link Status 2 equalization flags, lane error status, 8 GT/s equalization presets, 16 GT/s status/presets, and PCIe lane-margining controls/status.
- IOMMU, SR-IOV, or virtualization-adjacent paths that care about ACS, PASID, ARI, BAR sizing, and P2P isolation behavior.

## Risks

The main risk is silent hardware misprogramming if a mask or shift is wrong, stale, or paired with the wrong offset block. A bit-position error can misdecode link state, select an invalid payload or read-request size, suppress or misclassify AER events, corrupt MSI/MSI-X delivery, change BAR control semantics, break ACS/PASID/ARI policy, or issue unintended equalization or lane-margining commands.

The range has important boundary hazards. The first lines are the tail of `BIF_CFG_DEV0_EPF7_0_DBESL_DBESLD`, so the full group must be reconciled with the previous chunk. The final visible lane-margining group stops at lane 14; a complete per-file analysis must merge with following chunks before treating `DEV1_EPF0_0` margining coverage as complete.

Several names are very similar and easy to misuse. `DEV0_EPF7_0` and `DEV1_EPF0_0` are different configuration images. MSI and MSI-X controls have similar enable/mask words but different data structures. AER status, mask, and severity groups share most field names while having different semantics. Equalization groups distinguish 8 GT/s `PCIE_LANE_<n>_EQUALIZATION_CNTL` from 16 GT/s `LANE_<n>_EQUALIZATION_CNTL_16GT`, and margining has separate lane control and status registers.

Generated `RESERVED` masks and full-width payload masks should not be treated as permission to write arbitrary bits. Reserved fields, AER status, parity mismatch status, lane error status, and margining status may have hardware-specific clear or latch semantics not captured by these macros.

## Test Signals

Useful validation signals are hardware- and integration-facing:

- The AMDGPU tree builds with NBIO 7.7.0 headers included, proving generated macro names resolve for consumers.
- Static or generator checks confirm that every complete register group in this chunk has a matching `regBIF_CFG_DEV0_EPF7_0_*` or `regBIF_CFG_DEV1_EPF0_0_*` offset/base definition in `nbio_7_7_0_offset.h`.
- PCIe config dumps on matching hardware report plausible endpoint vendor/device, class, BAR, PM, PCIe capability, MSI/MSI-X, VSEC, VC, AER, ACS, PASID, LTR, ARI, DLF, PHY 16GT, and margining capability values.
- MSI/MSI-X tests verify that message address/data, table/PBA BIR and offset, enable, mask, and pending fields match interrupt behavior.
- AER/RAS tests or fault injection decode correctable and uncorrectable status, masks, severity, ECRC controls, header logs, and prefix logs consistently with hardware documentation.
- Link diagnostics decode expected speed, width, training state, Link Status 2 equalization state, DLF state, lane error status, 8 GT/s presets, 16 GT/s presets/status, and margining ready/control/status fields.
- Suspend/resume, FLR, hot reset, and GPU reset testing verifies that writable endpoint controls are restored by higher-level driver paths rather than relying on defaults implied by this generated header.
