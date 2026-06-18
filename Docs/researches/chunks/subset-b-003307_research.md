# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 115932-118382

## Scope And Purpose

This chunk is part of AMDGPU's generated NBIO 7.7.0 shift/mask header. It contains C preprocessor constants for field positions and bit masks, not executable driver logic. The covered range defines 2,138 `#define` entries across 283 register comment blocks, with address-block boundaries for NBIO error handling, IOAPIC, IOMMU L2A, BIF indexed access, BIOS scratch registers, RCC straps, endpoint/downstream PCIe controls, and RCC SR-IOV/GPUIOV controls.

The purpose of these constants is to let C code manipulate NBIO registers symbolically through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, and PCIe-port indexed accessors. The companion `nbio_7_7_0_offset.h` supplies register addresses; this file supplies how fields are packed inside the 32-bit register values.

The chunk starts in the middle of a repeated error-action-control family. Its first visible line is the mask for `PCIE0PortAExtFatal_ACTION_CONTROL__SyncFlood_En`, so the full `PCIE0PortAExtFatal_ACTION_CONTROL` block begins just before this range. The rest of the visible range is complete enough to describe the repeated action-control pattern and later address blocks.

## Important APIs, Types, And Register Families

There are no functions, structs, enums, global variables, inline helpers, or callable APIs in this chunk. The public interface is the generated macro namespace:

- `REGISTER__FIELD__SHIFT` constants encode right-shift amounts.
- `REGISTER__FIELD_MASK` constants encode the field's bit mask in the original register value.
- Full-width fields use `0xFFFFFFFFL`; single-bit enables/status bits use one-bit masks; packed numeric fields use contiguous multi-bit masks.

The first major family is PCIe/NBIF error action control. Repeated blocks for `PCIE0PortA` through `PCIE0PortF` and `NBIF1PortA` through `NBIF1PortC` expose the same core fields for SERR, internal fatal, internal non-fatal, internal corrected, external fatal, external non-fatal, external corrected, and parity-error events. Each action-control register uses `APML_ERR_En`, `IntrGenSel`, `LinkDis_En`, and `SyncFlood_En`, allowing firmware or driver policy to choose APML signaling, interrupt generation, link disable behavior, and sync-flood escalation for a given port/error class.

The next error and RAS-related family covers `SYNCFLOOD_STATUS`, `NMI_STATUS`, `POISON_ACTION_CONTROL`, `INTERNAL_POISON_STATUS`, `INTERNAL_POISON_MASK`, `EGRESS_POISON_STATUS_LO`, `EGRESS_POISON_STATUS_HI`, `EGRESS_POISON_MASK_LO`, `EGRESS_POISON_MASK_HI`, `EGRESS_POISON_SEVERITY_DOWN`, `EGRESS_POISON_SEVERITY_UPPER`, `APML_STATUS`, `APML_CONTROL`, and `APML_TRIGGER`. These fields describe status bits for sync-flood and NMI sources, poison-status bitmaps, masks and severity maps for egress poison events, and APML output/NMI/sync-flood controls.

The `nbio_iohub_nb_ioapiccfg_ioapic_cfgdec` block contributes `FEATURES_ENABLE`, including IOAPIC ID extension, sideband features, secondary IOAPIC enablement, processor mode, and INTx level-only mode.

The `nbio_iohub_iommu_l2a_l2acfg` block defines a broad IOMMU L2A control surface: performance counter selectors and count registers, L2 status, L2 cache-control registers, DTC/ITC/PTC-A cache invalidation and bypass controls, hash and way controls, credit controls, update-filter behavior, error-rule controls, clock gating, page-size controls, memory power-gating thresholds, IP power-gating status/control, and ECO bits. Important examples include `L2_CONTROL_0`, `L2_DTC_CONTROL`, `L2_ITC_CONTROL`, `L2_PTC_A_CONTROL`, `L2_CREDIT_CONTROL_2`, `L2_L2A_CK_GATE_CONTROL`, `L2_L2A_PGSIZE_CONTROL`, and `L2_PWRGATE_CNTRL_REG_3`.

The `nbio_nbif0_bif_bx_pf_SYSPFVFDEC` block defines the PF2 memory-mapped indexed access aperture: `BIF_BX_PF2_MM_INDEX`, `BIF_BX_PF2_MM_DATA`, and `BIF_BX_PF2_MM_INDEX_HI`. These fields split an indirect MMIO offset across low/high index registers and provide a 32-bit data register.

