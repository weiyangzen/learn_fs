# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 119034-121457

## Scope And Purpose

This chunk is part of AMDGPU's generated NBIO 7.2.0 register shift/mask header. It contains C preprocessor constants only: each hardware register field is represented by a `__SHIFT` constant and a `_MASK` constant. These definitions are consumed together with `nbio_7_2_0_offset.h`, which supplies the corresponding `reg...` addresses and `BASE_IDX` values, and with driver helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`.

The line range covers 2,424 source lines with 1,082 shift definitions, 1,120 mask definitions, and 258 register-comment markers. It closes the `BIFPLR3_1` PCIe CCIX/ESM area, then starts `addressBlock: nbio_pcie0_bifplr4_cfgdecp`. The `BIFPLR4_1` block is a PCIe configuration/decode register view for a second BIF PLR instance and covers conventional PCI config header fields, bridge controls, PCIe capability structures, error reporting, link/equalization controls, power management, DPC/RP PIO, ESM, data link feature, 16 GT PHY, and lane margining controls.

## Important Macro Groups

The opening `BIFPLR3_1` tail defines per-lane ESM equalization presets:

- `BIFPLR3_1_ESM_LANE_2_EQUALIZATION_CNTL_20GT` through `BIFPLR3_1_ESM_LANE_15_EQUALIZATION_CNTL_20GT`.
- `BIFPLR3_1_ESM_LANE_0_EQUALIZATION_CNTL_25GT` through `BIFPLR3_1_ESM_LANE_15_EQUALIZATION_CNTL_25GT`.
- Each lane register exposes downstream and upstream TX preset nibbles: `DSP_*_TX_PRESET` at shift `0x0` with mask `0x0f`, and `USP_*_TX_PRESET` at shift `0x4` with mask `0xf0`.
- `BIFPLR3_1_PCIE_CCIX_TRANS_CAP` and `BIFPLR3_1_PCIE_CCIX_TRANS_CNTL` expose CCIX optimized TLP format support and enable bits.

The `BIFPLR4_1` address block begins at line 119194. Its conventional PCI and bridge header macros include `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, class/revision bytes, cache/latency/header/BIST, secondary bus numbering, I/O and memory base/limit fields, prefetchable windows, capability pointer, ROM base, interrupt line/pin, `IRQ_BRIDGE_CNTL`, and `EXT_BRIDGE_CNTL`. These bitfields are the masks a driver would use when reading or modifying the emulated/configuration-facing PCI bridge register image.

The PCI power-management and PCIe base capability sections define:

- Vendor and PMI capability list/header fields: `VENDOR_CAP_LIST`, `ADAPTER_ID_W`, `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`.
- PCIe capability identity and device/link/slot/root fields: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `SLOT_CAP`, `SLOT_CNTL`, `SLOT_STATUS`, `ROOT_CNTL`, `ROOT_CAP`, and `ROOT_STATUS`.
- PCIe capability 2 structures: `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, and empty or minimal slot capability 2/status fields.
- MSI, SSID, and MSI map capability fields: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, MSI message address/data registers, `SSID_CAP_LIST`, `SSID_CAP`, `MSI_MAP_CAP_LIST`, and `MSI_MAP_CAP`.

The enhanced capability sections define vendor-specific, virtual-channel, device-serial-number, AER, secondary PCIe, ACS, multicast, L1 PM substate, DPC, root-port PIO, ESM, data-link-feature, 16 GT PHY, and margining fields. Important groups include:

- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, `PCIE_UNCORR_ERR_SEVERITY`, `PCIE_CORR_ERR_STATUS`, `PCIE_CORR_ERR_MASK`, `PCIE_ADV_ERR_CAP_CNTL`, header logs, root error command/status, error source ID, and TLP prefix logs.
- `PCIE_SECONDARY_ENH_CAP_LIST`, `PCIE_LINK_CNTL3`, `PCIE_LANE_ERROR_STATUS`, and `PCIE_LANE_0_EQUALIZATION_CNTL` through `PCIE_LANE_15_EQUALIZATION_CNTL`.
- `PCIE_ACS_CAP` and `PCIE_ACS_CNTL` for access-control-services capabilities and enables.
- `PCIE_MC_*` registers for multicast capability/control/address/receive/block/overlay BAR fields.
- `PCIE_L1_PM_SUB_*` for L1 substate capability and control timing/enable fields.
- `PCIE_DPC_*` and `PCIE_RP_PIO_*` for downstream port containment and root-port PIO error status/mask/severity/system-error/exception handling, plus header and prefix logs.
- `PCIE_ESM_CAP_LIST`, `PCIE_ESM_HEADER_1`, `PCIE_ESM_HEADER_2`, `PCIE_ESM_STATUS`, `PCIE_ESM_CTRL`, and `PCIE_ESM_CAP_1` through `PCIE_ESM_CAP_7`; these advertise many discrete ESM data-rate support bits, starting at 8.0G in cap 1 and continuing through higher 0.1G-spaced rates across the subsequent cap registers.
- `DATA_LINK_FEATURE_CAP`, `DATA_LINK_FEATURE_STATUS`, `PCIE_PHY_16GT_ENH_CAP_LIST`, `LINK_CAP_16GT`, `LINK_CNTL_16GT`, `LINK_STATUS_16GT`, local/retimer parity mismatch status registers, and per-lane 16 GT equalization controls.
- `PCIE_MARGINING_ENH_CAP_LIST`, `MARGINING_PORT_CAP`, `MARGINING_PORT_STATUS`, and per-lane `LANE_N_MARGINING_LANE_CNTL` / `LANE_N_MARGINING_LANE_STATUS` fields. This chunk includes complete margining control/status pairs for lanes 0 through 12 and begins lane 13 control before the chunk boundary.

## APIs, Types, And Functions

There are no C functions, structs, enums, or storage objects in this chunk. The public interface is the macro namespace itself:

- Field extraction contract: `(value & REGISTER__FIELD_MASK) >> REGISTER__FIELD__SHIFT`.
- Field update contract through AMDGPU helpers: `REG_SET_FIELD(value, REGISTER, FIELD, field_value)` and `REG_GET_FIELD(value, REGISTER, FIELD)` rely on the macro names generated here.
- Address pairing contract: a field macro such as `BIFPLR4_1_LINK_CNTL__RETRAIN_LINK_MASK` must be used with the matching register address macro from `nbio_7_2_0_offset.h`, such as `regBIFPLR4_1_LINK_CNTL`, not with another generation or PLR instance.

The nearby driver integration file `amdgpu/nbio_v7_2.c` includes both `nbio_7_2_0_offset.h` and this `_sh_mask.h` header. That file demonstrates the intended use style: read a register value, set or get named fields using `REG_SET_FIELD` or explicit mask/shift operations, and write the value back through SOC15 or PCIE-port register accessors.

## Control Flow

This header contributes no runtime control flow by itself. Runtime behavior is created only when driver code expands these macros into bit operations while reading or writing hardware registers. The control sequence for a typical user is:

1. Select an NBIO/PCIe register address from `nbio_7_2_0_offset.h`.
2. Read the register through an AMDGPU register accessor or prepare a new value.
3. Use this header's mask and shift macros to isolate, test, clear, or set individual fields.
4. Write the modified value back if the register is writable and the operation is appropriate for the PCIe state machine.

For status and logging registers, the macros support branch decisions in higher-level code: link status bits, AER/DPC/RP PIO status bits, lane-error bits, ESM current-rate/calibration bits, data-link feature status, and lane margining status can all drive diagnostics or recovery logic. For control registers, the macros support writes that may retrain links, enable/disable capabilities, configure L1 substates, control DPC behavior, or issue lane margining commands.

## State And Persistence Behavior

The macros themselves are compile-time constants and persist only in compiled driver code. The state they describe is hardware state in NBIO PCIe configuration and extended capability registers:

