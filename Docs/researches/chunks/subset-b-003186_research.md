# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 63516-65981

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.2 register field mask header. It provides preprocessor constants for bit shifts and masks used to decode or update fields in NBIO PCIe configuration registers for `BIF_CFG_DEV1_EPF0_0` and the beginning of `BIF_CFG_DEV1_EPF1_0`.

The assigned span starts in the middle of the `BIF_CFG_DEV1_EPF0_0` PCI configuration-space map, immediately after the `BASE_CLASS` field that began before this chunk. It then covers the rest of EPF0 through PCIe 4.0/16GT lane equalization and lane margining fields, switches at the `addressBlock: nbio_nbif0_bif_cfg_dev1_epf1_bifcfgdecp` marker, and covers EPF1 from vendor/device identity through the start of its vendor-specific extended capability list.

These definitions are not executable logic. They are an ASIC-specific hardware ABI: sibling offset macros name the register addresses, while this file names the bit layout consumed by AMDGPU register helpers.

## Covered Register Areas

- EPF0 standard PCI configuration fields: cache line size, latency timer, header type, BIST, BAR1 through BAR6, CardBus CIS pointer, subsystem/vendor adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, max latency, vendor capability list, and writable adapter ID mirror.
- EPF0 power-management and PCIe capability fields: `PMI_CAP_LIST`, `PMI_CAP`, `PMI_STATUS_CNTL`, USB-like `SBRN`/`FLADJ`/`DBESL_DBESLD`, PCIe capability header, device capability/control/status, link capability/control/status, and PCIe capability version-2 device/link registers.
- EPF0 interrupt capabilities: MSI and MSI-X capability list entries, message control, 32-bit and 64-bit message address/data fields, per-vector mask/pending fields, MSI-X table descriptor, and MSI-X PBA descriptor.
- EPF0 PCIe extended capabilities: vendor-specific capability header/scratch registers, virtual-channel resources, Advanced Error Reporting status/mask/severity/logging, resizable/enhanced BAR controls for BAR1 through BAR6, power budgeting, dynamic power allocation, secondary PCIe capability, ACS, PASID, LTR, ARI, TPH requester, data link feature, 16GT PHY, and margining capability registers.
- EPF0 per-lane arrays: `PCIE_LANE_0..15_EQUALIZATION_CNTL`, `LANE_0..15_EQUALIZATION_CNTL_16GT`, and `LANE_0..15_MARGINING_LANE_CNTL/STATUS`. The chunk exposes each lane as separate macro names rather than an indexed table.
- EPF1 standard PCI/PCIe function fields: vendor/device ID, command/status, class/revision fields, BARs, adapter ID, ROM BAR, capability pointer, interrupt fields, power-management capability, PCIe capability, device/link capability/control/status including version-2 fields, MSI/MSI-X fields, and the first macro of `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`.

## Important APIs, Types, and Functions

This chunk defines no C functions, structs, enums, variables, or inline helpers. Its public API is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: the bit offset for a field.
- `<REGISTER>__<FIELD>_MASK`: the mask for the field at its register position.

The practical consumers are AMDGPU register helper macros and accessors such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_*`, `WREG32_*`, and SOC15/NBIO register offset helpers. For example, code pairs a register address from `nbio_7_2_0_offset.h` with the matching field shift/mask from this file to extract status bits or construct read-modify-write values.

## Control Flow

There is no runtime control flow in the header. Its effective flow is compile-time substitution:

1. Driver code selects a `regBIF_CFG_DEV1_EPF0_0_*` or `regBIF_CFG_DEV1_EPF1_0_*` offset from `nbio_7_2_0_offset.h`.
2. It reads the current hardware/config-space dword or prepares a new register value.
3. It applies this chunk's `__SHIFT` and `_MASK` constants through field helpers or manual bit operations.
4. Writable control fields are written back through the selected NBIO/PCIe access path.

The runtime behavior belongs to the caller and to NBIO hardware. This header only encodes the bit positions that make those accesses meaningful.

## State and Persistence Behavior

The file itself has no state and persists nothing. The named fields correspond to hardware-backed PCIe configuration and extended-capability state:

- Identity, class-code, capability, supported-speed, supported-width, AER capability, ACS/PASID/LTR/ARI/TPH capability, power-budget, DPA capability, data-link feature capability, PHY 16GT capability, and margining capability fields are generally read-only or firmware/strap-derived capability reports.
- Control fields such as PCI command, power state, PME enable, PCIe device/link control, completion-timeout control, MSI/MSI-X enable/mask state, virtual-channel control, AER masks/severity, BAR control, DPA control, link control 3, lane equalization controls, ACS/PASID/ARI/TPH controls, data-link feature control, 16GT link controls, and margining lane controls are mutable hardware state.
- Status and log fields such as PCI status, device/link status, MSI pending bits, VC status, AER uncorrectable/correctable status, AER header/TLP prefix logs, DPA status, lane error status, 16GT link/equalization/parity status, and margining lane status are hardware-reported and may be latched or clear-on-write depending on the PCIe/NBIO specification.
- Persistence across reset, function-level reset, suspend/resume, hot reset, or GPU reset is hardware-defined. The macros do not encode reset values, access permissions, or write-one-to-clear semantics.

## Dependencies

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h`: supplies the paired register offsets and base indices. A shift/mask macro is only meaningful with the matching register address macro.
- AMDGPU SOC15/NBIO register access infrastructure: provides the read/write and field helper macros that consume this generated naming scheme.
- PCI and PCIe architectural register definitions: many names mirror standard configuration-space, MSI/MSI-X, PCIe capability, AER, ACS, PASID, LTR, ARI, TPH, DPA, data-link feature, PHY 16GT, and lane margining concepts.
- AMD NBIO 7.2 hardware generation: the numeric masks and shifts are ASIC-specific and must match the NBIO 7.2 register specification.

