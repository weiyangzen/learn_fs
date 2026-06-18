# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 31719-34187

## Scope

This chunk covers a generated AMD NBIO 7.0 shift/mask header segment for PCIe/NBIO register fields. It contains only preprocessor constants: one `__SHIFT` macro and one `_MASK` macro for each named bitfield. There are no C functions, structs, enums, variables, branches, locks, allocations, persistence objects, or direct hardware accesses in this range.

The chunk starts inside `BIF_CFG_DEV0_RC1_SLOT_STATUS`; its register comment and any fields before `ATTN_BUTTON_PRESSED` are in the previous chunk. It ends inside `BIF_BX_PF0_MM_CFGREGS_CNTL` after `MM_WR_TO_CFG_EN__SHIFT`; the mask definitions for that final register continue in the next chunk.

The visible address-block coverage is:

- Tail of `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp`: `BIF_CFG_DEV0_RC1_*` root-complex PCI configuration, MSI, vendor-specific capability, virtual channel, AER, link equalization, and ACS fields.
- Full visible `nbio_nbif0_bif_cfg_dev1_rc_bifcfgdecp`: `BIF_CFG_DEV1_RC1_*` PCI/PCIe root-complex configuration fields from IDs and command/status through ACS.
- `nbio_nbif0_bif_bx_pf_SYSPFVFDEC`: indirect MMIO index/data aperture fields for PF0.
- `nbio_nbif0_bif_bx_pf_SYSDEC`: syshub/PCIe indirect apertures, SBIOS/BIOS scratch fields, RLC/VCE/UVD interrupt controls, and GFX MMIO CAM remap/control fields.
- `nbio_nbif0_rcc_strap_BIFDEC1`: device/function strap fields for RCC device 0 endpoint function 0.
- `nbio_nbif0_rcc_ep_dev0_BIFDEC1`: endpoint-side PCIe control, interrupt, LTR, DPA, PME, TX, error, RX, and link-speed fields.
- `nbio_nbif0_rcc_dwn_dev0_BIFDEC1` and `nbio_nbif0_rcc_dwnp_dev0_BIFDEC1`: downstream PCIe control, error, RX, link-speed, strap, and LTR-message fields.
- Start of `nbio_nbif0_bif_bx_pf_BIFDEC1`: BIF PF0 indirect-access disable, bus control, scratch, reset-enable, and start of MM config-register control fields.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield half of AMD's generated NBIO 7.0 register interface. The matching register addresses live in `nbio_7_0_offset.h`, while reset/default values live in adjacent generated default headers. Runtime driver code includes this file so it can compose, extract, and update hardware register fields through the common AMDGPU register-helper convention rather than open-coding bit positions.

This chunk is centered on PCIe root-complex and NBIF bridge configuration surfaces. The `BIF_CFG_DEV0_RC1_*` and `BIF_CFG_DEV1_RC1_*` families expose PCI-compatible configuration fields such as command/status, bridge bus-number windows, I/O and memory base/limit registers, interrupt and bridge control, power-management capability, PCIe device/link/slot/root controls, MSI/MSI-map capability, virtual-channel capability and resources, AER status/mask/severity/header logs, secondary PCIe capability, per-lane equalization controls, and ACS capability/control. The later BIF/RCC blocks expose indirect register apertures, scratch registers, firmware-visible BIOS scratch space, block interrupt controls, MMIO CAM remapping, strap-derived device identity, endpoint/downstream PCIe behavior overrides, LTR/DPA controls, and error-reporting knobs.

This repository path is under a Ceph/distributed-filesystem mirror, but this header segment belongs to the mirrored Linux AMDGPU driver tree and has no Ceph filesystem behavior.

## Important APIs, Types, and Functions

There are no callable APIs, C types, or functions in this chunk. The public interface is the macro namespace. Each macro follows one of the generated forms:

- `<REGISTER>__<FIELD>__SHIFT` gives the zero-based bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field mask with the field already shifted into register position.

The register-helper contract is important. AMDGPU code can use these definitions with helpers such as `REG_GET_FIELD()` and `REG_SET_FIELD()` when the register offset macro has the same `<REGISTER>` stem. For example, command/status and PCIe-control fields can be read, masked, shifted, and updated without spelling raw bit numbers. Multi-bit masks in this range include bus numbers, bridge windows, payload/request sizes, link widths/speeds, completion timeout values, VC/TC mapping, AER header-log controls, equalization presets, DPA power allocation values, LTR timing values, and traffic-class selections.

Important field groups visible in this chunk include:

