# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 24687-27116

## Purpose

This chunk is an auto-generated AMD NBIO 7.11.0 shift/mask slice for PCI and PCIe configuration-space registers. It begins inside `BIF_CFG_DEV0_RC0_COMMAND`, covers the rest of the `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` root-complex configuration decode block, then starts the `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` endpoint/function block and runs through the first field of `BIF_CFG_DEV0_EPF0_0_PCIE_BAR1_CAP`.

The file does not implement executable logic. Its interface is a large set of C preprocessor constants used by AMDGPU NBIO code to extract or compose hardware register fields alongside the companion `nbio_7_11_0_offset.h` register-address macros.

## Public Surface In This Chunk

The exported API is the generated register-field convention:

- `REGISTER__FIELD__SHIFT` gives the bit position of a field.
- `REGISTER__FIELD_MASK` gives the raw bit mask for that field.

This range contains 2,147 `#define` lines spanning 281 register names. The root-complex portion covers `BIF_CFG_DEV0_RC0_*` standard PCI header, bridge window, PM, PCIe, MSI, SSID, vendor-specific, virtual-channel, serial-number, AER, secondary PCIe, lane equalization, ACS, data-link feature, 16 GT/s PHY, margining, and RTR capability fields. The endpoint/function portion covers `BIF_CFG_DEV0_EPF0_0_*` standard PCI header, BARs, adapter ID, PM, PCIe, MSI/MSI-X, vendor-specific, virtual-channel, serial-number, AER, header logs, TLP prefix logs, and the BAR enhanced capability header.

The range starts after the `BIF_CFG_DEV0_RC0_COMMAND` comment and after the preceding chunk's vendor/device ID definitions. It ends at `BIF_CFG_DEV0_EPF0_0_PCIE_BAR1_CAP__BAR_SIZE_SUPPORTED__SHIFT`; the matching mask and later BAR capability/control fields are in the following chunk.

## Important Register Families

The `BIF_CFG_DEV0_RC0` block models a PCIe root complex or bridge-style configuration space. Its standard header fields include command/status bits, class-code bytes, cache-line and latency fields, bridge bus numbering, IO/memory/prefetchable window registers, interrupt line/pin, and bridge control bits such as secondary bus reset, VGA/ISA forwarding, SERR, parity response, and discard timer status. These masks are the low-level layout used when code needs to decode the NBIO root-complex configuration image rather than relying only on generic PCI helpers.

The RC0 power and interrupt capabilities include PM capability list, PM capability/status-control, MSI message control/address/data, SSID, and MSI-map capability fields. PCIe base capability fields cover device capability/control/status, link capability/control/status, slot and root capability/control/status, and PCIe 2.0 `DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` fields. These names expose common controls and state such as max payload size, relaxed ordering, no-snoop, error reporting enables, function-level reset, target link speed, retraining, ASPM, negotiated link width/speed, equalization state, and root PME/error status.

The RC0 extended capability groups include vendor-specific headers and payload registers, virtual-channel capability/control/status and VC0/VC1 resource control/status, device serial number doublewords, and Advanced Error Reporting. AER fields define uncorrectable status/mask/severity bits for data link protocol, surprise-down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned TLP egress blocked. Correctable AER fields cover receiver errors, bad TLP/DLLP, replay rollover, replay timer timeout, advisory non-fatal, and correctable internal errors. Header-log and TLP-prefix-log registers are full-width fields.

The RC0 secondary PCIe and link-training groups define `LINK_CNTL3`, lane error status, per-lane equalization controls for lanes 0-15, 16 GT/s equalization controls, local/RTM parity mismatch status, lane margining control/status for lanes 0-15, ACS capability/control bits, data-link feature capability/status, PHY 16 GT/s capability/control/status, and RTR capability/data fields. These are integration points for link bring-up, diagnostics, PCIe Gen4/16 GT/s training, lane margining, isolation policy, and data-link feature reporting.

The `BIF_CFG_DEV0_EPF0_0` block starts at the generated address-block marker for endpoint function 0. It defines endpoint-style vendor/device ID, command/status, revision and class-code bytes, cache/latency/header/BIST, six BAR registers, adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant/max latency, vendor capability list, and writable adapter ID fields. Its PM and PCIe capability fields mirror endpoint-facing state: PM state/PME control, PCIe device/link capabilities and controls, PCIe 2.0 capabilities, MSI message controls and mask/pending registers, MSI-X table/PBA fields, vendor-specific extended capability, virtual channel resources, serial number, and AER status/mask/severity/log controls.

The EPF0 chunk ends in the BAR enhanced capability list and the first `BAR1_CAP` shift. The corresponding offset header places this block at base address `0x10140000` with `regBIF_CFG_DEV0_EPF0_0_PCIE_BAR_ENH_CAP_LIST` at `0x10080` and `regBIF_CFG_DEV0_EPF0_0_PCIE_BAR1_CAP` at `0x10081`, both using base index 5.

## Control Flow And State

There is no runtime control flow in this header slice. The effective flow is compile-time macro substitution:

