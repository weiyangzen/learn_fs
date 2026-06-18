# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 51289-53722

## Scope

This chunk covers a generated AMD NBIO 7.7.0 shift/mask header slice for PCIe endpoint-function configuration-space fields. It contains no executable C logic. The range is 2,434 source lines with 2,144 `#define` entries and 286 register/comment markers.

The slice spans:

- The tail of `BIF_CFG_DEV0_EPF2_0`, starting at `DBESL_DBESLD` after the preceding `SBRN`/`FLADJ` definitions.
- The complete `addressBlock: nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp` block from standard PCI identity fields through ARI control.
- The beginning of `addressBlock: nbio_nbif0_bif_cfg_dev0_epf4_bifcfgdecp`, from standard PCI identity fields through the start of `PCIE_CORR_ERR_MASK`.

The chunk is source-tree aligned with AMDGPU generated register headers. The final per-file report should reconcile this document with adjacent chunks before treating EPF2 or EPF4 as complete.

## Purpose

`nbio_7_7_0_sh_mask.h` provides bit positions and masks for the NBIO 7.7.0 register database. This chunk describes PCI and PCIe configuration-space fields for device 0 endpoint functions EPF2, EPF3, and EPF4. Consumers pair these macros with register addresses from the companion `nbio_7_7_0_offset.h` header and with AMDGPU register helper macros when extracting or programming individual fields.

The values are hardware ABI, not policy. They let driver code and debug tooling name fields such as PCI command bits, BAR fields, PCIe device/link capability bits, MSI/MSI-X controls, AER status/mask/severity bits, resizable BAR controls, dynamic power allocation, ACS, PASID, and ARI without hard-coding numeric bit positions.

## Important API Surface

There are no functions, structs, enums, typedefs, globals, or inline helpers in this range. The exported interface is the macro namespace:

- `BIF_CFG_DEV0_EPF<n>_0_<REGISTER>__<FIELD>__SHIFT` gives the low bit of a field.
- `BIF_CFG_DEV0_EPF<n>_0_<REGISTER>__<FIELD>_MASK` gives the field mask already shifted into register position.
- Register comments such as `//BIF_CFG_DEV0_EPF3_0_DEVICE_CNTL2` group the fields by containing register.
- Address-block comments identify generated config-space templates, for example `nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp` and `nbio_nbif0_bif_cfg_dev0_epf4_bifcfgdecp`.

Most logical fields are represented by a shift/mask pair. The observed count is 1,073 `__SHIFT` macros and 1,150 `_MASK` macros because the requested line range starts and ends inside larger generated register families; some masks or shifts are owned by adjacent chunks.

## Register Families Covered

### EPF2 Tail

The EPF2 portion begins in the conventional capability area after the previous chunk's `SBRN` and `FLADJ` fields. It covers 89 register groups for `BIF_CFG_DEV0_EPF2_0`:

- `DBESL_DBESLD` USB-style device best-effort service latency fields.
- PCIe capability list and PCIe capability header fields.
- Device capability/control/status fields for payload size, read request size, relaxed ordering, no-snoop, extended tag, FLR, error enables, transaction-pending state, and emergency power reduction status.
- Link capability/control/status fields for supported/current speed, width, ASPM/PM support, retrain/link disable/common-clock behavior, data-link active state, bandwidth notifications, DRS signaling, and link-status-2 equalization observations.
- Device capability/control/status 2 and link capability/control/status 2 fields for completion timeout, ARI forwarding, atomic operations, ID-based ordering, LTR, OBFF, 10-bit tags, end-to-end TLP prefixes, FRS, supported speed vector, compliance/de-emphasis controls, and crosslink/DRS status.
- MSI and MSI-X capability fields, including message address/data variants, extended message data, mask/pending registers, MSI-X table size/enable/function mask, table BIR/offset, and PBA BIR/offset.
- PCIe vendor-specific enhanced capability header and two scratch registers.
- Advanced Error Reporting fields: uncorrectable status/mask/severity, correctable status/mask, AER capability/control, header logs, and TLP prefix logs.
- Resizable BAR capability/control fields for BAR1 through BAR6.
- Power budget fields, dynamic power allocation capability/status/control and eight substate power-allocation registers.
- ACS capability/control fields, PASID capability/control fields, and ARI capability/control fields.

This EPF2 segment is partial because the standard PCI header, power-management capability, `SBRN`, and `FLADJ` groups start before line 51289.

### EPF3 Complete Endpoint Template

The EPF3 address block is complete within this chunk. It repeats the endpoint-function layout under the `BIF_CFG_DEV0_EPF3_0_*` namespace and covers 122 register groups:

