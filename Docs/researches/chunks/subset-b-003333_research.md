# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 15101-17790

## Scope

This chunk covers lines 15101-17790 of AMDGPU's generated NBIO 7.9.0 shift/mask header. It contains C preprocessor constants only: no functions, structs, enums, variables, locking, allocation, persistence code, or direct register accesses.

The range starts in the middle of the PCIe MSI-X vector table definitions at `PCIEMSIX_VECT162_ADDR_HI`/`MSG_DATA`/`CONTROL`, continues through vectors 163-255, covers MSI-X pending-bit array registers 0-7 and a small software-index/data window, then moves into NBIF RCC strap fields, BIF reset and reset-interrupt controls, and the beginning of BIF miscellaneous registers. The final section covers ROM/strap BIOS control, doorbell range entries 0-20, and VF base-address mapping registers through `AID0_XCC1_VF5_BASE_ADDR`.

Although this repository path sits under a `ceph-client` source tree mirror, the content is AMD GPU NBIO/PCIe register metadata. It has no Ceph or distributed-filesystem runtime behavior.

## Purpose

`nbio_7_9_0_sh_mask.h` is the bitfield-definition companion to the NBIO 7.9.0 register map. Each macro provides one of two pieces of hardware field geometry:

- `REGISTER__FIELD__SHIFT`: the least-significant bit index of the field.
- `REGISTER__FIELD_MASK`: the field mask in the containing register.

The definitions let AMDGPU code use symbolic NBIO, NBIF, PCIe, reset, strap, MSI-X, doorbell, and virtualization field names instead of hard-coded bit positions while reading, decoding, or updating ASIC registers through generated offsets and driver register helpers. This chunk is focused on the tail of the MSI-X table, strap-programmed PCIe capability/personality controls, reset behavior, reset-related interrupt reporting, doorbell aperture programming, and multi-AID/multi-XCC VF base address mapping.

## Important Definitions

The MSI-X section covers the upper vector-table entries:

- `PCIEMSIX_VECT162_*` through `PCIEMSIX_VECT255_*` define the per-vector message address, message data, and mask bit fields. Each vector uses `ADDR_LO.MSG_ADDR_LO` with shift 2 and mask `0xFFFFFFFC`, `ADDR_HI.MSG_ADDR_HI` and `MSG_DATA.MSG_DATA` as full 32-bit fields, and `CONTROL.MASK_BIT` as bit 0.
- `PCIEMSIX_PBA_0` through `PCIEMSIX_PBA_7` define full 32-bit pending-bit-array words for MSI-X pending state.

The `aid_nbio_nbif0_bif_swus_SUMDEC` block provides a simple software access window:

- `SUM_INDEX` and `SUM_DATA` expose full 32-bit index/data fields.
- `SUM_INDEX_HI` supplies the upper 8 bits of the index path. Together these fields support indirect access to an indexed NBIF/SWUS register space.

The `aid_nbio_nbif0_rcc_strap_rcc_strap_internal` block is the densest part of the chunk. It describes strap-derived PCIe/root-complex configuration fields:

- `RCC_STRAP1_RCC_DEV0_PORT_STRAP0` through `_STRAP14` cover downstream/root-port identity and capability straps: device and subsystem IDs, ARI, ACS, AER, MSI, VC, DSN, ECRC, E2E prefix, LTR, OBFF, atomic operations, two-VC support, ACS subfeatures, retimer presence, 10-bit tags, Gen2/Gen3/Gen4/Gen5 compliance and target speed, lane equalization presets for 16 GT/s and 32 GT/s, power budget data, interrupt pin, PM support, link latencies, DPC enablement, PASID/ATS page request handling, and capability pointer locations.
- `RCC_DEV1_PORT_STRAP*` and `RCC_DEV2_PORT_STRAP*` are present only as comment anchors in this chunk, with no shift/mask macros following them in this range.
- `RCC_STRAP1_RCC_BIF_STRAP0` through `_STRAP6` describe BIF-wide behavior such as bus/device/function numbering, extended config and alternate routing behavior, doorbell/VF aperture sizing, SR-IOV/VF mapping, ATS/PRI/PASID and page-request related capabilities, MSI-X/MSI behavior, power management, FLR, IOV, GPU IOV VSEC sizing/revision, BAR behavior, and timer/reset-related values.
- `RCC_STRAP1_RCC_DEV0_EPF0_STRAP*` and `RCC_STRAP1_RCC_DEV0_EPF1_STRAP*` describe endpoint function 0 and function 1 PCIe personality: function enablement, IDs, revision/class code, legacy device type, D-state support, AER/ACS/DPA/VC/PASID capability exposure, MSI/MSI-X controls, power management and PME support, interrupt pin, FLR support, resize BAR, BAR aperture sizes, doorbell BAR disable, ROM/I/O/VGA disable, VF aperture sizes, SR-IOV total VFs and VF mapping, ATS invalidate queue depth, reset timing, D3hot-to-D0 timing, VF reset/FLR timing, and GPU IOV VSEC length.

The `aid_nbio_nbif0_bif_rst_bif_rst_regblk` block defines reset and reset-notification control:

- `HARD_RST_CTRL`, `SELF_SOFT_RST`, and `SELF_SOFT_RST_2` select reset domains such as DSPT config/private paths, endpoint config/private paths, sticky reset paths, SDP ports, strap reset/reload, and core reset.
- `BIF_GFX_DRV_VPU_RST` describes driver-mode reset bits for PF/VF config and private reset domains.
- `BIF_RST_MISC_CTRL`, `_CTRL2`, and `_CTRL3` define reset policy knobs: driver reset mode, auto-clear behavior, FLR auto-clear, link reset protection and transaction-idle state, link reset grace timing, PME turnoff timeout/mode, strap reload delays, SR-IOV save-on-VF-enable-clear behavior, and dummy response behavior during reset.
- `DEV0_PF0_FLR_RST_CTRL` and `DEV0_PF1_FLR_RST_CTRL` define PF/VF reset routing for function-level reset, soft PF reset, sticky reset domains, grace modes/timeouts, dummy response status, and PF copy/private reset behavior.
- `DEV0_PF0_D3HOTD0_RST_CTRL` and `DEV0_PF1_D3HOTD0_RST_CTRL` define reset behavior tied to D3hot-to-D0 transitions.
- `BIF_INST_RESET_INTR_STS`, `BIF_PF_FLR_INTR_STS`, `BIF_D3HOTD0_INTR_STS`, `BIF_POWER_INTR_STS`, and `BIF_PF_DSTATE_INTR_STS` expose reset, FLR, D3hot-to-D0, PME turnoff, port D-state, and PF D-state interrupt status.
- The matching `*_INTR_MASK` registers expose masks for those interrupt sources.
- `BIF_PF_FLR_RST`, `BIF_DEV0_PF0_DSTATE_VALUE`, `BIF_DEV0_PF1_DSTATE_VALUE`, and `BIF_PORT0_DSTATE_VALUE` define explicit FLR reset trigger bits and target/ack D-state value fields.

The `aid_nbio_nbif0_bif_misc_bif_misc_regblk` portion begins miscellaneous NBIF programming:

- `REGS_ROM_OFFSET_CTRL.ROM_OFFSET` selects a 7-bit ROM register offset.
- `NBIF_STRAP_BIOS_CNTL` gates BIOS-driven strap override behavior, including PCIe ID strap override.
- `DOORBELL0_CTRL_ENTRY_0` through `_20` define doorbell range offset, range size, and fence-enable fields for 21 doorbell apertures.
- `AID*_VF*_BASE_ADDR`, `AID*_XCC*_VF*_BASE_ADDR`, and `AID0_{NBIF,ATHUB,IH,HDP}_VF*_BASE_ADDR` define 16-bit base-address fields for VF0 through part of VF5 across AID, XCC, NBIF, ATHUB, IH, and HDP mapping domains. `AID0_XCC0_VF*` entries in this range use a 17-bit mask (`0x0001FFFF`), while most adjacent base fields use 16-bit masks.