1. A translation unit includes `nbio_7_11_0_offset.h` and `nbio_7_11_0_sh_mask.h`.
2. Driver code obtains a raw register value using an AMDGPU register access helper and a `reg...` offset macro from the offset header.
3. The caller uses `REG_GET_FIELD`, `REG_SET_FIELD`, direct mask/shift arithmetic, or similar AMDGPU helper patterns to decode or construct a field value from the generated `*_MASK` and `*__SHIFT` constants.

The header stores no C state and has no persistence layer. Persistent state is the hardware state in NBIO PCI/PCIe configuration registers. Many fields in this chunk represent state that can outlive a single register read: bridge apertures, bus numbering, BAR sizing, PM state, MSI/MSI-X routing, link speed/width and equalization state, AER mask/status/severity, VC allocation, ACS policy, lane margining results, and BAR enhanced capability support.

Some hardware status fields may be latched or write-one-to-clear according to their PCIe/NBIO semantics. This header only names bit positions; it does not encode access permissions, side effects, reset values, valid value ranges, or sequencing requirements.

## Dependencies And Integration Points

The direct companion for this chunk is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_offset.h`. That header defines the corresponding `regBIF_CFG_DEV0_RC0_*` offsets under `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` with base address `0x10100000`, and `regBIF_CFG_DEV0_EPF0_0_*` offsets under `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` with base address `0x10140000`. This directory has `nbio_7_11_0_offset.h` and `nbio_7_11_0_sh_mask.h`; unlike some nearby NBIO generations, there is no visible `nbio_7_11_0_default.h` in this tree.

The only direct C include found for this exact header is `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c`, which includes both `nbio/nbio_7_11_0_offset.h` and `nbio/nbio_7_11_0_sh_mask.h`. That file uses the same generated macro family through AMDGPU register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and `REG_SET_FIELD`, although this specific chunk is primarily PCI/PCIe configuration-space layout rather than doorbell or HDP helper logic.

The semantic dependencies are the PCI and PCI Express specifications for standard configuration headers, bridge windows, PM capability, MSI/MSI-X, PCIe capability, AER, virtual channels, secondary PCIe/link equalization, ACS, data-link feature capability, 16 GT/s PHY capability, lane margining, RTR, vendor-specific capability layout, and BAR enhanced capability layout. The generated names encode those layouts but do not validate legal combinations.

## Risks And Maintenance Notes

- The assigned range is a partial slice: it starts after the `BIF_CFG_DEV0_RC0_COMMAND` register comment and ends before the complete `BIF_CFG_DEV0_EPF0_0_PCIE_BAR1_CAP` definition. Adjacent chunks are required for a whole-register view at both boundaries.
- Masks and shifts are hardware ABI. A one-bit drift between this file and NBIO 7.11.0 silicon, firmware tables, or the offset header can silently decode the wrong PCIe state or program the wrong control bit.
- Several fields control externally visible PCIe behavior: bus mastering, memory enable, bridge apertures, PM/PME state, MSI/MSI-X routing, link retrain/target speed, AER masking/severity, ACS isolation, VC resource negotiation, lane equalization, lane margining, and BAR sizing. Incorrect writes can affect enumeration, DMA, interrupt delivery, error containment, isolation, or link stability.
- Status and error fields in AER, link status, lane error, parity mismatch, margining status, and root status may have side effects when cleared. The presence of a mask does not imply that a read-modify-write is safe.
- Cross-generation similarity is high but not exact. Nearby NBIO headers show differences such as the presence or absence of certain command bits and BAR mask widths, so these constants should not be reused for other NBIO versions.
- Full-width masks such as `0xFFFFFFFFL` and high-bit masks such as `0xFFF00000L` rely on the established AMDGPU unsigned 32-bit register-helper context. Ad hoc use in signed or narrower expressions can introduce truncation or sign-extension bugs.
- The repetitive lane and AER definitions are generation output, making manual review error-prone. Automated structural checks are more reliable than visual inspection for verifying shift/mask alignment.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage for `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c` and any SOC paths that include the NBIO 7.11.0 offset and shift/mask headers.
- Static checks that every complete field in the chunk has a matching `*_MASK` and `*__SHIFT` pair, with the expected alignment between mask low bit and shift value. The known exception at this chunk boundary is `BIF_CFG_DEV0_EPF0_0_PCIE_BAR1_CAP__BAR_SIZE_SUPPORTED__SHIFT`, whose mask is outside the assigned range.
- Cross-header checks that each complete `BIF_CFG_DEV0_RC0_*` and `BIF_CFG_DEV0_EPF0_0_*` register family in this range has a matching `reg...` offset and `_BASE_IDX` in `nbio_7_11_0_offset.h`.
- Runtime PCIe/NBIO dumps on NBIO 7.11 hardware comparing decoded vendor/device IDs, command/status, class code, BARs, bus windows, PM state, MSI/MSI-X state, negotiated link speed/width, PCIe 2.0 controls, AER masks/status, VC resources, ACS controls, lane equalization, 16 GT/s state, margining results, and BAR enhanced capability fields against `lspci -vvxxx` and AMDGPU debug register reads.
- Error-path validation that AER status/mask/severity and header/TLP-prefix logs are decoded and cleared with the intended bits only.
- Link-training and power-management tests around retrain-link, target-speed changes, equalization completion, lane error reporting, 16 GT/s status, lane margining commands/status, PME, and low-power link states.