- PCI command/status and bridge windows: `IOEN_DN`, `MEMEN_DN`, `BUS_MASTER_EN`, parity/SERR/int-disable bits, primary/secondary/subordinate bus numbers, I/O and memory base/limit fields, prefetchable-window upper registers, and bridge control.
- PCIe capability fields: device capabilities and controls for payload, relaxed ordering, phantom functions, extended tag, No Snoop, AUX power, errors, FLR, link speed/width, ASPM, read completion boundary, link retrain, common clock, slot power/hotplug, root error/PME controls, and CRS visibility.
- MSI and subsystem fields: MSI enable/multiple-message/64-bit/per-vector mask capability, MSI message address/data fields, subsystem vendor/device IDs, and MSI-map control/address fields.
- PCIe extended capabilities: vendor-specific capability headers/scratch, VC port and resource controls, device serial number, AER uncorrectable/correctable status/mask/severity, AER capability/control, header/TLP prefix logs, root error command/status/source IDs, secondary PCIe link/equalization, per-lane equalization controls for lanes 0-15, and ACS capability/control fields.
- Indirect apertures and scratch: `BIF_BX_PF0_MM_INDEX`, `MM_DATA`, `MM_INDEX_HI`, `SYSHUB_INDEX_OVLP`, `SYSHUB_DATA_OVLP`, `PCIE_INDEX`, `PCIE_DATA`, `PCIE_INDEX2`, `PCIE_DATA2`, `SBIOS_SCRATCH_0..3`, and `BIOS_SCRATCH_0..15`.
- BIF/RCC controls: block interrupt controls for RLC/VCE/UVD, GFX MMIO CAM address/remap/enable/completion fields, RCC endpoint/downstream error reporting, hidden-register decode enables, LTR controls, DPA power allocation, PME control, PCIe TX requester ID, RX ignore controls, link-speed straps, downstream FLR/timeout controls, and PF0 bus/reset/MM-config fields.

## Control Flow

This header has no local control flow. It participates in external driver control flow as a constants provider:

1. Generation-specific AMDGPU code selects an NBIO 7.0 register offset from the matching offset header.
2. The code reads a PCIe/NBIO register through MMIO, SMN, PCI config-space, or an indirect index/data aperture.
3. The code uses this header's `__SHIFT` and `_MASK` constants to extract fields or compose a read-modify-write value.
4. The hardware, firmware, PCIe core, or NBIO block observes the resulting register value and performs the actual side effect.

The chunk's fields therefore support flows such as PCIe root-port discovery, bridge-window setup, error reporting/AER handling, link training and equalization, MSI setup, ACS isolation, virtual-channel configuration, firmware handoff through scratch registers, MMIO indirect access, block-level interrupt routing, GPU reset/FLR behavior, LTR/DPA power management, and endpoint/downstream error policy. The header itself does not enforce ordering, polling, locking, or reset sequencing.

## State and Persistence Behavior

No software state is stored here. All state described by the macros lives in NBIO, PCIe, BIF, RCC, firmware scratch, or strap-backed hardware registers once external code reads or writes the corresponding offsets.

State behavior varies by register family:

- PCI configuration and PCIe capability/control fields are hardware-visible configuration state. Some bits are set by enumeration or driver initialization, some are status bits, and others can be write-1-to-clear or write-sensitive depending on the PCIe/AER specification and the ASIC register database.
- AER status, root error status, header logs, TLP prefix logs, lane error status, interrupt status, and DPA/PME status-like fields are hardware-observed diagnostic or event state. They may be cleared by writes, reset by function reset, or updated asynchronously by PCIe hardware.
- `SBIOS_SCRATCH_*` and `BIOS_SCRATCH_*` are scratch registers intended for firmware/BIOS/driver coordination. Their persistence depends on ASIC reset domains and boot firmware policy; treating them as driver-private storage is unsafe without ownership knowledge.
- Strap fields such as `STRAP_DEVICE_ID_DEV0_F0`, revision IDs, function enable, legacy device type, and D-state support reflect boot-time strap/fuse/configuration values and should generally be considered hardware-initialized identity/capability state.
- Indirect aperture registers (`MM_INDEX`, `MM_DATA`, `PCIE_INDEX`, `PCIE_DATA`, syshub index/data) hold addressing and data windows for other register spaces. Their values may be transient cursor state for an access sequence and can race if shared without the driver's existing serialization.
- Reset and FLR-related bits (`BX_RESET_EN`, downstream `FLR_EXTEND_MODE`, reset-on-VF-enable-low, FLR twice enable) influence recovery behavior rather than storing durable user data.

## Dependencies and Integration Points

This chunk depends on the generated NBIO 7.0 register header set:

- `nbio_7_0_offset.h` supplies the matching register offsets for the same register stems.
- `nbio_7_0_default.h` or related generated default headers supply reset values where available.
- AMDGPU's common register helper macros consume the `__SHIFT` and `_MASK` naming convention.

