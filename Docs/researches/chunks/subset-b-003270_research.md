# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 27071-29531

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.7.0 shift/mask header. It defines C preprocessor constants for bit positions and masks in NBIO/PCIe bridge, BIF indexed-access, BIOS scratch, interrupt-control, GFX MMIO remap CAM, and RCC strap registers.

The range starts in the tail of the `BIFPLR5` PCI-to-PCI bridge configuration image, immediately after the `BIFPLR5_PREF_BASE_LIMIT` shifts, and continues through the rest of the `BIFPLR5` PCIe capability and enhanced-capability layout. It then moves across address-block comments for `nbio_pcie2_bifplr0_cfgdecp`, `nbio_nbif0_bif_bx_pf_SYSPFVFDEC:1`, `dbgu_nbio_ports_blk`, `nbio_nbif0_bif_bx_SYSDEC:1`, and starts `nbio_nbif0_rcc_strap_BIFDEC1`. The chunk ends partway through `RCC_STRAP0_RCC_BIF_STRAP2`, so the following `RCC_STRAP0` strap fields continue in the next chunk.

The file is not executable code. Its purpose is to provide the field-layout contract used by AMDGPU register access code when decoding or composing raw NBIO register values. Register addresses and base indices are supplied by the paired `nbio_7_7_0_offset.h`; this header supplies only the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants.

## Major Register Groups

The `BIFPLR5` portion describes one NBIO PCIe bridge/root-port-like configuration image. It covers conventional bridge header fields such as prefetchable and I/O base/limit upper halves, capability pointer, interrupt line/pin, extension bridge control, vendor capability metadata, subsystem ID, and power-management capability/status.

The same `BIFPLR5` block then defines standard PCIe capability fields: PCIe capability metadata, Device Control/Status, Link Capability/Status, Slot Capability/Control/Status, Root Control/Capability/Status, Device Control 2, Device Status 2, Link Status 2, and Slot Capability/Control/Status 2. These fields expose error reporting enables, payload and read-request sizing, relaxed ordering and no-snoop controls, link speed and width reporting, ASPM-related capability bits, hotplug/slot controls, CRS visibility, PME status, completion-timeout controls, ARI forwarding, atomic operation controls, LTR, OBFF, emergency power reduction, and 8 GT/s equalization status.

The interrupt and capability-list section includes MSI list metadata and message-address registers, SSID capability fields, MSI map capability fields, vendor-specific enhanced capability headers and scratch fields, Virtual Channel capability/control/status for VC0 and VC1, device serial number, AER, secondary PCIe, ACS, multicast, LTR, ARI, Downstream Port Containment, Root Port PIO, ESM, Data Link Feature, 16 GT/s PHY, lane margining, and CCIX/ESM capability fields.

The AER and RAS-adjacent register groups are extensive. `BIFPLR5_PCIE_UNCORR_ERR_STATUS`, `_MASK`, and `_SEVERITY` cover DLP, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receive overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic egress blocking, TLP prefix blocking, and poisoned-TLP egress blocking. Correctable status and mask cover receiver, bad TLP/DLLP, replay rollover/timeout, advisory nonfatal, internal correctable, and header-log-overflow errors. Header-log and TLP-prefix-log registers are full-width 32-bit fields.

The lane-management sections are highly repetitive. PCIe secondary capability supplies lane error status and per-lane equalization control for lanes 0-15. The 16 GT/s PHY capability adds link capability/status, local and retimer parity mismatch status, and per-lane 16 GT/s downstream/upstream transmit presets. The lane margining capability adds a port capability/status pair and per-lane control/status pairs for lanes 0-15, with receiver number, margin type, usage model, and payload fields. The CCIX/ESM area adds ESM support/capability/status and per-lane 20 GT/s and 25 GT/s equalization preset controls for lanes 0-15.

After `BIFPLR5`, the `BIF_BX_PF0_*` group defines indirect MMIO and RSMU index/data registers for a physical-function view: `MM_INDEX`, `MM_DATA`, `MM_INDEX_HI`, `RSMU_INDEX`, and `RSMU_DATA`. The `BIF_BX0_*` system block defines PCIe index/data pairs, four SBIOS scratch registers, sixteen BIOS scratch registers, RLC/VCE/UVD interrupt-control bits, and GFX MMIO register CAM address/remap pairs for entries 0-7 plus CAM enable and completion-value registers.

The `RCC_STRAP0` group begins strap registers that govern link generation, feature exposure, reset/link behavior, error handling, aperture/security behavior, and low-power behavior. `RCC_BIF_STRAP0` includes Gen4/Gen3 disabling, VGA and BIOS ROM straps, PX capability, MSI first-BE behavior, NBIF FLR error handling, PME compliance, multiple receive-error ignore controls, relaxed-ordering peer-to-peer behavior, VF bus-number checking, big-APU mode, and link-down reset. `RCC_BIF_STRAP1` covers strap validity/write-disable, ECRC intermediate checking, E2E prefix handling, software lane margining readiness, SWUS aperture settings, hardware/software revision bits, link-reset behavior, IOV link-reset disable, DLF, 16 GT/s PHY, margining, PSN unsupported-request reporting, slot-power support, graphics LTR mode, SMN post-write behavior, and address-translation/prefix enablement. This chunk starts `RCC_BIF_STRAP2` through fields for PCIe SWUS index aperture range, indirect-access disables, linkdown DMA drop, SWUS security override, GMI clock-request behavior, ACS mask/severity hiding, firmware power-gating interlock exit, and a reserved bit.