The `nbio_nbif0_bif_bx_SYSDEC` block defines PCIe indexed access registers, SBIOS and BIOS scratch registers, interrupt-control registers for RLC/VCE/UVD paths, and GFX MMIO register CAM address/remap/control/completion fields. `BIF_BX2_PCIE_INDEX`, `BIF_BX2_PCIE_DATA`, `BIF_BX2_PCIE_INDEX2`, and `BIF_BX2_PCIE_DATA2` are the visible indexed PCIe register windows. `BIF_BX2_SBIOS_SCRATCH_0..3` and `BIF_BX2_BIOS_SCRATCH_0..15` provide full-width scratch fields. The CAM fields (`BIF_BX2_GFX_MMIOREG_CAM_ADDR*`, `BIF_BX2_GFX_MMIOREG_CAM_REMAP_ADDR*`, `BIF_BX2_GFX_MMIOREG_CAM_CNTL`, and completion-control registers) describe remapping of graphics MMIO register accesses.

The `nbio_nbif0_rcc_strap_BIFDEC1` block is a large strap-definition area. `RCC_STRAP3_RCC_BIF_STRAP0..6` describe BIF-wide strap capabilities and policy, including Gen3/Gen4/Gen5 disable/kill pins, link reset behavior, ROM/fuse strap validity, DLF, PHY speed enables, SWUS aperture policy, link-down DMA behavior, ASPM/LTR/power-brake timers, emergency power reduction, and register-protection behavior. `RCC_STRAP3_RCC_DEV0_PORT_STRAP0..13` describe downstream/root-port-visible PCIe capabilities for device 0, including ARI, ACS, AER, device/subsystem IDs, link widths, payload sizes, equalization, PM/LTR/OBFF/MSI/atomic/VC/SSID features, 10-bit tags, lane equalization, retimer/modified TS details, alternate protocol capability, and power budget data. `RCC_STRAP3_RCC_DEV0_EPF*` fields then expose endpoint-function strap values for function identity, IDs, class code, revision, BAR sizing, MSI/MSI-X, SR-IOV/ARI/ACS/AER/PASID-like features, and related endpoint capability advertisement.

The `nbio_nbif0_rcc_ep_dev0_BIFDEC1` block covers endpoint-side runtime controls for device 0. It includes endpoint PCIe scratch/control/int-status registers, RX/TX controls, bus/config controls, LTR transmit controls, dynamic power allocation substates for F0 and F1, PME control, requester ID, error handling, RX completion timeout policy, and link-speed strap bits through `RCC_EP_DEV0_3_EP_PCIE_LC_SPEED_CNTL`.

The `nbio_nbif0_rcc_dwn_dev0_BIFDEC1` and `nbio_nbif0_rcc_dwnp_dev0_BIFDEC1` blocks cover downstream-port controls. They include reserved/scratch/control/config/RX fields, downstream bus-control bits, strap fields for atomic ops, relaxed ordering, no-snoop, requester/completer support, and downstream port error controls. `RCC_DWNP_DEV0_3_PCIE_ERR_CNTL` has reporting-disable and clear bits for corrected, non-fatal, and fatal received errors; `RCC_DWNP_DEV0_3_PCIE_RX_CNTL` has ignore/timeout bits; `RCC_DWNP_DEV0_3_PCIE_LC_SPEED_CNTL` gates Gen2 through Gen5 support; and `RCC_DWNP_DEV0_3_LTR_MSG_INFO_FROM_EP` exposes the full LTR message payload received from an endpoint.

The `nbio_nbif0_rcc_dev0_epf0_BIFPFVFDEC1[13440..14975]` block covers EPF0/PF-VF decoded RCC state. It includes invalid SR-IOV register access status, doorbell-read status, doorbell aperture enable, config memory size/reserved fields, and an IOV function identifier with an IOV enable bit.

The final `nbio_nbif0_rcc_dev0_BIFDEC1` block covers device-level RCC controls. It includes SR-IOV invalid-access interrupt enable, BACO request disable bits for ROM/AZ, doorbell aperture reset enable, VDM support flags, PCIe margining capability parameters, GPUIOV region and host-VM enable bits, console IOV mode and VF layout, peer register ranges, and `RCC_DEV0_3_RCC_BUS_CNTL` fields for PMI disable paths, root-error logging, poisoned completion logging, downstream completion-abort/unsupported-request behavior, max-payload-size policy, and max-read-request-size policy.

## Control Flow And Runtime Use