## APIs, Types, And Functions

There are no callable APIs, C types, or functions in this range. The exported interface is the generated macro namespace. Consumers combine these masks and shifts with matching NBIO 7.9.0 register offset/default headers and AMDGPU register-access helpers for MMIO, SMN, PCI configuration, indirect indexed access, or generated field composition/extraction.

The macros encode only field positions. They do not encode reset values, access permissions, firmware ownership, volatility, W1C behavior, reserved-bit policy, ordering requirements, or side effects.

## Control Flow

This header has no local runtime control flow. Runtime use is external and generally follows this pattern:

1. Driver or firmware-facing AMDGPU code selects the appropriate NBIO 7.9.0 register offset for the MSI-X, SUMDEC, strap, reset, doorbell, or VF-base register.
2. It reads a register and extracts fields using the matching `__SHIFT`/`_MASK`, or builds a write value by shifting and masking the desired field.
3. For writable control registers, code usually performs a read-modify-write that preserves unrelated and reserved bits.
4. Hardware applies the actual semantics: interrupt vector delivery and masking, pending-bit reporting, indirect register access, strap-controlled PCIe capability exposure, reset sequencing, interrupt status/masking, D-state acknowledgement, doorbell aperture routing, and VF address decode.

The order in the file follows the generated register database, not an execution order. Repeated field names across status, mask, reset-trigger, and reset-control registers can have different operational semantics even when the bit positions look similar.

## State And Persistence Behavior

The chunk owns no software state and persists nothing. It names hardware state that lives in NBIO/NBIF registers, PCIe configuration decode/shadow registers, strap latches, MSI-X table/PBA state, doorbell routing registers, reset-control registers, and virtualization address decode registers.

Represented hardware state includes:

- Interrupt state: per-vector MSI-X address/data/mask fields, PBA pending bits, reset interrupt status, FLR/D3hot/D-state/PME status, and interrupt masks.
- Strap-derived configuration: identity/class/revision fields, capability enables, link speed and lane equalization capability, BAR/ROM/doorbell/VF aperture sizing, SR-IOV and GPU IOV configuration, ACS/AER/ATS/PRI/PASID exposure, MSI/MSI-X behavior, power-management support, and reset timing defaults.
- Reset state and policy: hard reset enables, self soft reset bits, sticky reset domains, strap reload controls, link reset protection, FLR and D3hot-to-D0 reset routing, auto-clear behavior, grace timers, and reset transaction-idle/dummy-response state.
- Address decode and routing state: doorbell range offsets/sizes/fence enables and VF base addresses across AID/XCC/NBIF/ATHUB/IH/HDP domains.

Persistence is determined by hardware reset domains, strap reload behavior, PCIe function-level reset, D3hot-to-D0 transitions, GPU mode resets, suspend/resume restore, BIOS/firmware initialization, SR-IOV enablement, and explicit driver writes. Strap fields may be sampled from fuses, pins, firmware tables, or BIOS override paths; the shift/mask header does not distinguish immutable sampled straps from writable override registers.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 7.9.0 register-header set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_offset.h` supplies the matching register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_default.h` supplies reset/default values where generated.
- AMDGPU NBIO, PCIe, reset, interrupt, SR-IOV, GPU IOV, doorbell, and VM/HDP/IH/ATHUB code includes the generated NBIO headers and uses the common shift/mask convention through register helper macros.

Practical integration points are GPU platform behavior rather than filesystem behavior: MSI-X setup and masking, interrupt pending diagnostics, PCIe enumeration and capability exposure, root-complex and endpoint personality straps, link training/equalization, AER/ACS policy, ATS/PRI/PASID capability reporting, SR-IOV VF mapping, GPU IOV VSEC reporting, FLR and mode reset handling, D3hot-to-D0 recovery, runtime power management, suspend/resume, doorbell aperture assignment, queue/doorbell fencing, and multi-die/multi-XCC VF address routing.