- PCI command/status and bridge window fields are hardware/configuration state visible through PCI config space semantics.
- Capability, link, slot, root, ESM, ACS, MC, L1 PM, DPC, and DLF fields reflect either advertised hardware capabilities, live link state, or driver/programmed control bits.
- Error status and log fields may be sticky until cleared according to PCIe/AER/DPC rules. Misinterpreting masks can cause the driver to miss an error, clear the wrong bit, or report a stale condition.
- Lane equalization and margining fields affect or reflect per-lane PHY training state; writes are hardware-stateful and may persist until link retraining, reset, or firmware/driver reprogramming.

Because this is a generated ASIC register header, any persistence guarantee comes from the hardware register specification, not from C storage in this file.

## Dependencies And Integration Points

Primary dependencies:

- `nbio_7_2_0_offset.h` supplies matching register addresses. For this chunk, `regBIFPLR4_1_VENDOR_ID`, `regBIFPLR4_1_PCIE_ESM_CAP_1`, and nearby `regBIFPLR4_1_*` addresses are in base index 5.
- AMDGPU register-access helpers in the driver tree provide address translation and MMIO/PCIe-port access.
- `amdgpu/nbio_v7_2.c` includes this header and is the direct NBIO 7.2 driver integration point found in this tree.
- Other generated ASIC headers for adjacent IP versions, such as NBIO 7.7.0, have similar macro layouts; generated-name consistency matters for shared driver patterns and version-specific code paths.

The chunk is specifically tied to NBIO 7.2.0 register layout. The names embed `BIFPLR3_1` and `BIFPLR4_1`, so they are instance-specific as well as IP-version-specific. Code that uses a `BIFPLR4_1_*` mask with a `BIFPLR4_0_*`, `BIFPLR5_*`, or NBIO 7.7.0 address risks silently manipulating the wrong bitfield if layouts differ.

## Risks And Edge Cases

- Generated-header drift: these constants must match the hardware database and the paired offset header. A single incorrect bit position can corrupt link configuration, error masking, or power-management behavior.
- Instance confusion: the `BIFPLR3_1` tail and `BIFPLR4_1` block are adjacent in this chunk; using the wrong PLR instance's macro with a same-named register from another instance is easy to do in manual edits.
- Shared register addresses: several capability fields in the offset header share the same dword address but use different masks. Callers must preserve unrelated bits when updating a field.
- Write-one-to-clear and sticky status semantics: AER, DPC, RP PIO, lane error, parity mismatch, and margining status fields are not ordinary RAM bits. Read-modify-write code must respect the underlying PCIe clearing semantics.
- Link training sensitivity: `LINK_CNTL`, `LINK_CNTL2`, `LINK_CNTL3`, lane equalization, ESM control, and margining controls can affect live PCIe link behavior. Incorrect writes may retrain, disable, degrade, or destabilize the link.
- Capability advertisement vs control: many `*_CAP` fields are capability bits and should not be treated as writable policy knobs.
- Boundary completeness: this chunk ends in the middle of the lane margining area after beginning `BIFPLR4_1_LANE_13_MARGINING_LANE_CNTL`; lanes 13 status and lanes 14-15 margining definitions continue in the next chunk.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware/driver integration signals:

- Build the AMDGPU driver with `nbio_v7_2.c` and this generated header included; missing or renamed macros should fail compilation.
- Static checks can verify that every `__SHIFT` has a corresponding `_MASK` for the same register field and that masks align with shifts.
- Generated-header comparison against AMD's source register database or an upstream kernel copy can catch drift in bit positions and missing lane/capability fields.
- Runtime PCIe diagnostics should preserve expected behavior for link status, retraining, AER/DPC reporting, root-port PIO logging, L1 PM substate negotiation, ESM data-rate reporting, and margining operations on NBIO 7.2 hardware.
- Hardware smoke tests should include suspend/resume and GPU reset paths because link, power, and error-status fields often change across reset and power transitions.

## Chunk Notes

This is a partial oversized-file research artifact for `subset-b-003209`. It should be merged later with neighboring chunk reports for the full `nbio_7_2_0_sh_mask.h` file-level research document.