Integration points in the wider AMDGPU tree include NBIO generation code, PCIe configuration and link-management code, interrupt setup, GPU reset/FLR paths, SR-IOV/VF/PF handling, power-management code that relies on LTR/DPA/ASPM-related fields, error reporting/AER diagnostics, and firmware/BIOS handoff logic that reads scratch or strap fields. The `BIF_BX_PF0_*` indirect aperture and MMIO CAM fields also integrate with lower-level register access paths because they can redirect or expose otherwise hidden register windows.

The fields align with standard PCI/PCIe concepts, but the actual register addresses and some names are ASIC-specific. Code must pair these masks with NBIO 7.0 offsets, not with similar-looking masks from other NBIO generations or device instances.

## Risks and Edge Cases

- The chunk starts and ends mid-register. `BIF_CFG_DEV0_RC1_SLOT_STATUS` is incomplete at the start, and `BIF_BX_PF0_MM_CFGREGS_CNTL` is incomplete at the end. Final per-file research must merge neighboring chunks before claiming complete coverage of those registers.
- Many fields mirror PCIe specification bits with precise write semantics. Misusing status masks as normal read-write bits can lose AER/error evidence or accidentally clear interrupt/status conditions.
- DEV0 and DEV1 root-complex families are structurally similar. Copying a `BIF_CFG_DEV0_RC1_*` mask to a `BIF_CFG_DEV1_RC1_*` register, or the reverse, may compile if the field shape matches but operate on the wrong device instance.
- Per-lane equalization controls are repeated for lanes 0-15. Off-by-one lane selection or a missing lane in generated data can produce subtle link-training failures that are not caught by simple compile tests.
- ACS, peer-to-peer redirect, translation blocking, and upstream-forwarding bits affect DMA isolation and topology behavior. Incorrect masks can weaken isolation or break peer-to-peer traffic.
- AER mask/severity/status fields determine whether errors are surfaced, suppressed, or classified fatal/nonfatal. Generation drift in these constants can hide hardware faults or create spurious fatal handling.
- Indirect index/data aperture fields are shared access mechanisms. A driver sequence that updates index and data without appropriate locking or ordering can read/write an unintended target register.
- BIOS/SBIOS scratch registers are integration points with firmware. Driver changes that overwrite undocumented scratch content can break boot handoff, resume, reset recovery, or board-specific workarounds.
- Strap-derived fields are often read-only or boot-latched. Treating them as writable configuration can be ineffective or harmful depending on the actual hardware access policy.
- Several fields use high bits, full 32-bit masks, or 64-bit-related address/data pairs. C code must use types wide enough for masks such as `0x80000000L` and must handle split address fields correctly on 32-bit and 64-bit builds.

## Test Signals

- Build AMDGPU configurations that include NBIO 7.0 headers and all generation-specific code using these macros; this catches missing, renamed, or malformed generated symbols.
- Run generated-header consistency checks against the authoritative NBIO 7.0 register database: every register in this range should have matching offset/default entries and field masks that agree with the field width and shift.
- Verify cross-chunk continuity: `BIF_CFG_DEV0_RC1_SLOT_STATUS` must be complete when merged with the previous chunk, and `BIF_BX_PF0_MM_CFGREGS_CNTL` must be complete when merged with the next chunk.
- On affected AMD GPU hardware, exercise PCIe enumeration, bridge bus/window programming, MSI delivery, AER logging, hotplug/status bits where applicable, ACS behavior, link retrain/equalization, suspend/resume, GPU reset, and FLR.
- For AER and interrupt fields, inject or observe correctable/nonfatal/fatal PCIe events and confirm status, masks, root-error reporting, header logs, and source IDs behave as expected.
- For indirect aperture fields, test serialized index/data read and write paths with known registers and verify that unrelated accessors cannot corrupt the selected index.
- For scratch and strap fields, compare driver-observed values with firmware handoff expectations across cold boot, warm reboot, suspend/resume, and GPU reset.
- For repeated lane equalization and DPA allocation registers, include sequence and naming checks in generated-header tests, because simple bit-width checks would not catch swapped lane numbers or duplicated register stems.

## Unresolved Cross-Chunk References

The preceding chunk contains the beginning of `BIF_CFG_DEV0_RC1_SLOT_STATUS`, including the register comment and any field definitions before line 31719. The following chunk contains the remaining `BIF_BX_PF0_MM_CFGREGS_CNTL` mask definitions and subsequent `BIF_BX_PF0_*` BIFDEC1 registers. The final per-file document should stitch these boundaries and summarize the whole `nbio_7_0_sh_mask.h` generated register namespace rather than treating this chunk as a complete header.
