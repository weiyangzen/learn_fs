# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 61074-63526

## Scope

This chunk is a generated AMDGPU NBIO 7.7.0 shift/mask header segment. It contains preprocessor constants only: no functions, structs, enums, executable statements, allocations, locks, or software-owned storage. The assigned range has 2,143 `#define` lines over 2,453 source lines and describes 301 commented register groups.

The range begins in the middle of the `BIF_CFG_DEV2_EPF0_0` endpoint-function lane-margining area, starting with the final field of lane 4 control and then covering lanes 4-15 status plus lanes 5-15 control/status. It then covers complete field layouts for `BIF_CFG_DEV2_EPF1_0`, complete field layouts for `BIF_CFG_DEV2_EPF2_0`, and ends in the early `BIFPLR0_0` bridge/root-port-style block at `BIFPLR0_0_DEVICE_CNTL`. Adjacent chunks are required for the beginning of EPF0 lane 4 control and the remainder of `BIFPLR0_0`.

Although the repository path is under a Ceph source mirror, this file is AMDGPU hardware register metadata. It has no distributed-filesystem or Ceph-specific behavior.

## Purpose

`nbio_7_7_0_sh_mask.h` is the field-geometry half of AMD's generated NBIO 7.7.0 register interface. For each register field, it publishes two macros:

- `...__SHIFT`, the bit position for the field.
- `..._MASK`, the register mask for the field after shifting.

Driver code combines these constants with register offsets from `nbio_7_7_0_offset.h` and with AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, SOC15 MMIO accessors, or PCIe config accessors. This chunk therefore describes how to interpret or modify individual bits in PCI/PCIe configuration-space windows for NBIO device 2 endpoint functions and the beginning of a BIFPLR bridge block.

## Register Families

The EPF0 tail is dedicated to PCIe lane margining. For lanes 5-15, each `BIF_CFG_DEV2_EPF0_0_LANE_N_MARGINING_LANE_CNTL` register has fields for receiver number, margin type, usage model, and margin payload. Each matching `LANE_N_MARGINING_LANE_STATUS` register exposes the corresponding returned status fields. Lane 4 is partial in this chunk: the first visible line is only `LANE_4_MARGIN_PAYLOAD_MASK`, followed by the full lane 4 status layout.

The `BIF_CFG_DEV2_EPF1_0` and `BIF_CFG_DEV2_EPF2_0` blocks repeat a full endpoint PCI/PCIe configuration-space field layout. They include conventional PCI identity and header fields, BAR fields, subsystem/vendor IDs, capability-list pointers, power-management capability/status-control, SBRN/FLADJ/DBESL, PCIe device/link capability and control/status, PCIe capability 2 registers, MSI and MSI-X capability fields, vendor-specific enhanced capability fields, Advanced Error Reporting fields, TLP header and prefix logs, enhanced BAR controls, power-budgeting, dynamic power allocation, ACS, PASID, and ARI capability/control fields.

The `BIFPLR0_0` portion starts a PCIe bridge/root-port-style layout. In this chunk it covers vendor/device ID, command/status, revision/class/header bytes, bus-number and latency fields, I/O and memory base/limit windows, prefetchable memory upper/base/limit windows, capability pointer, ROM base, interrupt line/pin, a small extended bridge control, vendor/subsystem ID fields, PM capability/status-control, PCIe capability header, device capability, and the beginning of device control.

## Important APIs, Types, And Functions

There are no callable APIs or C types here. The public interface is the macro namespace itself:

- `BIF_CFG_DEV2_EPF0_0_LANE_*_MARGINING_*__*` gives per-lane PCIe margining field geometry.
- `BIF_CFG_DEV2_EPF1_0_*__*` gives field geometry for endpoint function 1 under device 2.
- `BIF_CFG_DEV2_EPF2_0_*__*` gives field geometry for endpoint function 2 under device 2.
- `BIFPLR0_0_*__*` gives field geometry for the beginning of a bridge/root-port config block.

The macros are untyped integer literals. They do not carry access width, reset value, read/write permission, reserved-bit policy, write-one-to-clear semantics, firmware ownership, or sequencing constraints. Those rules come from the PCI/PCIe specifications, AMD's NBIO register database, firmware contracts, and the consuming AMDGPU code.

## Control Flow

This header has no local runtime control flow. Runtime flow is imposed by consumers:

1. ASIC-specific AMDGPU code includes `nbio_7_7_0_sh_mask.h`, usually together with `nbio_7_7_0_offset.h`.
2. Code selects a register offset macro from the offset header and one or more field macros from this header.
3. Read paths apply the mask and shift to extract a field value.
4. Write paths generally read the register, clear the masked field, insert a shifted value, and write the updated register while preserving unrelated bits.
5. Hardware, firmware, and PCI/PCIe semantics determine whether the access changes configuration state, clears a sticky error, starts link activity, updates interrupt routing, or simply reads status.

For this exact slice, typical logical flows include decoding endpoint identity and capability lists, enabling PCI command bits, programming BAR or enhanced BAR sizing, configuring MSI/MSI-X state, observing or masking AER conditions, managing PCIe power-management fields, controlling ACS/PASID/ARI bits, and reading lane margining or link status fields.

## State And Persistence Behavior

The header stores no software state and persists nothing itself. It names hardware-backed PCI/PCIe configuration fields.