- Standard PCI configuration header: vendor/device ID, command/status, revision/class fields, cache-line/latency/header/BIST, BAR1-BAR6, CardBus CIS pointer, subsystem/adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, max latency, vendor capability list, and writable adapter ID mirror.
- Power management: `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`, including PME support/enables/status, D1/D2 support, auxiliary current, power state, no-soft-reset, data select/scale, B2/B3 support, and bus power enable.
- Legacy/auxiliary fields: `SBRN`, `FLADJ`, and `DBESL_DBESLD`.
- PCIe capability: PCIe capability-list header, device/link capability-control-status groups, PCIe capability 2 groups, and link capability/control/status 2 groups.
- Interrupt capabilities: MSI and MSI-X message control, address/data, mask, pending, table, and PBA fields.
- PCIe vendor-specific enhanced capability and two scratch registers.
- AER: enhanced capability list, uncorrectable status/mask/severity, correctable status/mask, advanced error capability/control, header logs, and TLP prefix logs.
- Resizable BAR: BAR1-BAR6 capability/control fields, including supported size vectors, selected sizes, BAR index, total number, and upper supported-size bits.
- Power budget and DPA: power budget data select/data/capability, DPA substate maximum and latency fields, DPA status/control, and eight substate power allocation registers.
- ACS, PASID, and ARI: routing/isolation capabilities and enables, PASID width and privilege/execute support, PASID enable bits, ARI next-function and function-group controls.

EPF3's layout is mechanically similar to EPF2 but must not be treated as interchangeable. The prefix selects a different endpoint function's configuration image even when numeric masks are identical.

### EPF4 Beginning

The EPF4 address block starts in this chunk and covers 73 register groups before ending mid-AER:

- Standard PCI identity, command/status, class/revision, BAR, ROM, capability pointer, interrupt, and subsystem/adapter fields.
- Power management, `SBRN`, `FLADJ`, and `DBESL_DBESLD`.
- PCIe capability list, device and link capability/control/status, and device/link capability 2 fields.
- MSI/MSI-X capability fields.
- PCIe vendor-specific enhanced capability header and scratch fields.
- AER enhanced capability list, uncorrectable error status/mask/severity, and correctable error status.
- The first `PCIE_CORR_ERR_MASK` shift definitions begin at the end of the requested range; the remaining fields and later EPF4 AER/logging/capability groups belong to the next chunk.

EPF4 is therefore intentionally incomplete here. Any audit should use adjacent chunks before concluding which EPF4 AER masks are present.

## Control Flow

This header has no runtime control flow. It contributes compile-time constants to downstream code that performs hardware register access. The effective consumer flow is:

1. Include the NBIO 7.7.0 offset header for the register address and this shift/mask header for field layout.
2. Read the PCIe/NBIO configuration register through the relevant AMDGPU MMIO, indexed, or PCIe-port access path.
3. Extract fields with `value & *_MASK` and the matching `*__SHIFT`, commonly through AMD register helper patterns such as `REG_GET_FIELD`.
4. For writable controls, preserve unrelated bits, insert the new field value with the matching mask/shift, and write the register back.

Hardware behaviors represented by these fields include PCI enumeration, BAR decode, MSI/MSI-X interrupt delivery, PCIe link training and feature negotiation, error reporting through AER, dynamic power allocation, power budget reporting, ACS isolation, PASID tagging, and ARI multi-function routing.

## State and Persistence Behavior

The macros themselves are immutable preprocessor constants and hold no state. The state they describe lives in device configuration registers and PCIe enhanced capabilities:

- Identity, class, capability-list, supported-link, supported-payload, AER capability, resizable-BAR capability, power-budget capability, DPA capability, ACS/PASID/ARI capability fields are hardware/firmware-defined values for the endpoint-function image.
- Command, BAR, ROM BAR, MSI/MSI-X enable/mask, PCIe device/link controls, completion timeout controls, DPA control, ACS control, PASID control, ARI control, AER masks, and AER severity fields are writable configuration state whose lifetime depends on PCI reset, GPU reset, function-level reset, suspend/resume, and firmware initialization.
- Link status, device status, MSI pending, AER status, header logs, TLP prefix logs, DPA status, and power-management status are live or latched hardware observations.

The header does not encode access permissions, reset defaults, write-one-to-clear behavior, ordering requirements, access width, or side effects. Callers must rely on PCIe semantics, hardware documentation, and existing AMDGPU access helpers for those rules.

## Dependencies and Integration Points

