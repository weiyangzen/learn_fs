# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 31986-34402

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.7.0 shift/mask header. It defines C preprocessor constants for PCIe root-complex configuration-space bitfields in `BIF_CFG_DEV0_RC0` and the beginning of the next `BIF_CFG_DEV1_RC0` block. The constants describe only bit positions and masks; the register addresses and base indices live in the paired `nbio_7_7_0_offset.h` header.

The range starts in the middle of the `BIF_CFG_DEV0_RC0_PCIE_CAP` group, with only the `VERSION`, `DEVICE_TYPE`, `SLOT_IMPLEMENTED`, and `INT_MESSAGE_NUM` masks present here. It then covers the rest of the `DEV0_RC0` PCIe capability and enhanced-capability image, including device/link/slot/root controls, MSI, vendor-specific capability, virtual-channel capability, device serial number, AER, secondary PCIe, ACS, data-link feature, 16 GT/s PHY, and PCIe lane-margining fields. The chunk then switches at `addressBlock: nbio_nbif0_bif_cfg_dev1_rc_bifcfgdecp` to a second root-complex config image, covering the conventional PCI bridge header through AER and 8 GT/s equalization for lanes 0-3. It ends on the `BIF_CFG_DEV1_RC0_PCIE_LANE_4_EQUALIZATION_CNTL` comment, so lane 4's field definitions are outside this chunk.

## Major Register Groups

The `BIF_CFG_DEV0_RC0` portion covers root-complex PCIe capability fields after the initial capability-list metadata:

- PCIe Device/Link/Slot/Root Capability, Control, and Status fields for payload size, read-request size, error enables, relaxed ordering, no-snoop, FLR, link speed/width, ASPM/PM, retrain, data-link active state, hotplug controls, PME/root error reporting, and PCIe Capability 2 features.
- MSI and subsystem/vendor capabilities: MSI control, message address/data variants, MSI mapping, and SSID capability fields.
- PCIe enhanced capabilities: vendor-specific headers/scratch fields, virtual-channel capability/control/status for VC0 and VC1, device serial number, AER status/mask/severity/logging/root-error fields, TLP prefix logs, secondary PCIe capability, Link Control 3, lane error status, and per-lane 8 GT/s equalization control for lanes 0-15.
- Isolation and link feature capabilities: ACS capability/control, data-link feature capability/status, and 16 GT/s PHY enhanced capability with 16 GT/s link capability/control/status, parity-mismatch status, and per-lane 16 GT/s equalization presets for lanes 0-15.
- PCIe margining capability: port capability/status plus lane-specific margining control/status pairs for lanes 0-15.

The `BIF_CFG_DEV1_RC0` portion begins a second root-complex/bridge configuration image. It includes vendor/device ID, command/status, class/revision, header/BIST, bridge BARs and bus-number windows, I/O and memory base/limit windows, ROM BAR, interrupt and bridge controls, PM capability, PCIe capability, MSI and SSID fields, vendor-specific and VC enhanced capabilities, device serial number, AER status/mask/severity/logging/root-error fields, secondary PCIe capability, Link Control 3, lane error status, and complete 8 GT/s equalization-control groups for lanes 0-3.

## Important APIs, Types, And Functions

There are no functions, structs, enums, or callable APIs in this chunk. Its exported interface is the generated macro namespace:

- `BIF_CFG_DEV0_RC0_<REGISTER>__<FIELD>__SHIFT` and `BIF_CFG_DEV1_RC0_<REGISTER>__<FIELD>__SHIFT` give zero-based bit positions.
- `BIF_CFG_DEV0_RC0_<REGISTER>__<FIELD>_MASK` and `BIF_CFG_DEV1_RC0_<REGISTER>__<FIELD>_MASK` give masks in the containing PCIe/NBIO config register.

The chunk contains 2,152 `#define` entries. Most logical fields appear as a pair of `__SHIFT` and `_MASK` macros, but the boundaries are partial: the `DEV0_RC0_PCIE_CAP` shifts are in the previous chunk, and the `DEV1_RC0_PCIE_LANE_4_EQUALIZATION_CNTL` definitions start in the following chunk.

## Control Flow

This header has no executable control flow. Runtime behavior comes from AMDGPU code that includes this generated header, selects the NBIO 7.7.0 register map for the detected ASIC, reads or writes a register using the paired offset macro, and decodes or updates fields with these masks and shifts.

Typical consumer flow is:

1. Select the matching offset, such as `regBIF_CFG_DEV0_RC0_DEVICE_CAP` or `regBIF_CFG_DEV1_RC0_PCIE_LANE_4_EQUALIZATION_CNTL`, from `nbio_7_7_0_offset.h`.
2. Read the register through the AMDGPU MMIO/indexed-register path used for NBIO configuration registers.
3. Extract fields with `value & *_MASK`, shifted by the matching `*__SHIFT`.
4. For writable controls, preserve unrelated and reserved bits, insert the new shifted value, and write the register back.

The hardware flows described by these fields include PCI command and bridge-window programming, link training/retraining, speed/width negotiation, 8 GT/s and 16 GT/s equalization, PCIe lane margining commands and status, interrupt delivery via MSI, virtual-channel arbitration, ACS isolation, AER/RAS reporting, root error messaging, DLF negotiation, hotplug/slot reporting, and power-management/PME handling.