This header chunk has no local control flow. The runtime pattern is indirect:

1. ASIC-specific code includes `nbio/nbio_7_7_0_offset.h` and `nbio/nbio_7_7_0_sh_mask.h`.
2. The offset macro selects a register address or indexed aperture.
3. The shift/mask macros in this chunk extract, test, clear, or compose individual fields.
4. AMDGPU register helpers read or write the resulting 32-bit value through MMIO, SOC15, or PCIe-port access paths.

The direct NBIO 7.7 integration point found in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes this header with the matching offset header. That implementation uses the generated constants to implement `nbio_v7_7_funcs`, covering revision-ID reads, memory-controller access enablement, memory-size reads, doorbell range setup, doorbell aperture setup, IH interrupt controls, HDP flush offsets, PCIe index/data offsets, clock-gating and light-sleep controls, NBIO initialization, HDP register remapping, and MMIO remap setup.

Most specific macros in this chunk are not hand-referenced by `nbio_v7_7.c`; they are still part of the generated hardware ABI available to NBIO, PCIe, RAS, IOMMU, SR-IOV, virtualization, diagnostics, and future feature code. A generated header can be consumed by common register helpers, debug tooling, or out-of-tree bring-up patches even when a given field has no direct in-tree call site today.

## State And Persistence Behavior

The macros themselves hold no runtime state. They compile into immediate constants and do not allocate memory, acquire locks, perform I/O, or persist data.

The hardware registers described by the macros are stateful. Error-action controls, APML/poison masks, IOAPIC features, IOMMU L2A controls, BIF index windows, scratch registers, strap latches, PCIe control registers, doorbell aperture enables, GPUIOV/HostVM settings, and bus-control policy all live in NBIO hardware state. Their persistence depends on the register's hardware reset domain, firmware ownership, power state, virtualization mode, and whether values are strap-latched, writable, write-one-to-clear, or status-only.

BIOS/SBIOS scratch registers are explicitly intended as firmware/driver communication or diagnostic storage, but this header does not describe ownership or lifetime. Strap fields often reflect fuse/ROM/strap-derived defaults and may be read-only or write-protected after strap capture, despite being represented here as simple bit masks. Poison, sync-flood, NMI, and error-received clear fields can have side effects when written; the mask definitions do not encode clear-on-write behavior.

Any runtime code changing L2A cache, invalidation, power-gating, SR-IOV, doorbell, or PCIe link/error bits must reapply or verify settings after GPU reset, suspend/resume, BACO, function-level reset, virtualization transitions, or firmware-driven power-state changes if hardware loses or rewrites state.

## Dependencies And Integration Points

