# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 97018-99440

## Scope

This chunk is part of AMDGPU's generated NBIO 7.7.0 register field header. It contains C preprocessor constants only: every register field has a `__SHIFT` value and a matching `_MASK` value. There are no functions, structs, inline helpers, storage objects, or executable control flow in this slice.

The slice starts immediately after the `BIFPLR4_1_MSI_CAP_LIST` field definitions and covers most of the `BIFPLR4_1` PCIe capability/register field map, then crosses into the beginning of the `BIFPLR5_0` PCIe bridge configuration block. The requested line range ends at `BIFPLR5_0_SLOT_CAP__PHYSICAL_SLOT_NUM_MASK`; the subsequent `BIFPLR5_0_SLOT_CNTL` field definitions begin on the next line and are outside this chunk.

## Purpose

The purpose of this chunk is to provide bit layout constants for NBIO PCIe root-port/bridge configuration registers on ASICs using the NBIO 7.7.0 register map. These constants are paired with address constants from `nbio_7_7_0_offset.h` and consumed by AMDGPU register access macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`.

The chunk describes fields for:

- MSI capability programming for `BIFPLR4_1`, including enable state, multi-message capability/enables, 64-bit MSI support, per-vector masking capability, extended message data, message address low/high, and message data fields.
- Subsystem ID and AMD MSI mapping capability registers.
- Vendor-specific and virtual-channel enhanced capabilities.
- PCIe advanced error reporting (AER): uncorrectable/correctable error status, masks, severity, ECRC controls, header logs, root error command/status, error source ID, and TLP prefix logs.
- PCIe secondary enhanced capability and lane equalization controls for lanes 0-15.
- Access Control Services (ACS), multicast (MC), L1 PM substates, Downstream Port Containment (DPC), Root Port PIO error reporting, ESM/data-link feature/PHY-speed capabilities, lane margining, CCIX/ESM transport controls, and 32 GT/s link capability/control/status fields.
- The start of the next address block, `nbio_pcie1_bifplr5_cfgdecp`, through `BIFPLR5_0_SLOT_CAP`.

## Important APIs, Types, and Constants

This chunk exports preprocessor constants named in the pattern:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

Examples from the chunk include:

- `BIFPLR4_1_MSI_MSG_CNTL__MSI_EN__SHIFT` and `BIFPLR4_1_MSI_MSG_CNTL__MSI_EN_MASK`.
- `BIFPLR4_1_PCIE_UNCORR_ERR_STATUS__CPL_TIMEOUT_STATUS_MASK`, `...__ACS_VIOLATION_STATUS_MASK`, and other AER status bits.
- `BIFPLR4_1_PCIE_DPC_STATUS__DPC_TRIGGER_REASON_MASK` and `...__RP_PIO_FIRST_ERROR_POINTER_MASK`.
- Per-lane equalization/margining masks such as `BIFPLR4_1_PCIE_LANE_0_EQUALIZATION_CNTL__DOWNSTREAM_PORT_RX_PRESET_HINT_MASK` and `BIFPLR4_1_LANE_15_MARGINING_LANE_STATUS__MARGINING_READY_MASK`.
- `BIFPLR4_1_LINK_CAP_32GT__LINK_SPEED_VECTOR_32GT_MASK`, `BIFPLR4_1_LINK_CNTL_32GT__NO_EQUALIZATION_NEEDED_DISABLE_MASK`, and `BIFPLR4_1_LINK_STATUS_32GT__EQUALIZATION_COMPLETE_32GT_MASK`.
- `BIFPLR5_0_DEVICE_CNTL__MAX_PAYLOAD_SIZE_MASK`, `BIFPLR5_0_LINK_STATUS__DL_ACTIVE_MASK`, and `BIFPLR5_0_SLOT_CAP__PHYSICAL_SLOT_NUM_MASK`.

There are no declared C types. The "API" surface is the macro namespace. Driver code includes this header from `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, along with `nbio_7_7_0_offset.h`, so the field constants can be used against the matching register addresses.

## Control Flow

The chunk has no runtime control flow. Its behavior is compile-time substitution into call sites. Runtime behavior emerges when code combines:

- A register address, for example `regBIFPLR4_1_PCIE_DPC_STATUS` from `nbio_7_7_0_offset.h`.
- A field name and its shift/mask from this header.
- A register accessor or field helper such as `REG_SET_FIELD`/`REG_GET_FIELD`.

The surrounding NBIO implementation in `amdgpu/nbio_v7_7.c` follows this model for other registers: it reads a register, updates fields using generated mask/shift constants, and writes the value back. This chunk supplies the same style of field metadata for PCIe config/capability registers, even though the sampled `nbio_v7_7.c` code does not directly reference the specific `BIFPLR4_1`/`BIFPLR5_0` names in this slice.