## Important APIs, Types, And Functions

There are no functions, structs, enums, or callable APIs in this chunk. The exported interface is the generated macro namespace:

- `REGISTER__FIELD__SHIFT` gives the zero-based bit offset of a field.
- `REGISTER__FIELD_MASK` gives the field mask in the containing register.

Consumers normally combine these macros with AMDGPU helper macros such as `REG_GET_FIELD` and `REG_SET_FIELD`, or direct bit operations, after selecting the matching NBIO 7.7.0 register address from `nbio_7_7_0_offset.h`.

Important macro families in this chunk include `BIFPLR5_*` for PCIe bridge/capability decoding, `BIF_BX_PF0_*` and `BIF_BX0_*` for indirect register access and BIOS/system scratch state, `BIF_BX0_BIF_{RLC,VCE,UVD}_INTR_CNTL` for engine interrupt signaling, `BIF_BX0_GFX_MMIOREG_CAM_*` for graphics MMIO aperture remapping, and `RCC_STRAP0_RCC_BIF_STRAP*` for hardware strap-controlled NBIO behavior.

## Control Flow

This header has no runtime control flow. Runtime behavior is created by code that:

1. Selects the NBIO 7.7.0 register set for the detected ASIC.
2. Uses the paired offset/base-index macro for a `BIFPLR5`, `BIF_BX0`, `BIF_BX_PF0`, or `RCC_STRAP0` register.
3. Reads the raw register through SOC15/NBIO, indexed MMIO, PCIe config, or firmware-facing access paths.
4. Extracts fields using the mask and shift constants, or composes a new value while preserving unrelated and reserved bits.
5. Writes back only when the target register is writable and the surrounding driver flow owns that hardware state.

The hardware flows represented by the fields include PCIe bridge enumeration, power management, link status and equalization, lane margining, MSI metadata, AER/RAS error reporting, DPC and Root Port PIO error capture, CCIX/ESM data-rate capability, indirect MMIO/RSMU access, firmware/BIOS scratch handoff, engine interrupt event reporting, GFX MMIO remap CAM programming, and strap-driven link/feature policy.

## State And Persistence

The header itself is stateless and persists no data. It is a compile-time description of hardware register layouts.

The state described by the macros lives in NBIO/PCIe hardware registers. Capability fields such as PCIe capability IDs, supported link width/speed, VC/ACS/multicast/LTR/ARI/DPC/ESM/DLF/16 GT/s/margining/CCIX support, MSI metadata, and serial-number data are generally hardware-, fuse-, strap-, or firmware-defined. Control fields such as Device Control, Device Control 2, Slot Control, Root Control, AER masks/severity, DPC controls, Root Port PIO masks/severity/syserror/exception bits, ESM enablement, lane margining controls, indirect-access indices, interrupt clear/enable-like controls, CAM enable bits, and strap override bits are writable only according to the hardware access rules for the specific register.

Status fields are live or sticky hardware observations. Examples include PCIe Device Status, Link Status, Slot Status, Root Status, Link Status 2 equalization bits, AER correctable/uncorrectable status, header/prefix logs, lane error status, 16 GT/s link/equalization/parity status, margining port/lane status, CCIX/ESM calibration/current-data-rate status, BIOS scratch contents, interrupt status/clear bits, and strap-valid/write-disable indicators.

Persistence depends on the register's hardware domain. Some values survive until FLR, hot reset, GPU reset, suspend/resume, power-gating transitions, or firmware reinitialization; scratch registers may be used for BIOS/driver handoff; strap-derived values may be latched from fuses or ROM straps and may not behave like normal software-owned configuration state. This header does not encode reset defaults, read-only/write-only permissions, read side effects, or write-one-to-clear semantics.

## Dependencies And Integration Points

