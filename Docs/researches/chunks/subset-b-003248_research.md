# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h lines 4877-7378

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.7.0 register-offset header. It provides C preprocessor constants that map NBIO/BIF/RCC/SION register names to DWORD-style offsets plus a companion `_BASE_IDX` value used by AMDGPU register-access macros to select the correct register aperture/base.

The range contains 2,502 source lines and 2,394 `#define` entries: 1,197 register-offset macros and 1,197 `_BASE_IDX` macros. The count is balanced only because the chunk starts on `regBIF_CFG_DEV2_RC0_SLOT_CNTL2_BASE_IDX` without the matching offset in this chunk and ends on `regBIF_CFG_DEV0_EPF0_0_PCIE_PASID_CNTL` before its `_BASE_IDX` appears. Most base indices in this chunk are `5`, matching the NBIO aperture used by these generated headers.

At a high level, the chunk covers:

- The tail of the `BIF_CFG_DEV2_RC0` root-complex PCI/PCIe configuration image, starting at slot control/status 2 and continuing through MSI, subsystem ID, vendor-specific, VC, device serial number, AER/root error, lane equalization, ACS, DLF, 16 GT/s PHY, and lane margining offsets.
- NBIF/BIF system and PF/VF decode registers around the `0x10120000` base, including MM/PCIE index-data windows, S/BIOs scratch registers, BIF interrupt controls, GFX MMIO remap CAMs, doorbell/FB/remap/VF windows, BACO controls, power-break, PERST, scratch, and mailbox registers.
- RCC strap, endpoint, downstream, downstream-port, and device blocks for device 0/1/2, including per-function strap registers, common/device/endpoint/downstream controls, LTR/VDM/margining registers, and bus/device-number programming.
- BIF miscellaneous, reset, power, D-state, FLR, interrupt, RAS, SION arbitration/credit, and SDP/SMN virtual-wire control offsets.
- The beginning of the `BIF_CFG_DEV0_EPF0_0` endpoint-function PCI configuration image, from vendor/device identity through the first PASID capability/control offset.

The file is not executable code and has no Ceph or distributed-filesystem behavior despite its mirrored source-tree location. It is a generated hardware register contract for AMDGPU NBIO 7.7.0 code.

## Important APIs, Types, and Macros

There are no functions, structs, typedefs, or enums in this chunk. The only API surface is the generated macro convention:

- `reg<REGISTER_NAME>` gives the register offset within the address block selected by the generated base index.
- `reg<REGISTER_NAME>_BASE_IDX` gives the base-index selector passed to AMDGPU register helpers for the same register.

Important visible register families include:

- `regBIF_CFG_DEV2_RC0_*`: PCIe root-complex configuration-space offsets for device 2, root complex 0. The visible portion includes MSI message registers, SSID and MSI-map capability registers, PCIe vendor-specific and VC capabilities, device serial number, AER status/mask/severity/logs, root error command/status/source ID, TLP prefix logs, secondary PCIe capability, per-lane equalization, ACS, DLF, 16 GT/s capability/control/status, retimer/local parity mismatch status, 16 GT/s per-lane equalization, lane margining port status, and lane 0-15 margining control/status.
- `regBIF_BX_PF1_*` and `regBIF_BX1_*`: BIF indirect access, scratch, interrupt, MMIO remap, doorbell, FB, BACO, power-management, mailbox, and per-client BIF control offsets. These are internal NBIF/BIF control-plane registers rather than PCI capability registers.
- `regRCC_STRAP1_*`, `regRCC_STRAP2_*`, `regRCC_DEV*_EPF*_*`, `regRCC_DEV*_PORT_*`, `regRCC_EP_*`, `regRCC_DWN_*`, and `regRCC_DWNP_*`: reset/control/configuration straps and RCC port/endpoint/downstream registers for multiple devices and functions. These encode hardware-visible function identity, link/endpoint behavior, LTR, margining, VDM, bus numbering, and downstream-port controls.
- `regBIFC_*`, `regNBIF_*`, `regINTR_*`, `regBIF_*`, `regDEV*_PF*_*`, and `regSELF_SOFT_RST*`: miscellaneous BIF/NBIF controls for interrupt polarity/enable, outstanding VC allocation, DMA attribute overrides, PASID checking/status, performance counters, SDP/GMI/HSTARB/SMN controls, power and D-state interrupts, per-function D3hot/D0 and FLR reset controls, reset misc controls, and function D-state values.
- `regBIFL_RAS_*`: BIF leaf and central RAS control/status registers plus IOHUB RAS interrupt handling and virtual-wire forwarding offsets.
- `regSION_*`: SION client arbitration, burst target, time-slot, request/data/read-response/write-response pool credit allocation, and top-level SION control registers for clients 0-2.
- `regBIF_CFG_DEV0_EPF0_0_*`: endpoint-function PCI configuration-space offsets for device 0 EPF0. The visible range includes conventional PCI header fields, BARs, ROM BAR, capability pointer, interrupt/min-grant/max-latency fields, vendor/PM/PCIe capabilities, MSI/MSI-X, vendor-specific capability, VC capability/resource registers, device serial number, AER logs, BAR enhanced capability, power budget, DPA, secondary PCIe capability, per-lane equalization, ACS, ATS, page request, outstanding page request, and the start of PASID.

