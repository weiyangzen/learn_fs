# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 104474-106883

## Scope

This chunk covers a generated AMD NBIO 7.2.0 register shift/mask header section. It starts in the tail of `PARITY_ERROR_STATUS_UCP_GRP2`, continues through the remaining UCP parity groups, RAS/action-control, poison/APML, BIF indirect/scratch/CAM registers, RCC strap registers for BIF/dev0/endpoint functions, and endpoint PCIe/DPA fields. It ends in the shift definitions for `RCC_EP_DEV0_3_EP_PCIE_TX_CNTL`; the corresponding masks and later endpoint PCIe fields continue in the next chunk.

The file is data-only C preprocessor material. This chunk defines no C functions, structs, variables, locks, allocations, or direct MMIO operations. Its public interface is the generated field-pair convention:

- `<REGISTER>__<FIELD>__SHIFT` for a bit offset.
- `<REGISTER>__<FIELD>_MASK` for the 32-bit field mask.

There are 2,150 `#define` lines and 240 comment/address-block lines in the requested range. The definitions describe register layout, not executable behavior.

## Purpose

This header section is part of the bitfield ABI between AMDGPU code and NBIO 7.2.0 hardware. The companion `nbio_7_2_0_offset.h` header supplies register addresses and base indices; this `*_sh_mask.h` file supplies the field positions and masks used to compose or decode 32-bit MMIO values.

Consumers normally use these macros through AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, and PCIe-port helpers. The source tree includes `amdgpu/nbio_v7_2.c`, which includes both `nbio_7_2_0_offset.h` and `nbio_7_2_0_sh_mask.h` and uses the generated mask/shift convention for NBIO revision ID, doorbell aperture, interrupt, clock-gating, and PCIe-related programming. Display resource files also mirror/use NBIO BIOS scratch register addresses and masks for BIOS/display handoff paths.

## Important Macro Families

### UCP Parity Status and Counters

The chunk begins with the last `PARITY_ERROR_STATUS_UCP_GRP2` mask entries for IDs 15-31, then defines complete `PARITY_ERROR_STATUS_UCP_GRP3` through `PARITY_ERROR_STATUS_UCP_GRP7` families. Each group exposes one bit per `ParityErrDetected_Id0` through `ParityErrDetected_Id31`, with matching shift and mask definitions. Together these registers form a banked parity-error bitmap for UCP-related internal blocks.

`PARITY_COUNTER_UCP_GRP0` through `PARITY_COUNTER_UCP_GRP7` provide compact counter registers with `ParityErrCounter` and `ParityErrCounterOverflow` fields. These are reliability/diagnostic state rather than ordinary configuration: the detected bits and counters let RAS or debug code identify which internal parity source has asserted and whether event volume exceeded the counter width.

### RAS Severity, Scratch, and Action Control

`MISC_SEVERITY_CONTROL` maps severity selection for generic error events and PCIe parity errors. `MISC_RAS_CONTROL` contains output and reporting controls including NMI/sync-flood pin enable, interrupt/link-disable/sync-flood output disables, PCIe NMI/SCI/SMI enables, and software SCI/SMI/NMI enables. `RAS_SCRATCH_0` and `RAS_SCRATCH_1` are full-width scratch registers.

The repeated `*_ACTION_CONTROL` families are the core RAS policy map in this chunk. `ErrEvent_ACTION_CONTROL`, `ParitySerr_ACTION_CONTROL`, `ParityFatal_ACTION_CONTROL`, `ParityNonFatal_ACTION_CONTROL`, and `ParityCorr_ACTION_CONTROL` define action bits for APML error reporting, interrupt generation selection, link disable, and sync-flood behavior. The same four-field layout is repeated for many PCIe and NBIF sources:

- `PCIE0PortA` through `PCIE0PortG` sources, including SERR, internal fatal/nonfatal/correctable, external fatal/nonfatal/correctable, and parity error action registers.
- `NBIF1PortA` through `NBIF1PortC` sources with the same SERR, internal, external, and parity action split.

These definitions allow driver or firmware policy to choose whether a given reliability event only reports, raises an interrupt class, disables a link, triggers sync flood, or routes through APML.

### Sync Flood, NMI, Poison, and APML

`SYNCFLOOD_STATUS` exposes per-source sync-flood status bits. The covered fields include generic error, parity classes, many `PCIE0Port*` categories, and `NBIF1Port*` categories. `NMI_STATUS` is a compact NMI-status register.