## Integration Points

- The AMDGPU NBIO 7.2 implementation includes this generated header alongside the matching offset header for NBIO-specific setup and register manipulation.
- The EPF0/EPF1 prefixes identify separate endpoint-function register maps under NBIF device 1. Callers must not mix an EPF0 field macro with an EPF1 offset or with another NBIO generation.
- Standard PCIe integration includes enumeration identity, BAR sizing/programming, command/status bits, interrupt routing, MSI/MSI-X programming, power management, link speed/width negotiation, AER reporting, ACS/PASID/LTR/ARI/TPH features, and lane-level diagnostics.
- The repeated lane and TPH table definitions are expressed as independent macro names. Any caller that iterates lanes or table entries has to map indexes to explicit register symbols or generate those names at compile time; there is no array in this header.

## Risks and Edge Cases

- The chunk begins mid-register: `BIF_CFG_DEV1_EPF0_0_BASE_CLASS__BASE_CLASS_MASK` is present while the matching shift definition is just before line 63516. Merge logic should preserve adjacent context.
- The chunk ends mid-register-family: `BIF_CFG_DEV1_EPF1_0_PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST` continues after line 65981 with its remaining masks and subsequent EPF1 extended capabilities.
- Some offset registers share a dword while this header exposes byte/word/nibble fields. Callers must use the correct access width and preserve unrelated fields during read-modify-write operations.
- Status and error bits may have side effects on write. Blindly writing full masks to PCI status, AER status, MSI pending, link status, or margining status fields can clear diagnostics or acknowledge events unintentionally.
- EPF0 and EPF1 definitions are highly repetitive. Copy/paste mistakes across endpoint-function prefixes, lane numbers, 16GT vs generic equalization fields, or control vs status fields can silently program the wrong hardware.
- Full-width masks such as BARs, header logs, TLP prefix logs, scratch registers, MSI masks, and table offsets should be treated as multi-bit values, not boolean flags.
- Capability fields do not imply writability. The header gives bit layout only; access permissions and reset defaults must come from the PCIe specification or AMD register documentation.

## Test Signals

- Build signal: references to these macros should compile when AMDGPU NBIO 7.2 code includes `nbio_7_2_0_sh_mask.h` with the matching offset header.
- Static validation signal: compare each register prefix and field pair against `nbio_7_2_0_offset.h` and the generated AMD NBIO 7.2 register specification, especially at shared dword offsets and the EPF0/EPF1 boundary.
- Runtime signal: successful PCIe enumeration, correct BAR assignment, working bus mastering/DMA, correct MSI/MSI-X delivery, stable link speed/width negotiation, and clean amdgpu initialization logs indicate that consumed config fields are coherent.
- Error-reporting signal: `lspci -vv`, kernel AER logs, DRM/amdgpu logs, link retraining reports, and GPU reset logs can expose mismatches in PCIe capability, AER, DPA, ACS/PASID/LTR/ARI/TPH, or MSI/MSI-X fields.
- Stress signal: suspend/resume, hot reset/function-level reset, high-throughput DMA, interrupt stress, PCIe link speed transitions, lane equalization diagnostics, and lane margining tests are relevant because this chunk covers mutable power, link, interrupt, error, and per-lane control/status state.