## State and Persistence Behavior

The header stores no software state. The fields described here map onto persistent hardware register state while the GPU/NBIO block is powered and configured. Some registers are control registers whose bits can alter hardware behavior until reset or reprogramming, such as MSI enable bits, AER masks/severity controls, VC resource enables, ACS controls, L1 PM substate controls, DPC controls, CCIX transport controls, and link equalization controls.

Other registers are status/log surfaces that expose hardware-observed state, such as AER status bits, header/TLP prefix logs, DPC status, Root Port PIO logs, ESM status, link status, lane margining status, and `BIFPLR5_0_*_STATUS` fields. Status fields may be clear-on-write, write-1-to-clear, sticky until reset, or hardware-updated depending on the PCIe/NBIO register definition; this header only supplies masks and shifts and does not encode access semantics.

## Dependencies

Primary dependencies and companions:

- `nbio_7_7_0_offset.h` provides the register addresses and base indices corresponding to these field layouts. In the same address range it maps `BIFPLR4_1` registers under base index 5, then starts `BIFPLR5_0` under the `nbio_pcie1_bifplr5_cfgdecp` address block.
- AMDGPU register helpers/macros use this generated naming convention. The helpers expect masks and shifts to match the register name passed as the field namespace.
- PCIe architectural definitions are the hardware contract behind many field names: MSI, PCIe capability lists, AER, VC, ACS, MC, L1 PM substates, DPC, lane equalization, link speeds, and slot capabilities.
- The header is included by `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which is the NBIO 7.7 implementation layer.

This chunk also mirrors concepts present in older/generated sibling headers such as `nbio_7_0_sh_mask.h` and `nbio_7_2_0_sh_mask.h`. That duplication indicates ASIC-version-specific generated register maps rather than hand-authored logic.

## Integration Points

The chunk integrates with AMDGPU at the hardware abstraction boundary:

- NBIO initialization and runtime paths can use the constants to program PCIe/NBIO registers for link behavior, error reporting, power management, and interrupt/MSI behavior.
- Diagnostics or recovery paths can use AER, DPC, Root Port PIO, and link/lane status masks to decode fault state.
- PCIe capability or platform configuration code can use the `BIFPLR5_0` bridge capability fields to inspect or update device/link/slot capability and control registers.
- Offset definitions in `nbio_7_7_0_offset.h` show several packed 16-bit PCI config registers sharing the same 32-bit dword address, for example MSI high/data and VC/DPC status/control pairs. Correct masks are therefore essential to avoid corrupting adjacent fields.

## Risks

- A wrong shift or mask silently targets the wrong hardware bits. That can break PCIe link training, MSI delivery, AER/DPC recovery behavior, ACS isolation, power management, or lane equalization.
- The chunk crosses an address-block boundary from `BIFPLR4_1` to `BIFPLR5_0`. Generated-file edits or manual slicing errors can easily mix fields from different PCIe logical ports.
- Several fields share register dwords or halfwords. Read-modify-write users must preserve unrelated bits, especially around MSI message data/address aliases, VC status/control registers, ACS capability/control, MC capability/control, DPC control/status/source ID, and lane controls packed by lane pairs or lane groups.
- Status/log registers may have write-sensitive clear behavior. A field mask being available does not imply that writing an arbitrary masked value is safe.
- Feature bits for advanced PCIe capabilities such as DPC, ACS, L1 PM substates, CCIX/ESM, 16/20/25/32 GT/s equalization, and margining should be used only when the corresponding capability exists and the ASIC/register map matches NBIO 7.7.0.
- Because this is generated hardware metadata, hand edits are high risk. The safer source of truth is the hardware register database/specification used to generate the header.

## Test Signals

Useful verification signals for this chunk are mostly compile-time and hardware/driver runtime oriented:

- AMDGPU builds including `nbio_v7_7.c` should compile without undefined register-field macros or macro redefinition warnings.
- Static checks should confirm every `<REGISTER>__<FIELD>_MASK` has the expected companion `<REGISTER>__<FIELD>__SHIFT`, and that masks align with shifts without crossing the documented register width.
- Cross-check generated masks against `nbio_7_7_0_offset.h` for packed registers and address-block boundaries, especially the `BIFPLR4_1` to `BIFPLR5_0` transition.
- Runtime smoke tests on NBIO 7.7.0 hardware should cover GPU probe, PCIe link training, interrupt/MSI delivery, suspend/resume or power-state transitions, and error recovery paths.
- Fault-injection or platform tests that trigger AER/DPC/PIO reporting should decode expected status bits and should not report spurious adjacent-field changes after clear or mask operations.