`POISON_ACTION_CONTROL` describes the action policy for internal poisoned data and low/high egress poison events. Each poison class has APML error enable, interrupt generation selection, link-disable enable, and sync-flood enable fields. `EGRESS_POISON_STATUS_LO` and `EGRESS_POISON_STATUS_HI` define 64 individual egress poison status bits across two registers. `EGRESS_POISON_MASK_LO/HI` are full-width masks, while `EGRESS_POISON_SEVERITY_DOWN` and `EGRESS_POISON_SEVERITY_UPPER` provide full-width severity maps.

`APML_STATUS` exposes APML-latched correctable, nonfatal, fatal, SERR, internal poison, and egress poison low/high status bits. `APML_CONTROL` controls APML NMI, sync flood, and output disable. `APML_TRIGGER` provides an explicit APML NMI trigger bit. These fields integrate NBIO RAS events with platform management and serviceability paths.

### BIF Indirect Windows, BIOS Scratch, Interrupts, and CAM Remap

The `nbio_nbif0_bif_bx_pf_SYSPFVFDEC` address block defines `BIF_BX_PF2_MM_INDEX`, `BIF_BX_PF2_MM_DATA`, and `BIF_BX_PF2_MM_INDEX_HI`, a PF2 MMIO indirect index/data window. The index includes low offset and aperture selection; the high register carries the upper offset.

The `nbio_nbif0_bif_bx_SYSDEC` block defines:

- `BIF_BX2_PCIE_INDEX/DATA` and `BIF_BX2_PCIE_INDEX2/DATA2`, full-width PCIe indirect index/data windows.
- `BIF_BX2_SBIOS_SCRATCH_0..3` and `BIF_BX2_BIOS_SCRATCH_0..15`, full-width scratch registers used for firmware/BIOS/display handoff state.
- `BIF_BX2_BIF_RLC_INTR_CNTL`, `BIF_BX2_BIF_VCE_INTR_CNTL`, and `BIF_BX2_BIF_UVD_INTR_CNTL`, with command-complete, self-recovered hang, FLR-required hang, VM-busy transition, and UVD instance-select fields.
- `BIF_BX2_GFX_MMIOREG_CAM_ADDR0..7` and matching `CAM_REMAP_ADDR0..7`, each with 20-bit CAM/remap addresses.
- `BIF_BX2_GFX_MMIOREG_CAM_CNTL`, `CAM_ZERO_CPL`, `CAM_ONE_CPL`, and `CAM_PROGRAMMABLE_CPL`, controlling which CAM entries are enabled and how completion behavior is represented.

These families are integration points for indirect PCIe register access, firmware scratch communication, block interrupt routing, and graphics MMIO remapping.

### RCC BIF and Device Port Straps

The `nbio_nbif0_rcc_strap_BIFDEC1` address block starts with `RCC_STRAP3_RCC_BIF_STRAP0..6`. These strap registers describe platform and PCIe fabric capabilities or policy, including Gen3/Gen4 disable/kill pins, VGA/BIOS ROM/memory aperture settings, PX capability, error-ignore controls, PME support, FLR/link-reset behavior, margining/DLF/PHY 16 GT/s capability, SWUS aperture settings, link-down DMA-drop behavior, power-break deglitching, ASPM/L0s/L1/LDN timers, SMN error response behavior, emergency power reduction support, and related link-management controls.

`RCC_STRAP3_RCC_DEV0_PORT_STRAP0..9` defines downstream/root-port style capabilities for device 0. Covered fields include ARI/ACS/AER, completion-abort error enable, downstream device/vendor/subsystem IDs, interrupt pin, max payload, max link width, lane equalization presets, power-management support, atomic routing/64-bit atomic support, virtual-channel support, DLF support, ACS subfeatures, MSI map/SSID, CRS, RTM presence detect, 10-bit tag capability, TPH completer support, extended MSI message data capability, port number, revision IDs, bus/device/function identity, and packed power-budget entries.

These strap fields are normally sampled from firmware/strap state and drive PCIe capability presentation and low-level link behavior. They are hardware topology and policy state, not general runtime knobs.

### Endpoint Function Straps for Device 0 F0 and F1

`RCC_STRAP3_RCC_DEV0_EPF0_STRAP*` defines endpoint function 0 identity and capability straps. The covered fields include device/vendor ID, revision/class code, function enable, D1/D2 support, SR-IOV VF device ID and supported page size, SR-IOV enable and total VFs, 64-bit BAR disable, soft reset behavior, resize BAR, PASID width and PASID feature support, MSI/MSI-X capability controls, ARI/AER/ACS/ATS, DPA, DSN, virtual-channel, page request, poisoned advisory nonfatal, power enable, subsystem IDs, SMN error mask behavior, VF resize BAR, clock power-management, true PM status, atomic/FLR/PME/interrupt/AUX power support, subsystem vendor ID, doorbell/ROM/IO/memory/register aperture sizes, VF aperture sizes, VGA disable, VF MSI capability, VF mapping mode, outstanding page request capacity, BAR compliance, VF register protection disable, framebuffer always-on, completion type, and GPU IOV VSEC revision.