The direct generated dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h`, which supplies matching `cfgBIF_CFG_DEV0_EPF2_*`, `cfgBIF_CFG_DEV0_EPF3_*`, and `cfgBIF_CFG_DEV0_EPF4_*` offsets. In the offset header, the config-register names omit this file's `_0` infix, so code and generated helper macros must use the naming convention expected by their access macro layer rather than manually mixing arbitrary names.

The direct in-tree include site is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes both `nbio_7_7_0_offset.h` and `nbio_7_7_0_sh_mask.h`. That implementation uses NBIO register helpers to read revision IDs, configure memory-controller access, program doorbell apertures and ranges, set interrupt controls, configure HDP flush/remap offsets, control clock-gating/light-sleep behavior, and handle PCIe master-control setup. This particular chunk's EPF2-EPF4 PCIe capability fields are mostly generated register ABI surface for endpoint-function config decoding/programming, diagnostics, and future feature paths rather than a dense local call graph in `nbio_v7_7.c`.

Other integration points are architectural:

- Linux PCI/PCIe semantics for standard config-space fields, power management, MSI/MSI-X, PCIe capability structures, AER, resizable BAR, power budget, DPA, ACS, PASID, and ARI.
- AMDGPU register access helper macros such as `REG_GET_FIELD` and `REG_SET_FIELD`, which expect the generated `__SHIFT` and `_MASK` naming pattern.
- Debug tools or register dump decoders that need stable symbolic names to interpret NBIO 7.7.0 EPF2/EPF3/EPF4 configuration images.
- Reset, suspend/resume, PCIe error-recovery, interrupt, and virtualization code that may rely on these fields if it inspects or restores endpoint-function configuration state.

## Risks

- Generated-header drift: offsets, shift/mask headers, and any default-value headers must come from the same NBIO 7.7.0 hardware database revision. Mismatched files can compile while decoding or writing the wrong bits.
- Naming mismatch hazards: this shift/mask header uses `BIF_CFG_DEV0_EPF<n>_0_*` while the offset header exposes `cfgBIF_CFG_DEV0_EPF<n>_*` for these blocks. Manual code that constructs names or pairs fields by string can get this wrong.
- Function-prefix confusion: EPF2, EPF3, and EPF4 repeat many identical field layouts. Reusing an EPF3 mask with an EPF4 offset, or vice versa, may silently target the wrong endpoint-function image.
- Chunk-boundary incompleteness: EPF2 starts before this range, and EPF4 continues after it. Merge/reconciliation must avoid treating the partial EPF2 opening or EPF4 closing AER group as complete.
- Write-sensitive fields: command, BAR, ROM, device control, link control, MSI/MSI-X control, AER mask/severity, resizable BAR control, DPA control, ACS, PASID, and ARI fields can change enumeration, routing, interrupt delivery, isolation, or link behavior if programmed incorrectly.
- Status/log side effects: PCI status, device status, AER status, PME status, MSI pending, header logs, and TLP prefix logs may be latched or write-one-to-clear. The masks identify bits but do not make clearing them safe.
- Diagnostic misclassification: incorrect AER status, mask, or severity definitions can hide real PCIe faults, report the wrong first-error class, or confuse recovery and RAS analysis.
- Virtualization and isolation exposure: ACS, PASID, ARI, and resizable BAR fields affect peer-to-peer routing, address-space tagging, and multi-function behavior. Stale or mismatched masks can undermine assumptions made by IOMMU or SR-IOV-adjacent code.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, generator-level, and hardware-observation checks:

- AMDGPU builds with NBIO 7.7.0 support enabled and `nbio_v7_7.c` including both generated headers.
- Static consistency checks verify that each complete field has a correctly aligned shift/mask pair and that masks match their declared shift and width.
- Generated-header checks confirm that EPF2, EPF3, and EPF4 register groups represented here have matching offsets in `nbio_7_7_0_offset.h`, accounting for the `_0` naming convention difference.
- Register dump decoders produce plausible EPF2/EPF3/EPF4 PCI command/status, class, BAR, capability-list, PCIe device/link status, MSI/MSI-X, AER, resizable BAR, DPA, ACS, PASID, and ARI values on matching hardware.
- PCIe link diagnostics decode coherent speed, width, training state, common-clock state, data-link-active state, link bandwidth status, equalization status, DRS fields, and supported-speed vectors.
- Interrupt validation confirms MSI/MSI-X enable, table, PBA, message-address/data, mask, and pending fields agree with Linux PCI state and working interrupt delivery.
- AER/RAS validation or fault-injection, where available, maps correctable and uncorrectable status bits, masks, severities, header logs, and TLP prefix logs to expected PCIe error classes.
- Reset, suspend/resume, and FLR testing confirms higher-level code restores writable PCIe, MSI/MSI-X, BAR, AER, DPA, ACS, PASID, and ARI state as needed rather than relying on this header for defaults.

## Research Notes

This chunk is a dense generated hardware-description slice. Its engineering value is exact symbolic alignment: the repeated EPF2/EPF3/EPF4 endpoint-function masks must remain synchronized with the NBIO 7.7.0 offset map and hardware register database. The highest-risk review areas are not algorithms, but repetition, naming, and boundary handling: similar endpoint functions must not be cross-wired, and partial register families at the chunk edges must be merged with their neighbors before whole-file conclusions are drawn.
