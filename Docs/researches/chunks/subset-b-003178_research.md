# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 43965-46431

## Purpose

This chunk is a generated AMD NBIO 7.2 shift/mask slice for RCC PCIe register fields. It defines C preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for endpoint-function strap registers and RCC endpoint/downstream port control registers. The companion offset header supplies register addresses; this file supplies the field layout needed to encode or decode register values.

The range starts in the middle of `RCC_STRAP2_RCC_DEV0_EPF1_STRAP0`, covers strap fields for multiple PCIe endpoint functions, then transitions into RCC port-decode blocks for `DEV0_2`, `DEV1`, and `DEV2`. It ends on the `RCC_DWN_DEV2_DN_PCIE_CNTL` comment, before that register's field definitions. This is not executable driver logic; it is a hardware contract exposed as macros.

## Public Surface In This Chunk

The public API is the macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the register storage width.
- Comment headings identify register names and generated address blocks, but do not define symbols by themselves.

No C types, functions, structs, enums, inline helpers, or storage objects are defined here. Consumers use these macros with register access helpers, field packing helpers such as `REG_SET_FIELD`/`REG_GET_FIELD` style macros elsewhere in AMDGPU, or direct mask/shift operations.

## Register Coverage

The first half is dominated by endpoint-function strap definitions:

- Continuation of `RCC_STRAP2_RCC_DEV0_EPF1_STRAP0`, then `RCC_STRAP2_RCC_DEV0_EPF1_STRAP2` through `STRAP14`.
- `RCC_DEV0_EPF2` through `RCC_DEV0_EPF7` strap sets.
- `RCC_DEV1_EPF0` and `RCC_DEV1_EPF1` strap sets, plus empty marker comments for `DEV1_EPF2` through `DEV1_EPF5`.
- `RCC_DEV2_EPF0`, `RCC_DEV2_EPF1`, and `RCC_DEV2_EPF2` strap sets.

The strap fields describe PCI configuration identity and capability exposure: device ID, major/minor revision, function enable, legacy device type, D1/D2 support, no-soft-reset, resizable BAR, PASID width and permission bits, AER/ACS/ATS/ARI/DPA/VC capability straps, MSI/MSI-X enable and table sizing, subsystem/vendor IDs, power management capability bits, atomic operation support, FLR support, interrupt pin, aperture enable/prefetchable bits, class code, and vendor ID. Some commented strap registers have no fields in this slice, indicating generated holes or registers with no named fields.

The second half covers RCC port decode blocks:

- `nbio_nbif0_rcc_dev0_RCCPORTDEC` with `RCC_DEV0_2_*` register fields.
- `nbio_nbif0_rcc_ep_dev0_RCCPORTDEC` with `RCC_EP_DEV0_2_*` endpoint PCIe fields.
- `nbio_nbif0_rcc_dwn_dev0_RCCPORTDEC` and `nbio_nbif0_rcc_dwnp_dev0_RCCPORTDEC` downstream/downstream-port fields.
- Equivalent `DEV1` blocks.
- `DEV2` RCC and endpoint blocks, ending at the start of its downstream block.

The RCC port fields include VDM support, bus control, miscellaneous feature control, link state control, requester ID restore, LTR switch latency, multi-host arbitration, PCIe lane margining parameters, endpoint interrupt control/status, endpoint PCIe control, RX/TX behavior, LTR transmission, DPA capability/control/substate power allocations, PME service timing, requester ID fields, AER/error handling, link-speed strap bits, downstream hidden config decode controls, downstream FLR extension mode, and downstream strap bits.

## Important APIs And Field Families

The most important field families are:

- Endpoint strap identity and enablement: `STRAP_DEVICE_ID`, `STRAP_MAJOR_REV_ID`, `STRAP_MINOR_REV_ID`, `STRAP_FUNC_EN`, `STRAP_CLASS_CODE_*`, and `STRAP_VENDOR_ID` determine what functions and identities the hardware presents.
- PCIe capability exposure: `STRAP_AER_EN`, `STRAP_ACS_EN`, `STRAP_ATS_EN`, `STRAP_ARI_EN`, `STRAP_PASID_EN`, `STRAP_DPA_EN`, `STRAP_VC_EN`, `STRAP_RESIZE_BAR_EN`, `STRAP_FLR_EN`, and TPH/MSI/MSI-X-related straps gate features visible to software.
- Addressing and BAR layout: `STRAP_APER*_EN`, `STRAP_APER*_PREFETCHABLE_EN`, `STRAP_APER0_64BAR_EN`, and related aperture fields describe how endpoint apertures are exposed.
- Error and interrupt controls: endpoint `EP_PCIE_INT_CNTL`, `EP_PCIE_INT_STATUS`, `EP_PCIE_ERR_CNTL`, and RX error-ignore bits control or report correctable, non-fatal, fatal, miscellaneous, PASID, prefix, timeout, malformed atomic, and poisoned completion behavior.
- Power and latency controls: `PMI_*`, `PME_SERVICE_TIMER`, `CLK_PM`, `TRUE_PM_STATUS`, `TX_LTR_CNTL`, `LTR_MSG_INFO_FROM_EP`, DPA capability/control/substate allocation, and common link control fields affect power management and latency tolerance behavior.
- Link and margining controls: `LC_GEN2/3/4_EN_STRAP`, link-down entry/exit fields, lane margining capability fields, and downstream-port link control bits expose PCIe link capability, training, and diagnostics knobs.
- Downstream/root-complex integration: `RCC_BUS_CNTL`, downstream `DN_PCIE_*`, `DWNP_*`, and requester ID restore fields mediate root-complex routing, hidden register decode, upstream/downstream error policy, and endpoint requester IDs.

## Control Flow

This header has no runtime control flow. The effective flow is compile-time:

1. A driver source includes `nbio_7_2_0_sh_mask.h` for an ASIC that uses NBIO 7.2.
2. The driver selects an offset macro from a matching generated offset header and a shift/mask macro from this header.
3. Register access code reads, modifies, writes, or decodes the hardware register value.
4. Any hardware behavior, ordering, locking, or side effects occur in the caller and in the device, not in this header.

Because there is no executable code, branch coverage and function-level behavior are not applicable. The important control property is that field names must stay synchronized with register offsets, access widths, and the hardware generation.

## State And Persistence

This chunk stores no driver state. The state represented by these macros lives in NBIO/RCC hardware registers and PCIe-visible configuration behavior. Depending on the field, state may be strap-derived at hardware initialization, writable by firmware or the kernel through MMIO/config paths, latched by link training, or reported as live hardware status.

Persistent or externally visible effects include endpoint function visibility, PCI IDs and class codes, BAR/aperture layout, MSI/MSI-X capability presentation, AER and error reporting policy, PASID/ATS/ACS/ARI capabilities, requester ID behavior, link-speed advertisement, DPA and LTR behavior, PME timing, and downstream-port error/logging behavior. Some fields are status or timer-expired bits; others are controls or strap mirrors. The macros do not encode which fields are read-only, write-one-to-clear, strap-only, volatile, or sequence-sensitive.

## Dependencies And Integration Points

The direct generated-header dependency is the matching NBIO 7.2 offset/default/register header set under `drivers/gpu/drm/amd/include/asic_reg/nbio/`. The offset header supplies addresses; this shift/mask header supplies field geometry; default headers provide reset/default values for many registers.

`drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c` includes this header, so NBIO v7.2 driver code is the central integration point. Other AMDGPU and display code may indirectly depend on the same generated constants through shared register helpers and ASIC-specific register programming tables. The semantic dependencies are AMD's NBIO 7.2 register specification plus the PCI/PCIe specifications for endpoint functions, MSI/MSI-X, AER, ACS, ATS, PASID, ARI, TPH, DPA, LTR, PME, link control, and lane margining.

The names are source-tree aligned with the generated address block comments. For example, `RCC_EP_DEV1_EP_PCIE_ERR_CNTL__AER_HDR_LOG_TIMEOUT_MASK` belongs to the `nbio_nbif0_rcc_ep_dev1_RCCPORTDEC` block, while `RCC_DWN_DEV1_DN_PCIE_CNTL__HWINIT_WR_LOCK_MASK` belongs to the downstream `DEV1` block. Code using these definitions must pair the correct device/function/block prefix with the correct offset macro; the preprocessor cannot detect a mismatched register/field pair if numeric widths happen to compile.

## Risks And Maintenance Notes

- The line range starts and ends mid-definition group. The start omits the earlier `RCC_STRAP2_RCC_DEV0_EPF1_STRAP0` shifts and masks, and the end stops before `RCC_DWN_DEV2_DN_PCIE_CNTL` fields. Adjacent chunks are needed for complete per-file reconciliation.
- Generated repetition makes review difficult. `DEV0` functions 2-7 and `DEV1`/`DEV2` endpoint blocks are highly similar but not identical; fields such as `ATS`, `ARI`, aperture 1 enablement, MSI-X table size, or empty strap markers vary by function.
- A stale shift or mask can silently program the wrong hardware bit. Since many values are single-bit feature enables, a one-bit displacement can invert feature exposure, error reporting, link behavior, or power-management semantics.
- Error-control fields can suppress or alter AER/UR/fatal/non-fatal reporting. Misuse can hide hardware faults from the PCI core or make expected unsupported-request paths noisy.
- Capability straps affect security and isolation semantics. ACS, ATS, PASID, ARI, TPH, and requester-ID fields interact with IOMMU, virtualization, peer-to-peer routing, and SR-IOV-style assumptions.
- Link, margining, LTR, DPA, and PME fields can affect power and stability. Writes without ASIC-specific sequencing may disrupt link training, latency reporting, or power-state transitions.
- `HWINIT_WR_LOCK` and hidden-register decode fields indicate access-control concerns. Code that writes them late or without checking hardware initialization state may block future programming or expose hidden config paths unexpectedly.
- The macros do not describe access width or side effects. Callers must know whether a register is MMIO, config-space backed, latched, volatile, write-one-to-clear, or strap-only.

## Test Signals

Useful validation signals for this chunk are:

- Compile coverage for `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c` and any translation unit that includes `nbio_7_2_0_sh_mask.h`.
- Generated-header consistency checks that each `__SHIFT` in the selected lines has the expected matching `_MASK`, and that every mask corresponds to the documented bit range.
- Cross-header checks that each register field here has a compatible offset macro in `nbio_7_2_0_offset.h` and, where applicable, a reset/default macro in the default header.
- Static checks for duplicated or missing endpoint-function strap patterns across `DEV0_EPF2` through `DEV0_EPF7`, while allowing intentional differences such as aperture count, `ATS` presence, `ARI` presence, and MSI-X table size fields.
- Hardware register dump comparison on NBIO 7.2 ASICs, especially for PCI IDs, class codes, BAR/aperture exposure, MSI/MSI-X capability, PASID/ACS/ATS/ARI capability bits, AER settings, LTR/DPA fields, and link speed strap bits.
- PCIe functional tests that exercise MSI/MSI-X delivery, AER reporting, FLR, resizable BAR visibility, PASID/ATS paths where supported, link speed negotiation, PME/power transitions, and error injection without affecting unrelated endpoint functions.
- Runtime diagnostics from `lspci -vvxxx`, AMDGPU debugfs/register dumps, PCI AER logs, IOMMU/PASID traces, and suspend/resume or reset tests can reveal mismatches between these field definitions and actual hardware behavior.