## Risks And Edge Cases

- The range starts mid-vector-table and ends mid-VF-base-address family. Adjacent chunks must be reconciled before drawing whole-table or whole-family conclusions.
- A wrong MSI-X address/data/mask bitfield can compile cleanly but break interrupt delivery, leave a vector masked, or direct messages to the wrong APIC/interrupt remapping address.
- MSI-X PBA bits are status-like. Treating pending bits as ordinary writable data can lose diagnostics or interact badly with interrupt masking/unmasking.
- Strap fields are capability-defining. Incorrect masks can misadvertise PCIe capabilities such as ACS, AER, ATS, PASID, SR-IOV, DPA, VC, MSI-X, Gen5, or 10-bit tags, which can affect enumeration, IOMMU grouping, passthrough policy, and OS feature enablement.
- Reset fields are operationally sensitive. Misprogramming hard reset, self reset, FLR, sticky reset, strap reload, or D3hot-to-D0 reset controls can hang the GPU, drop PCIe config state, fail to reset VFs, or reset more domains than intended.
- Status and mask register pairs have similar names. Code that accidentally writes a status mask to a status register or vice versa can suppress interrupts or fail to clear/observe reset events.
- D-state target and acknowledgement fields are state-machine interfaces. Polling the wrong field or failing to preserve unrelated bits can make power transitions appear stuck.
- Doorbell range and fence fields affect queue submission routing and ordering. Bad range sizes or offsets can cause queues to ring the wrong engine, expose another function's doorbells, or bypass required fencing.
- VF base-address fields are repeated across AIDs, XCCs, and client blocks. Prefix mix-ups may not be caught at compile time and can route a VF to the wrong die, compute complex, NBIF, ATHUB, IH, or HDP aperture.
- `AID0_XCC0_VF*` fields use a wider 17-bit mask than many neighboring 16-bit base fields. Generic assumptions about base-address field width can truncate values or fail consistency checks.
- BIOS strap override controls can change identity/capability reporting before the OS driver observes the device. Debugging must account for firmware-programmed state, not just static generated defaults.

## Test Signals

- Build AMDGPU configurations that include NBIO 7.9.0 support. Compile failures catch malformed generated symbols or mismatches between generated offset/default headers and shift/mask users.
- Run generated-header consistency checks against the authoritative NBIO 7.9.0 register database: every field should have the expected shift/mask, every register should have a matching offset, and defaults should match where present.
- Validate MSI-X programming on matching hardware: vectors 162-255 should accept message address/data programming, mask/unmask correctly, and report pending status coherently through PBA words.
- Exercise PCIe enumeration and capability decode with `lspci -vv` or equivalent debug output: IDs, class codes, MSI/MSI-X, AER, ACS, ATS, PASID, PRI, SR-IOV, power management, link speed, lane equalization, and vendor-specific GPU IOV capability data should match strap policy.
- Exercise FLR, GPU mode reset, link reset, D3hot-to-D0 transition, runtime suspend/resume, and full device reset paths while checking reset interrupt status/masks, D-state target/ack fields, strap reload behavior, and that unrelated functions/VFs survive when policy says they should.
- Validate SR-IOV enable/disable and VF reset paths: VF counts, VF base mapping, VF doorbell/register/memory aperture sizes, PASID/ATS behavior, and PF/VF reset isolation should match the represented fields.
- Validate doorbell routing under queue creation and teardown: doorbell offsets, aperture sizes, fence-enable fields, and per-function isolation should remain consistent across reset and power transitions.
- Cross-check multi-AID/multi-XCC VF base-address programming on hardware with multiple AIDs or XCCs, especially the wider `AID0_XCC0_VF*` masks.
- Use debugfs/register dumps or firmware diagnostics to compare strap, reset, and doorbell register values before and after BIOS override, driver init, SR-IOV enablement, FLR, suspend/resume, and GPU reset.