These offset macros are normally paired with the sibling `nbio_7_7_0_sh_mask.h` field definitions. Offset macros choose the register; shift/mask macros choose fields within the register value.

## Control Flow and Runtime Behavior

This header has no runtime control flow. It contributes compile-time constants that AMDGPU code uses in hardware access sequences. The implied runtime pattern is:

1. ASIC-specific initialization selects the NBIO 7.7.0 register headers.
2. A caller chooses a `reg...` offset and matching `_BASE_IDX` for the target NBIO/BIF/RCC/SION register.
3. The driver reads or writes the register through AMDGPU MMIO/SMN/config-space helpers.
4. If individual fields are needed, the caller combines the offset from this file with masks and shifts from the matching generated shift/mask header.

The represented hardware flows include PCIe root-complex and endpoint configuration, link training and equalization, 16 GT/s/PCIe PHY diagnostics, AER and RAS error reporting, interrupt/MSI/MSI-X setup, BACO/power/reset/D-state handling, FLR and D3hot-D0 reset control, mailbox and scratch communication with firmware/BIOS, address-remap/doorbell/FB window programming, DMA/PASID policy, virtual wires, SION credit/arbitration policy, and RCC strap/port/endpoint setup.

## State and Persistence

The header owns no mutable state, allocates no memory, performs no I/O, and persists nothing. It is a compile-time map of hardware state locations.

The state addressed by the macros lives in NBIO hardware registers and PCI configuration images. Some offsets point to mostly static or firmware-seeded values, such as PCI vendor/device/class/capability structures, serial-number registers, supported link and VC capabilities, strap values, and BAR capability registers. Other offsets point to live or sticky state: link status, lane equalization and margining status, AER/RAS status/log registers, D-state and reset interrupt status, PASID status, performance counters, SION credit/control state, mailbox registers, and scratch registers.

Writable state includes PCI command/device/link controls, MSI/MSI-X controls, AER masks/severity, ACS/ATS/page-request/PASID controls, DPA and power-budget controls, reset/FLR/D3hot controls, BACO/power-break/PERST controls, doorbell/FB/remap windows, DMA attribute overrides, PASID checking, virtual-wire registers, SION arbitration credits, RCC device/endpoint/downstream controls, and BIOS/firmware scratch/mailbox locations. Persistence across GPU reset, PCI reset, FLR, BACO, suspend/resume, or runtime power transitions is hardware-defined and not described by this offset header.

## Dependencies and Integration Points

The direct dependency is exact synchronization with the rest of the generated NBIO 7.7.0 register set:

- `nbio_7_7_0_sh_mask.h` supplies field masks and shifts for the values at these offsets.
- Other generated NBIO headers in the same directory provide SMN or related ASIC-register definitions.
- AMDGPU NBIO/BIF/RCC code relies on the exact `reg...` names and `_BASE_IDX` suffixes expected by local register-access helpers.

Likely integration areas include:

- NBIO 7.7.0 ASIC bring-up and low-level register read/write paths.
- PCIe root-complex and endpoint enumeration/configuration logic for `DEV2_RC0` and `DEV0_EPF0_0`.
- PCIe link management, retraining, equalization, 16 GT/s diagnostics, and lane margining code.
- MSI/MSI-X interrupt setup and PCIe AER/root-error/RAS diagnostics.
- GPU reset, per-function FLR, D3hot/D0 transition, power interrupt, BACO, PERST, and self-soft-reset handling.
- Firmware/BIOS handoff paths that use scratch, mailbox, SBIOS scratch, BIOS scratch, strap, and RCC registers.
- Virtualization and isolation-adjacent paths that depend on PASID, ATS, ACS, page-request, doorbell, VF FB, VF doorbell, and PF/VF decode windows.
- Internal fabric tuning or diagnostics that use SION credit/time-slot/burst-target controls, SDP/GMI/HSTARB controls, SMN virtual wires, and BIF performance counters.