State represented by this chunk includes endpoint identity, class code, BAR attributes, subsystem IDs, capability list topology, PM state and PME status, PCIe device/link capabilities, payload and read-request sizing, link speed/width and training status, completion timeout and atomic-operation controls, MSI/MSI-X routing data and masks, AER status/mask/severity bits, captured TLP headers/prefixes, power-budget and DPA values, ACS isolation controls, PASID controls, ARI function-group fields, lane margining command/status payloads, and bridge I/O/memory/prefetchable decode windows.

Persistence is hardware-defined. Some values are strap or firmware initialized, some are OS PCI enumeration state, some are writable configuration controls, and some are hardware-updated or sticky status/log registers. Values may reset differently across cold boot, warm reset, PCIe hot reset, function-level reset, GPU reset, BACO, suspend/resume, runtime power transitions, and driver reinitialization. AER status/log fields, MSI/MSI-X masks and pending bits, PM status/control, BAR sizing state, and lane margining controls are especially sensitive to reset and ownership sequencing.

## Dependencies And Integration Points

The direct sibling dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h`, which supplies the register addresses for the fields described here. The mask and offset headers must stay synchronized by register name, block prefix, and field layout.

The main NBIO 7.7 consumer in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes this header and wires NBIO 7.7 register behavior into AMDGPU through `nbio_v7_7_funcs` and related RAS/HDP/doorbell helpers. That file uses other masks from this same generated header family directly, and broader AMDGPU PCIe, RAS, interrupt, reset, virtualization, and power-management code can rely on the field definitions when addressing the corresponding config decode windows.

Semantic dependencies include conventional PCI configuration space, PCI Express capability layout, MSI/MSI-X, Advanced Error Reporting, Access Control Services, Process Address Space ID, Alternative Routing-ID Interpretation, dynamic power allocation, power budgeting, PCIe link equalization, and lane margining. The header does not document which capabilities are enabled on every ASIC or which fields are owned by firmware versus the OS driver.

## Risks And Edge Cases

- The chunk starts and ends mid-logical-block. Lane 4 margining control and most of `BIFPLR0_0` are outside this range, so whole-file conclusions must merge adjacent chunks.
- EPF1 and EPF2 are highly repetitive. Prefix mistakes can compile cleanly while targeting the wrong endpoint function's field layout.
- Many PCI config fields share the same register dword. Consumers must use the exact shift/mask pair and preserve unrelated fields during read/modify/write.
- `*_MASK_MASK` names in AER mask registers are generated from field names ending in `_MASK`; they are intentional but easy to misread in manual review.
- AER status, mask, and severity fields may be sticky, write-one-to-clear, or interrupt-affecting depending on the register. Treating them as ordinary read/write fields can hide PCIe errors or create spurious error reporting.
- MSI/MSI-X address, data, mask, table, and PBA fields affect interrupt delivery. Incorrect programming can produce lost interrupts, interrupt storms, or broken function isolation.
- BAR and enhanced BAR control fields affect PCI resource sizing and decode. Wrong sizes or indexes can break enumeration, MMIO placement, or VF/PF resource layout.
- ACS, PASID, and ARI fields affect isolation, routing, and address-space semantics. Incorrect enablement can affect IOMMU behavior or peer-to-peer access policy.
- Lane margining fields are diagnostic/control surfaces for PCIe link health. Writes during active traffic or outside documented margining flows can disturb link diagnostics or training assumptions.
- Bridge-window fields in `BIFPLR0_0` define I/O, memory, and prefetchable decode ranges. Incorrect masks or shifts can route traffic incorrectly once consumed by bridge programming code.
- Generated header drift is silent at compile time if symbol names remain present but numeric masks or shifts change incorrectly.

## Test Signals

Useful validation for this chunk combines generated-header checks with AMDGPU hardware behavior:

- Build AMDGPU with NBIO 7.7 support enabled so include sites catch missing or malformed symbols.
- Compare this chunk against AMD's authoritative NBIO 7.7.0 register database and the adjacent generated offset header.
- Mechanically verify that every visible field has both `__SHIFT` and `_MASK` definitions, except where the chunk boundary intentionally exposes only the tail of lane 4 control.
- Check that repeated EPF1 and EPF2 field layouts match where the hardware register database expects identical endpoint-function capability maps.
- Validate that shared-dword PCI config fields use non-overlapping masks and expected shifts for vendor/device, command/status, class-code bytes, device/link control/status, and MSI/MSI-X capability fields.
- Exercise boot, PCI enumeration, GPU reset, FLR, suspend/resume, runtime power management, and PCIe link retraining on NBIO 7.7 hardware.
- Inspect `lspci -vvv` and kernel logs for stable BAR sizing, MSI/MSI-X enablement, PCIe capability decoding, AER reporting, ACS/PASID/ARI visibility, and link speed/width status.
- Run SR-IOV or virtualization coverage where endpoint functions and PASID/ARI/ACS state are exposed; check VF enumeration, interrupt delivery, isolation, and FLR recovery.
- Use PCIe error-injection or platform AER diagnostics where available to confirm uncorrectable/correctable status, mask, severity, and header-log fields decode correctly.
- Use link diagnostics or vendor tools for lane margining/equalization where available, especially lanes 4-15 in the EPF0 tail covered here.

## Cross-Chunk Notes

The previous chunk owns the beginning of `BIF_CFG_DEV2_EPF0_0_LANE_4_MARGINING_LANE_CNTL` and earlier EPF0 registers. The next chunk owns the rest of `BIFPLR0_0` after `DEVICE_CNTL`, including later bridge/device/link status, extended capabilities, AER, and any higher-speed or lane-specific fields. The final per-file report should reconcile these boundaries before making complete statements about EPF0 lane margining or the full `BIFPLR0_0` block.