## State And Persistence

The header itself is stateless and persists no data. It is a compile-time description of hardware register layout.

The state described by the macros lives in NBIO PCIe configuration registers. Capability fields such as supported link speeds, maximum payload support, FLR support, 16 GT/s capability, ACS capability, data-link feature support, AER capability, serial number, and margining support are generally hardware- or firmware-defined for the ASIC. Control fields such as `DEVICE_CNTL`, `LINK_CNTL`, `DEVICE_CNTL2`, `LINK_CNTL2`, `ROOT_CNTL`, MSI enables, VC enables, ACS controls, AER masks/severity, 16 GT/s link controls, and margining lane controls are writable hardware state whose lifetime depends on PCIe reset, GPU reset, suspend/resume, and power-management domains.

Status and log fields such as Device Status, Link Status, Slot Status, Root Status, VC status, AER correctable/uncorrectable status, header logs, TLP prefix logs, lane error status, 16 GT/s parity mismatch status, and lane margining status are live hardware observations. The macros do not encode reset defaults, read-only/write-only policy, access width, write-one-to-clear behavior, or whether reads latch or clear hardware events.

## Dependencies And Integration Points

These macros must be used with the NBIO 7.7.0 offset header. For example, `BIF_CFG_DEV0_RC0_DEVICE_CAP__FLR_CAPABLE_MASK` is only a field layout; it is meaningful when paired with the corresponding `regBIF_CFG_DEV0_RC0_DEVICE_CAP` address and base index. The same applies to the `DEV1_RC0` bridge/root-complex groups and their `regBIF_CFG_DEV1_RC0_*` offsets.

Integration points include:

- AMDGPU NBIO 7.7.0 ASIC support that includes generated `asic_reg/nbio` headers.
- PCIe configuration, diagnostics, and reset code that inspects root-complex device, link, slot, bridge, and power-management fields.
- Link-management code that decodes negotiated speed/width, retrain state, data-link active status, Link Status 2 equalization flags, Link Control 3 equalization requests, 16 GT/s presets, and margining controls/status.
- Interrupt setup or diagnostics that program or inspect MSI message address/data, MSI enable/mask state, and MSI mapping capability.
- RAS/AER paths that decode correctable and uncorrectable errors, error masks, severity policy, first-error pointers, ECRC controls, root error command/status, source IDs, header logs, and TLP prefix logs.
- PCIe isolation and traffic-management paths that may use ACS, virtual-channel, DLF, and bridge-window fields.
- Debug tooling that dumps NBIO registers and needs stable field names for `DEV0_RC0` and `DEV1_RC0` register images.

## Risks

The main risk is silent hardware misprogramming if a mask or shift is wrong, stale, or paired with an offset from the wrong ASIC or root-complex block. A bit-position error can misdecode link training state, select an invalid link speed, suppress or misclassify AER errors, corrupt MSI delivery, change bridge decoding windows, or issue unintended equalization/margining commands.

The range has important chunk-boundary hazards. The first four lines are only the mask half of `BIF_CFG_DEV0_RC0_PCIE_CAP`; the corresponding shifts are immediately before the requested range. The final line is only the comment for `BIF_CFG_DEV1_RC0_PCIE_LANE_4_EQUALIZATION_CNTL`; the lane 4 shift/mask definitions follow after the requested range. Any merged per-file report or generator audit must account for adjacent chunks before treating those register groups as complete.

Many fields describe hardware status or reserved areas. Software should not infer that a generated `RESERVED` mask is safe to write, and should not clear status bits without understanding the register's clear semantics. AER, PCI status, PME/root status, lane error, parity mismatch, and margining status fields may be latched or write-one-to-clear depending on the hardware specification.

The repeated lane and root-complex naming is easy to misuse. `DEV0_RC0` versus `DEV1_RC0`, 8 GT/s `PCIE_LANE_<n>_EQUALIZATION_CNTL` versus 16 GT/s `LANE_<n>_EQUALIZATION_CNTL_16GT`, and lane margining control versus status groups differ only by name fragments while compiling as ordinary integer constants. Copy/paste errors can target the wrong device image, speed generation, or lane.

## Test Signals

Useful validation signals are hardware- and integration-facing:

- The AMDGPU tree builds with NBIO 7.7.0 headers included, proving referenced generated macro names resolve.
- Generator or static checks confirm that every complete register group in this chunk has a matching `regBIF_CFG_*` offset/base-index definition in `nbio_7_7_0_offset.h`.
- PCIe enumeration and debug register dumps on matching hardware report plausible `DEV0_RC0` and `DEV1_RC0` vendor/device, class, bridge-window, capability-list, PM, MSI, PCIe, VC, AER, ACS, DLF, PHY, and margining capability values.
- Link diagnostics decode expected speed, width, training state, data-link active state, 8 GT/s equalization state, 16 GT/s preset fields, lane error status, and margining status.
- MSI tests verify that message address/data and control fields produce working interrupts and that masking/pending behavior matches PCIe expectations.
- AER/RAS tests or fault injection decode correctable and uncorrectable status, masks, severity, root error status, source IDs, header logs, and prefix logs consistently with hardware documentation.
- Suspend/resume, FLR/hot reset, and GPU reset testing verifies that writable controls are restored by higher-level driver paths rather than relying on this header for defaults.