The chunk crosses multiple address blocks with different hardware semantics even though most `_BASE_IDX` values are the same. Consumers must pair the correct register prefix with the intended hardware block; repeated names across `DEV0`, `DEV1`, `DEV2`, `EP`, `DWN`, and `DWNP` families are intentionally similar but not interchangeable.

## Risks

- Chunk boundaries split macro pairs. Line 4877 is only the `_BASE_IDX` for `regBIF_CFG_DEV2_RC0_SLOT_CNTL2`, whose offset is on the previous line outside this chunk. Line 7378 defines `regBIF_CFG_DEV0_EPF0_0_PCIE_PASID_CNTL`, whose `_BASE_IDX` follows in the next chunk. Pair-completeness checks must account for adjacent chunks.
- A wrong offset or base index silently targets the wrong hardware register. This can corrupt PCIe configuration, reset state, interrupt routing, RAS/AER policy, firmware scratch/mailbox state, or internal fabric tuning.
- Many register families are repeated by device, port, endpoint, downstream block, function, lane, or VF/PF role. Copy/paste or generated-name mistakes can map valid-looking code to the wrong device/function/lane.
- Some registers at the same offset represent different logical fields or access widths in PCI config space, such as MSI address/data aliases, status/control sharing, ACS capability/control sharing, DPA status/control sharing, and PASID capability/control sharing. Callers must use the paired shift/mask definitions and preserve unrelated bits.
- Status and log registers may have side effects such as sticky bits, write-one-to-clear behavior, destructive reads, or reset-domain-specific retention. This header does not encode access permissions or side-effect rules.
- Power/reset/D-state/FLR/BACO/PERST registers are high impact. Incorrect writes can hang the device, lose function state, or break recovery paths.
- Scratch, mailbox, and strap registers may participate in firmware contracts. Uncoordinated writes can break SBIOS/SMU/driver handoff assumptions.
- SION, DMA attribute, PASID, ATS, ACS, page-request, and virtual-wire registers can affect DMA routing, isolation, ordering, or internal fabric fairness. Incorrect programming can become a security, correctness, or performance issue.

## Test and Validation Signals

Useful validation for this chunk is mostly generated-header consistency plus hardware-facing behavior:

- Build AMDGPU configurations that include `nbio_7_7_0_offset.h` to catch malformed or duplicate macro definitions.
- Cross-check every in-range `reg...` macro against a matching `_BASE_IDX`, allowing the known first and last chunk-boundary exceptions.
- Cross-check register names against `nbio_7_7_0_sh_mask.h` so offsets have matching field definitions where the register is field-addressable.
- Compare the generated offsets and address-block boundaries with the NBIO 7.7.0 hardware register database for `bif_cfg_dev2_rc`, `bif_bx`, RCC, BIF misc/reset/RAS, SION, and `bif_cfg_dev0_epf0`.
- On matching hardware, inspect PCIe configuration dumps for `DEV2_RC0` and `DEV0_EPF0_0`; capability chains should report plausible MSI/MSI-X, VC, AER, ACS, ATS, page request, PASID, DPA, power budget, DLF, and 16 GT/s structures.
- Exercise link bring-up, retraining, equalization, 16 GT/s status, and lane margining diagnostics, confirming lane-numbered offsets map to expected lanes.
- Validate interrupt delivery through MSI/MSI-X setup and confirm mask/pending/table/PBA offsets decode correctly.
- Run reset and power-management flows such as suspend/resume, BACO, FLR, D3hot/D0 transitions, and GPU reset, checking that writable controls are restored and status bits behave as expected.
- Exercise AER/RAS error reporting or fault injection and verify uncorrectable/correctable status, root error status/source ID, header logs, TLP prefix logs, BIFL RAS central/leaf status, and IOHUB RAS interrupt controls decode consistently.
- Use firmware/BIOS handoff tests to confirm scratch, mailbox, strap, and RCC programming remain compatible with SBIOS/firmware expectations.

## Chunk Boundary Notes

Lines 4877-5143 complete the visible tail of `nbio_nbif0_bif_cfg_dev2_rc_bifcfgdecp`, whose address-block comment and early PCI header offsets are above this chunk. Lines 5144-5735 cover BIF PF/system and BIFDEC1 internal blocks. Lines 5736-6517 cover large RCC strap and device/endpoint/downstream blocks for devices 0, 1, and 2. Lines 6518-6911 cover BIF miscellaneous and reset/power/D-state/FLR controls. Lines 6912-6935 cover BIF RAS controls/status. Lines 6936-7063 cover SION credit/arbitration controls. Lines 7064-7378 begin `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` and stop at the `PCIE_PASID_CNTL` offset before its `_BASE_IDX`.