The direct companion dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h`. Offsets and field masks must come from the same ASIC generation. Mixing NBIO 7.7.0 offsets with another generation's shift/mask file can compile cleanly while reading or modifying the wrong field.

AMDGPU's register helper layer is the main consumer abstraction. `REG_SET_FIELD` and `REG_GET_FIELD` rely on the exact `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` naming convention. SOC15 and PCIe-port helpers rely on matching address definitions from the offset header. Generated defaults, reset values, access permissions, and firmware ownership are not present in this chunk, so consumers must consult other generated headers and hardware documentation for safe write behavior.

The RAS and platform-management integration points are the action-control, poison, sync-flood, NMI, and APML fields. These fields bridge NBIO hardware events into interrupt generation, APML signaling, link disable, and system-level sync-flood/NMI escalation policy.

The IOMMU integration point is the L2A block. Fields for cache controls, page sizes, invalidation selection, parity, credit allocation, update filtering, and power gating affect address translation and IOMMU performance/robustness. Incorrect settings can surface as DMA faults, ATS/PASID behavior issues, or hard-to-reproduce latency/performance regressions rather than a local compile failure.

The virtualization integration points are the SR-IOV, GPUIOV, HostVM, console IOV, peer register range, and PF/VF decoded EPF0 fields. These fields influence VF access behavior, invalid register access reporting, doorbell aperture exposure, function identifiers, and host-visible GPU virtual-memory behavior.

The PCIe integration points are broad: root/downstream/endpoint capability straps, link-speed enables through Gen5, dynamic power allocation, LTR, PME, ACS/AER/ARI/MSI/MSI-X/atomic/VC/10-bit tag feature advertisement, error reporting, completion timeout, requester IDs, and payload/read-request policies. These fields must align with both AMD's NBIO register database and PCIe capability semantics.

## Risks And Edge Cases

The highest risk is generated-register drift. A one-bit change in a mask or shift can corrupt an unrelated field while still compiling. This is especially dangerous for packed strap registers, link-control fields, poison severity masks, IOMMU cache controls, and SR-IOV/doorbell aperture controls.

The range begins mid-register-block, so chunk-level analysis must not assume `PCIE0PortAExtFatal_ACTION_CONTROL` is fully defined here. Merge/reconciliation should combine adjacent chunks before making whole-file completeness claims for that register.

Repeated action-control blocks are intentionally redundant. Refactoring them into hand-written macros or shared aliases would risk breaking the generated naming contract expected by `REG_SET_FIELD`/`REG_GET_FIELD` and by ASIC-specific call sites.

Full-width `0xFFFFFFFFL` masks do not imply a register is freely writable. Many status, scratch, strap, indirect-data, severity, and config-size fields have access restrictions or side effects not represented in the mask header.

Strap fields are particularly easy to misuse. A name beginning with `STRAP_` may describe latched hardware configuration or advertised PCIe capability, not a normal mutable policy bit. Writing these fields without checking write-enable/protection behavior can be ineffective or destabilizing.

Error-clear fields such as corrected/non-fatal/fatal received clear bits and poison/status controls may be write-one-to-clear or otherwise side-effectful. Generic read-modify-write code that preserves stale status bits could accidentally clear, retrigger, or mask real errors.

IOMMU L2A invalidation and bypass controls can affect address translation correctness. Changing `DTCSoftInvalidate`, `ITCSoftInvalidate`, `PTCASoftInvalidate`, cache bypass, way disable, page-size, or credit fields without proper sequencing can cause stale translations, lost invalidations, or performance collapse.

Virtualization fields have isolation implications. Incorrect SR-IOV invalid-access handling, doorbell aperture enablement, GPUIOV region sizing, HostVM enablement, console IOV offsets/strides, or peer register ranges can expose registers to the wrong function or prevent VFs from operating.

PCIe capability strap changes have compatibility risk. Incorrect Gen speed enablement, payload/read-request limits, ACS/AER/ARI/atomic/MSI/MSI-X capability bits, completion timeout policy, LTR/PM/OBFF behavior, or requester IDs can break link training, enumeration, error reporting, peer-to-peer access, or power management.

## Test Signals

Compile coverage should build AMDGPU with NBIO 7.7 support so `nbio_v7_7.c` includes `nbio_7_7_0_offset.h` and this `nbio_7_7_0_sh_mask.h` together. Warnings or missing macro errors are the first signal of generated-header mismatch.

Generated-header consistency checks should verify that each `REGISTER__FIELD__SHIFT` has a matching `REGISTER__FIELD_MASK`, that masks align with their shifts and expected widths, and that registers in this chunk have matching address macros where they are meant to be addressable through `nbio_7_7_0_offset.h`.

Runtime smoke tests on NBIO 7.7 hardware should cover GPU probe, PCIe enumeration, firmware handoff, doorbell aperture setup, IH interrupt delivery, HDP flush behavior, and memory-size reporting. These exercise the include pairing and related generated-field conventions even when not every field in this chunk is directly touched.

RAS and error-handling tests should inject or observe PCIe corrected/non-fatal/fatal events, poison events, APML signaling, sync-flood/NMI policy, and error clear behavior where platform support exists. Expected signals are correct interrupt/APML routing, no unintended link disable, and status bits that clear only under the intended sequence.

IOMMU tests should stress ATS/PASID-style translation, DMA fault handling, invalidation paths, and suspend/resume or reset recovery. Useful signals include no stale translation faults, stable DMA under load, and no unexpected performance drop after L2A cache or power-state transitions.

Virtualization tests should run PF and VF probe paths, invalid VF register access reporting, doorbell access, GPUIOV region handling, HostVM/console IOV configuration, and FLR or VF reset sequences. The important signal is correct isolation and functional VF doorbells without PF-only register exposure.

PCIe tests should cover link training across supported speeds, payload/read-request negotiation, AER/ACS/ARI/MSI/MSI-X capability exposure, DPC/error-reporting behavior, LTR/PME/power-management transitions, and peer-to-peer access where available.

Power-management and reset tests should include BACO, suspend/resume, runtime power transitions, and GPU reset because NBIO register state described by this chunk may be strap-latched, firmware-owned, reset-lost, or reinitialized by `nbio_v7_7_funcs` and related platform code.
