# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_11_0_sh_mask.h lines 49194-51624

## Purpose

This chunk is a generated AMD NBIO 7.11.0 shift/mask header segment. It exports preprocessor constants for bitfield positions and masks in NBIO PCIe configuration, RCC port decode, and BIF reset-control registers. The file is hardware metadata only: it has no functions, structs, variables, locks, allocations, or executable control flow.

The range starts mid-way through the `BIF_CFG_DEV2_EPF6_0` PCIe endpoint-function block at `LINK_CNTL`, continues through endpoint PCIe capability and enhanced-capability registers, covers RCC endpoint/downstream/downstream-port control blocks for devices 0-2, and then enters the `nbio_nbif0_bif_rst_bif_rst_regblk` reset block. It ends inside the `DEV2_PF2_FLR_RST_CTRL` field definitions, so adjacent chunks are needed for complete analysis of the preceding `BIF_CFG_DEV2_EPF6_0_LINK_CAP` register and the following `DEV2_PF2_FLR_RST_CTRL` masks plus later reset registers.

Although the repository path is under a `ceph-client` mirror, this source is AMDGPU ASIC register metadata and has no direct distributed-filesystem behavior.

## Public Surface

The public API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's starting bit.
- `<REGISTER>__<FIELD>_MASK` gives the raw register mask, usually as a C integer literal with an `L` suffix.

The macros are intended to be used with companion address metadata from `nbio_7_11_0_offset.h` and AMDGPU bitfield helpers such as `REG_GET_FIELD` or `REG_SET_FIELD`, plus the NBIO/SOC15 register access path selected by the caller. This header does not provide register addresses, reset defaults, read/write permissions, side-effect rules, or sequencing requirements.

`drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c` includes both `nbio/nbio_7_11_0_offset.h` and this shift/mask header. Spot checks in the offset header show matching address entries for representative registers in this slice, including `regBIF_CFG_DEV2_EPF6_0_LINK_CNTL`, `regRCC_EP_DEV0_0_EP_PCIE_CNTL`, `regHARD_RST_CTRL`, and `regDEV2_PF2_FLR_RST_CTRL`. There is no sibling `nbio_7_11_0_default.h` in this tree, so default/reset-value validation for this NBIO version cannot rely on a local generated default header.

## Important Register Families

The `BIF_CFG_DEV2_EPF6_0` section describes one endpoint-function PCIe configuration space. It includes link control/status and PCIe 2.0 link/device capabilities: ASPM and PM control, link disable/retrain/common-clock/extended-sync controls, hardware autonomous width/speed disable bits, bandwidth interrupt enables/status, negotiated speed and width, DL active reporting, supported target link speeds, equalization status, de-emphasis, DRS signaling, RTM presence detection, AtomicOp/ARI/LTR/OBFF/10-bit-tag capability and enablement, completion-timeout controls, IDO enablement, emergency power reduction, and end-to-end TLP prefix support/blocking.

The same endpoint block then defines MSI and MSI-X capability layout: capability IDs and next pointers, MSI enablement, multi-message capability and enable fields, 64-bit address support, extended message data support, per-vector masking capability, message address/data registers for 32-bit and 64-bit forms, mask and pending-bit arrays, MSI-X table and PBA BIR/offset fields, table size, function mask, and MSI-X enable.

The endpoint enhanced-capability portion covers SATA capability/index/data registers, vendor-specific capability header/data fields, AER, BAR sizing/control, power budgeting, Dynamic Power Allocation, ACS, PASID, ARI, and RTR capability blocks. AER fields include uncorrectable status/mask/severity for DLP, surprise-down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned TLP egress blocked. Correctable AER fields include receiver, bad TLP/DLLP, replay rollover, replay timer timeout, advisory non-fatal, correctable internal, and header-log overflow status/masks. The AER capability/control group exposes first-error pointer, ECRC generation/check support and enablement, multi-header receipt support/enablement, four TLP header log dwords, and four TLP prefix log dwords.

The BAR enhanced capability defines supported BAR sizes and per-BAR control for BAR1 through BAR6, including BAR index, size, upper supported-size bits, and total BAR count. Power budgeting fields describe selected power data, base power, data scale, PM state/substate, power rail, type, and whether the system allocates the power budget. DPA fields describe transition latency, power-allocation scale, maximum substate, current substate control/status, and substate power-allocation registers 0-7.