`RCC_STRAP3_RCC_DEV0_EPF1_STRAP*` mirrors a subset for endpoint function 1. Function 1 has identity, class/vendor IDs, no-soft-reset/resize-BAR/PASID/MSI/AER/ACS/ATS/DPA/DSN/VC capabilities, poisoned advisory, power/subsystem/MSI/MSI-X/SMN/clock-PM/true-PM fields, atomic/FLR/PME/interrupt/AUX power support, subsystem vendor ID, and an aperture 0 enable/prefetchable/64-bit BAR strap. Empty comments for `EPF1_STRAP10..12` and `EPF1_STRAP7` are generated placeholders in this chunk with no field macros.

These endpoint strap macros are directly tied to PCI configuration-space capability exposure, SR-IOV behavior, PASID/ATS/page-request features, interrupt capability, and BAR sizing.

### Endpoint PCIe Control, Interrupts, LTR, DPA, and TX Controls

The `nbio_nbif0_rcc_ep_dev0_BIFDEC1` block defines endpoint PCIe runtime/control fields for device 0:

- `RCC_EP_DEV0_3_EP_PCIE_SCRATCH` is a full-width scratch register.
- `RCC_EP_DEV0_3_EP_PCIE_CNTL` controls unsupported-request error reporting, malformed atomic ops, and ignoring LTR messages as UR.
- `RCC_EP_DEV0_3_EP_PCIE_INT_CNTL` and `RCC_EP_DEV0_3_EP_PCIE_INT_STATUS` expose enable/status bits for correctable, nonfatal, fatal, user-detected, miscellaneous, and power-state-change interrupts.
- `RCC_EP_DEV0_3_EP_PCIE_RX_CNTL2`, `BUS_CNTL`, and `CFG_CNTL` control invalid-PASID UR handling, immediate PMI behavior, and access to hidden Gen2/Gen3/Gen4 registers.
- `RCC_EP_DEV0_3_EP_PCIE_TX_LTR_CNTL` configures private snoop and non-snoop LTR short/long values, requirements, message-disable in non-D0 power states, LTR reset on data-link down, flow-control checking for L1, and D-state using write-data behavior.
- Function 1 DPA substate power allocation registers `RCC_EP_DEV0_2_PCIE_F1_DPA_SUBSTATE_PWR_ALLOC_0..7` provide 8-bit allocation fields.
- `RCC_EP_DEV0_3_EP_PCIE_STRAP_MISC` and `STRAP_MISC2` expose master 64-bit address and TPH support straps.
- Function 0 DPA capability/status/control fields include transition-latency units/values, power-allocation scale, latency indicator bits, substate status, compliance mode, and `F0_DPA_SUBSTATE_PWR_ALLOC_0..7`.
- `RCC_EP_DEV0_3_EP_PCIE_PME_CONTROL` defines a PME service timer, and `RCC_EP_DEV0_3_EP_PCIEP_RESERVED` is a full-width reserved field.
- The chunk ends after `RCC_EP_DEV0_3_EP_PCIE_TX_CNTL` shift fields for SNR override, RO override, and TPH disable for functions 0-2; the matching masks are in the next chunk.

## Control Flow and State Behavior

There is no executable control flow in this header. The control flow affected by this chunk lives in the C files that include the generated register headers. At compile time, the macros determine how those files build register values and extract hardware state.

The state represented here is hardware state. Some fields are persistent configuration or strap-derived capability state, such as PCIe generation support, BAR sizes, SR-IOV totals, PASID/ATS/ACS/AER capabilities, endpoint function enablement, link timers, and DPA/LTR settings. Other fields are status or event latches, such as parity error status bits, sync-flood status, APML status, egress poison status, interrupt status, and DPA substate status. Still others are action policy bits, such as APML enable, interrupt-generation selection, link-disable enable, sync-flood enable, and poison severity/mask settings.

Several fields are command-like or clear/trigger style rather than durable configuration. `APML_TRIGGER__APML_NMI_TRIGGER`, APML/NMI routing fields, interrupt status fields, and indirect index/data windows require sequencing from the owning NBIO, RAS, display, or PCIe code. The masks alone do not encode ordering, clear-on-write semantics, polling requirements, privilege level, or timeout policy.

## Dependencies and Integration Points

This chunk depends on the generated NBIO header set:

- `nbio_7_2_0_offset.h` provides the register addresses and base indices for the names represented here.
- Other `nbio_7_*_sh_mask.h` files provide similar but not interchangeable layouts for other ASIC revisions.
- AMDGPU helper macros in the driver consume the generated `__SHIFT` and `_MASK` names through field composition/extraction helpers.

Observed integration points in this source tree include:

- `amdgpu/nbio_v7_2.c`, which includes this header and programs NBIO registers through SOC15 and PCIe-port helpers. Nearby code uses the same generated convention for revision IDs, framebuffer access, SDMA/VCN/IH doorbell ranges, doorbell aperture control, interrupt control, medium-grain clock gating, and PCIe request-size controls.
- AMD display resource files such as `dcn315_resource.c`, `dcn314_resource.c`, and `dcn36_resource.c`, which define/register NBIO BIOS scratch registers, and display BIOS/parser/helper code that reads or writes BIOS scratch state for display handoff and power/display behavior.
- RAS and platform-management paths that would use the parity, sync-flood, poison, APML, and action-control fields to route errors to interrupts, APML, NMI, link disable, or sync flood.
- PCIe/SR-IOV/virtualization setup paths that rely on strap fields for function capability exposure, BAR aperture sizing, PASID/ATS/page-request support, VF mapping, and ACS/AER/ARI behavior.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can write unrelated NBIO fields, causing bad PCIe capability exposure, broken BAR/doorbell apertures, lost interrupts, incorrect RAS routing, or GPU/device enumeration failures.
- The repeated action-control families are easy to corrupt mechanically. PCIE0 ports A-G and NBIF1 ports A-C share a similar layout, but the register names identify different error sources.
- RAS fields are policy-sensitive. Misprogramming APML, NMI, link-disable, sync-flood, or severity/mask fields can either hide real hardware faults or escalate recoverable conditions into disruptive events.
- Poison and parity status fields are diagnostic. Treating status bits as configuration, or clearing/masking them without preserving reporting policy, can lose root-cause evidence.
- Strap fields are topology and capability state. Overriding SR-IOV, PASID, ATS, ACS, AER, BAR sizing, link generation, lane equalization, DPA, LTR, or PME fields inconsistently with platform firmware and hardware fuses can break PCIe enumeration, isolation, power management, or peer-to-peer behavior.
- BIOS scratch registers are shared handoff state. Writes must respect display/BIOS protocols; careless updates can confuse display detection, panel control, or firmware-visible state.
- Indirect index/data windows need strict access ordering and correct aperture selection. Racing or misaddressing these windows can read/write the wrong PCIe/MMIO register.
- The chunk ends mid-register at `RCC_EP_DEV0_3_EP_PCIE_TX_CNTL`; per-file synthesis must stitch the next chunk before making complete claims about TX control fields.

## Test and Validation Signals

Useful validation is mainly build, bring-up, and hardware integration coverage:

- Build AMDGPU and display code that includes `nbio/nbio_7_2_0_sh_mask.h`; this catches missing or renamed generated macros.
- NBIO bring-up tests should verify revision ID reads, framebuffer access enable/disable, doorbell aperture programming, interrupt setup, and PCIe-port register access through the matching offset/mask headers.
- RAS validation should exercise parity status/counters, sync-flood status, APML status/control/trigger, poison status/mask/severity, and action-control routing for correctable, nonfatal, fatal, SERR, and parity classes.
- PCIe enumeration and capability tests should validate strap-derived device/vendor/class IDs, BAR sizes, MSI/MSI-X, AER/ACS/ARI/ATS/PASID/page-request, SR-IOV/VF mapping, FLR, PME, DPA, LTR, and link-generation behavior.
- Display tests should cover BIOS scratch register handoff paths, especially panels or display configurations that read or update BIOS scratch state during initialization, power changes, or connector detection.
- Virtualization/SR-IOV tests should confirm VF count/page-size/device ID, VF BAR/doorbell/register/memory apertures, VF MSI capability, VF register protection, and GPU IOV VSEC revision behavior.
- Reliability tests should confirm poison/parity/APML events are neither masked accidentally nor escalated incorrectly, and that status read/clear behavior preserves actionable diagnostics.

## Unresolved Cross-Chunk References

The first line is already inside `PARITY_ERROR_STATUS_UCP_GRP2`, so the register comment and IDs 0-14 shift/mask definitions are in the previous chunk. The last covered line is `RCC_EP_DEV0_3_EP_PCIE_TX_CNTL__TX_F2_TPH_DIS__SHIFT`; masks for `RCC_EP_DEV0_3_EP_PCIE_TX_CNTL` and later endpoint PCIe fields such as requester ID, error control, RX control, and link-speed strap fields are in the next chunk. The merge lane should combine adjacent chunks before producing the final per-file research document.