These definitions must remain synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h`. A field macro such as `BIFPLR5_PCIE_UNCORR_ERR_STATUS__CPL_TIMEOUT_STATUS_MASK` is only meaningful with the matching `BIFPLR5_PCIE_UNCORR_ERR_STATUS` register address and base index. The same applies to `BIF_BX0_GFX_MMIOREG_CAM_ADDR<n>`, `BIF_BX0_BIF_UVD_INTR_CNTL`, and the `RCC_STRAP0_RCC_BIF_STRAP*` registers.

Integration points include:

- AMDGPU NBIO 7.7.0 ASIC support that includes generated `asic_reg/nbio` headers for register access.
- PCIe configuration and diagnostics paths that inspect bridge identity, PM, PCIe, MSI, VC, AER, ACS, ARI, DPC, ESM, DLF, 16 GT/s, margining, and CCIX capability data.
- Link-management and signal-quality diagnostics that read negotiated link speed/width, equalization completion, retimer presence, parity mismatch, lane presets, margining readiness, and ESM calibration/rate fields.
- RAS/AER and PCIe error-handling paths that decode correctable/uncorrectable status, masks, severity, first-error pointer, ECRC controls, header logs, TLP prefix logs, DPC trigger/reason/source IDs, and Root Port PIO logs.
- Firmware and low-level NBIO paths using `BIF_BX0_PCIE_INDEX/DATA`, `BIF_BX0_PCIE_INDEX2/DATA2`, BIOS/SBIOS scratch registers, and `BIF_BX_PF0_MM_*` or `RSMU_*` indirect windows.
- Engine interrupt paths that use the RLC, VCE, and UVD interrupt-control masks for command-complete, hang/self-recovery, FLR-required, and VM-busy transition events.
- Graphics aperture/remap setup paths that program `BIF_BX0_GFX_MMIOREG_CAM_ADDR0-7`, matching remap addresses, `CAM_ENABLE`, and completion-value behavior.
- Strap override or bring-up code. Related AMDGPU NBIF/NBIO revisions directly read/modify/write `RCC_STRAP0_RCC_BIF_STRAP2`, `RCC_STRAP0_RCC_BIF_STRAP3`, and `RCC_STRAP0_RCC_BIF_STRAP5` for ASPM/LTR/LDN behavior; this chunk supplies the NBIO 7.7.0 layout for the beginning of that same strap family.

## Risks

The primary risk is silent hardware misprogramming if a generated mask or shift is wrong, copied into a consumer with the wrong register prefix, or paired with an offset from the wrong ASIC revision or address block. A one-bit error can enable the wrong PCIe error-reporting path, misdecode negotiated link status, mask the wrong AER error, corrupt DPC/PIO policy, change an ESM rate bit, route indirect register accesses incorrectly, clear the wrong engine interrupt, or expose a different strap-controlled feature than intended.

Chunk boundaries are a specific documentation risk. This range starts after the `BIFPLR5_PREF_BASE_LIMIT` shift definitions and ends before `RCC_STRAP0_RCC_BIF_STRAP2` is complete. Any final per-file report must merge adjacent chunks before treating those register groups as complete.

The repeated per-lane sections are vulnerable to lane-index mistakes. Equalization, 16 GT/s, margining, and 20/25 GT/s ESM registers repeat for lanes 0-15 with nearly identical field names. A typo or generator drift may affect only wide-link configurations or only a single physical lane, making it hard to catch with narrow-link testing.

Status and log registers have hardware-defined semantics not represented here. AER status, PCIe Device/Slot/Root status, DPC status, Root Port PIO status, header logs, TLP prefix logs, lane status, parity mismatch, margining status, CCIX/ESM status, and interrupt-control bits may be sticky, write-one-to-clear, read-only, or side-effecting depending on the hardware specification. Consumers must not infer writability from the presence of a mask.

Strap fields are especially sensitive. `RCC_STRAP0` controls link generation enablement, firmware/ROM strap validity, reset policy, error-ignore policy, aperture/security settings, and access disable bits. Treating strap-derived fields as ordinary software knobs can break enumeration, power management, FLR/reset behavior, error reporting, or security isolation.

Mixed logical widths also matter. Some PCI capability fields are 8- or 16-bit logical fields, while AER logs, ESM capability bitmaps, scratch registers, CAM registers, and strap registers are 32-bit. Consumers must use the access width and read-modify-write pattern expected by the matching AMDGPU register path and preserve reserved bits.

## Test Signals

Useful validation signals are mostly integration and hardware-facing:

- The AMDGPU tree builds with NBIO 7.7.0 headers included, proving referenced macro names resolve.
- Static generator validation confirms every register in this chunk has a matching `nbio_7_7_0_offset.h` address/base-index entry where expected, and that all `*_SHIFT` values match their `*_MASK` bit positions.
- PCIe enumeration and diagnostics on matching hardware report plausible bridge PM/PCIe/MSI/VC/AER/ACS/ARI/DPC/ESM/DLF/16 GT/s/margining/CCIX capabilities.
- Link tests decode expected negotiated speed/width, equalization state, retimer presence, 16 GT/s status, parity mismatch, ESM rate/calibration state, and lane margining readiness.
- RAS/AER fault injection or real error logs decode correctable and uncorrectable errors, masks, severity, first-error pointer, header logs, prefix logs, DPC status/source IDs, and Root Port PIO logs consistently with hardware documentation.
- Firmware handoff and resume tests preserve or reinitialize SBIOS/BIOS scratch data and indirect-access windows as expected.
- RLC, VCE, and UVD interrupt tests observe command-complete, hang recovery, FLR-required, and VM-busy transition bits without clearing or routing unrelated events.
- GFX MMIO CAM tests verify each of the eight CAM address/remap entries and `CAM_ENABLE` bits map only the intended MMIO ranges.
- Suspend/resume, FLR, hot reset, GPU reset, and power-management tests verify that writable PCIe controls, AER policy, DPC/PIO masks, ESM/margining controls, CAM programming, and strap-derived policies are restored by higher-level driver paths rather than relying on this header for defaults.