Isolation and address-translation capability groups include ACS capability/control fields for source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, P2P egress control, direct-translated P2P, and egress-control vector size. PASID fields expose max PASID width, execute permission and privileged mode support, and their enables. ARI fields expose next function number, MFVC/ACS function group capability, ARI function group value, and related enables. RTR is represented by an enhanced-capability header and two data registers.

The `RCC_*` sections describe endpoint and downstream port control blocks for devices 0, 1, and 2. Endpoint blocks include scratch registers, PCIe control and interrupt control/status, RX controls, bus/config controls, TX LTR control, DPA capability/control/substate power allocation, PME service timer, TX control/requester ID, error controls, and LC speed control. Fields control or report behavior such as malformed AtomicOp handling, unsupported-request reporting suppression, ignoring LTR invalid-message URs, immediate PMI behavior, hidden-register decode enables for Gen2 through Gen5, completion-timeout suppression, TPH disablement, relaxed/no-snoop override, requester ID bus/device/function, TX LTR private snoop and no-snoop requirements, flow-control checks for L1, PME service timing, and endpoint interrupt enables/status for correctable, non-fatal, fatal, miscellaneous, unsupported request, and power-state-change events.

The downstream and downstream-port `RCC_DWN_*`/`RCC_DWNP_*` blocks repeat a smaller control set for devices 0-2. They include reserved/scratch words, general downstream PCIe control, config control, RX control, bus control, config decode enables, error-control fields, LC speed/control fields, and LTR message information from the endpoint. These fields affect how the internal downstream-facing ports expose hidden registers, handle LTR and UR conditions, and manage link control/speed behavior.

The `RCC_STRAP0_RCC_DEV0_EPF0_STRAP0` and `RCC_DEV0_EPF5_STRAP4` strap registers expose boot/configuration strap fields such as device ID, revision IDs, function enablement, D1/D2 support, legacy device type enablement, and strap-reserved or function-specific fields. These are hardware strap-derived configuration fields rather than ordinary runtime policy state.

The BIF reset section begins at `HARD_RST_CTRL`, `SELF_SOFT_RST`, `BIF_GFX_DRV_VPU_RST`, and `BIF_RST_MISC_CTRL*`, then defines FLR, D3hot-to-D0, power, instance-reset, and PF D-state interrupt status/mask registers. It also defines per-function FLR and D3hot-to-D0 reset controls for DEV0 PF0-PF7, DEV1 PF0-PF1, and the beginning of DEV2 PF0-PF2. Important fields include core/endpoint/downstream-port reset and sticky-reset controls, soft reset selectors, graphics/driver/VPU reset bits, miscellaneous reset policy, FLR interrupt status/masks, D3hot-to-D0 and power interrupt status/masks, D-state target/acknowledge/need-reset fields, PF/VF configuration and private reset enables, sticky reset enables, soft-PF and VF-VF reset domains, FLR twice-enable, FLR grace mode and timeout, DMA/host dummy response status selections, and soft PF PFCOPY private enablement where present.

## Control Flow

There is no local runtime control flow. Runtime use is external and follows the generated-register pattern:

1. AMDGPU code selects a register address from `nbio_7_11_0_offset.h`.
2. It reads or prepares a 16-bit or 32-bit register value through the appropriate NBIO/SOC15/PCIe config access helper.
3. It applies this header's `*_MASK` and `*__SHIFT` constants to extract a field or compose a new value while preserving unrelated bits.
4. The resulting value drives hardware behavior such as PCIe link management, interrupt routing, AER/DPA/ACS/PASID/ARI capability programming, RCC endpoint/downstream policy, or reset/FLR handling.

Several hardware flows are only implied by the field names: PCIe link training and retraining, equalization, MSI/MSI-X delivery, AER logging and clearing, DPA substate negotiation, LTR/PME signaling, hidden config-register decode, strap sampling, function-level reset, D3hot-to-D0 reset, power-state interrupt reporting, and reset-domain sticky behavior.

## State And Persistence Behavior

The header stores no state and persists nothing. It describes hardware-visible state in NBIO PCIe configuration, RCC control, strap, and reset registers. Persistence depends on the hardware reset domain, strap sampling, firmware/BIOS setup, PCIe reset, FLR, D3hot-to-D0 transitions, suspend/resume restore, power gating, and explicit AMDGPU writes.

Fields in this chunk include a mix of read-only capability bits, writable policy bits, latched status bits, interrupt status/mask bits, diagnostic log fields, and reset-control selectors. Status and log fields such as link status, AER status, MSI pending bits, interrupt status, D-state acknowledgements, and reset status may be live, latched, or write-one-to-clear depending on the hardware specification; this generated header does not encode those access semantics.

Strap registers should be treated as hardware-initialized configuration state. Reset-control fields can intentionally preserve or clear configuration/private/sticky domains across FLR or D3hot-to-D0 events. Code that writes them must understand which domain is being reset and whether firmware or another function owns the state.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.11.0 register database. The shift/mask header must stay synchronized with `nbio_7_11_0_offset.h`; representative matching offsets are present for the endpoint config block, RCC control blocks, and BIF reset block. Unlike several other NBIO generations in this tree, a local `nbio_7_11_0_default.h` is absent, so reset defaults are not available from a sibling generated file here.

The direct AMDGPU integration point is `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c`, which includes this file with the matching offset header. Semantically, the fields integrate with PCI/PCIe standard capabilities, MSI/MSI-X, AER, ACS, PASID, ARI, BAR sizing, power budgeting, DPA, SATA/VSEC vendor capability layout, endpoint/downstream RCC policy registers, and AMDGPU reset/FLR/D-state handling.

Consumers must rely on AMDGPU register helpers and PCIe/NBIO access paths for width, endianness, register-space selection, locking, ordering, polling, and side-effect handling. The macros alone do not protect reserved bits or enforce legal sequencing.

## Risks And Edge Cases

- The range starts and ends mid-family. Adjacent chunk research is required to reconstruct the complete `BIF_CFG_DEV2_EPF6_0_LINK_CAP` and `DEV2_PF2_FLR_RST_CTRL` definitions.
- Generated mask drift can compile cleanly but decode or program the wrong hardware bit, especially in repetitive DEV/PF and endpoint/downstream blocks.
- PCIe control fields for retraining, ASPM, target speed, AtomicOp, ARI, LTR, OBFF, PASID, ACS, MSI/MSI-X, AER, DPA, and BAR sizing can affect link stability, isolation, interrupt routing, error containment, power behavior, and address translation.
- Status and error-log fields may be write-one-to-clear or otherwise side-effectful. A read-modify-write using only masks from this header can be unsafe without the hardware access rules.
- Reset-control fields are high blast-radius. Incorrect PF/VF, soft-PF, sticky, FLR grace, or dummy-response programming can leave functions wedged, expose stale state after FLR, or reset domains still in use.
- RCC hidden-register decode and UR/LTR suppression fields can alter how internal config spaces respond to software and firmware. They should not be changed outside version-specific NBIO code.
- Strap fields should not be treated like ordinary writable runtime configuration without confirming access permissions and sampling behavior.
- Masks use untyped preprocessor integer literals, often with `L` suffixes and some full-width fields. Callers should keep the established AMDGPU register-helper types to avoid signedness, truncation, or width mistakes.

## Test Signals

- Build AMDGPU paths with NBIO 7.11 support enabled, especially `drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c`, to catch missing or renamed generated symbols.
- Run generated-header consistency checks: every field should have a matching shift and mask, masks should align with shifts, repeated DEV0/DEV1/DEV2 and PF blocks should match expected per-function differences, and reserved fields should not overlap defined fields.
- Cross-check register names in this chunk against `nbio_7_11_0_offset.h` so every shift/mask register maps to an address and base index.
- On NBIO 7.11 hardware, compare decoded endpoint PCIe config state against `lspci -vvxxx` or AMDGPU debug register dumps: link speed/width, MSI/MSI-X, AER masks/status, ACS/PASID/ARI, DPA, BAR capability, power-budget data, and vendor-specific capability headers should decode correctly.
- Exercise reset paths that use DEV/PF FLR and D3hot-to-D0 controls. Validate function recovery, interrupt status/mask behavior, D-state target/acknowledge fields, sticky reset preservation, and dummy-response behavior across FLR, hot reset, suspend/resume, and GPU reset.
- Validate RCC endpoint/downstream behavior with register traces around hidden config decode, LTR/PME handling, completion-timeout suppression, error interrupt enable/status, requester ID programming, and LC speed/link-control fields.
- For error handling, inject or observe AER/correctable/uncorrectable events where possible and verify the driver reports, masks, logs, and clears exactly the intended fields without disturbing unrelated status bits.
