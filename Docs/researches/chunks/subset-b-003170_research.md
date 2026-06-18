# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 24501-26923

## Purpose

This chunk is part of the generated AMD NBIO 7.2.0 register shift/mask header used by the AMDGPU DRM driver. It does not contain executable logic; it defines preprocessor constants for extracting and composing bitfields in PCIe/NBIO configuration-space registers. The covered range spans the tail of the `BIFPLR3` PCIe/CCIX register block and the start of the `BIFPLR4` PCIe port register block under the `nbio_pcie0_bifplr4_cfgdecp` address block.

The constants are consumed by register accessor code elsewhere in the AMDGPU stack through the common `REG_SET_FIELD`, `REG_GET_FIELD`, read-modify-write, and MMIO/config-space access patterns. The field names encode the hardware register, field, bit shift, and mask so callers can avoid open-coded literals when programming PCIe capabilities, link training/equalization, error reporting, MSI, power management, and PCIe enhanced capability registers.

## Important APIs, Types, and Data

There are no C functions, structs, or runtime types in this chunk. The important API surface is the generated macro namespace:

- `BIFPLR3_LANE_<n>_MARGINING_LANE_CNTL` and `BIFPLR3_LANE_<n>_MARGINING_LANE_STATUS` for PCIe lane margining control/status fields. This chunk starts at lane 2 status and then covers lane 3 through lane 15 control/status.
- `BIFPLR3_PCIE_CCIX_*` for CCIX extended capability list/header/capability/status/control/transition fields, including required and optional ESM capability bits.
- `BIFPLR3_ESM_LANE_<n>_EQUALIZATION_CNTL_20GT` and `_25GT` for lane-by-lane equalization presets at 20 GT/s and 25 GT/s.
- `BIFPLR4_*` for a second PCIe bridge/function register block. This includes conventional PCI configuration header fields (`VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, class code, BAR/bridge window fields, interrupt and bridge control) and numerous PCIe capability structures.
- `BIFPLR4_PCIE_*` enhanced capability fields for PCIe capability, AER, secondary PCIe, ACS, multicast, L1 PM substate, DPC, ESM, DLF, and PHY 16GT capability/status/control registers.

The shift/mask convention is consistent: each field has a `__SHIFT` macro giving the least-significant bit index and a `_MASK` macro giving the already-positioned bit mask. Callers should shift values before masking only through the established register field helper macros, because manually combining these constants can easily double-shift values.

## Control Flow

This header has no control flow. Runtime control flow is imposed by driver code that includes it:

1. The driver selects a target NBIO/PCIe register address from companion address headers.
2. It reads or prepares a 32-bit register value.
3. It uses the `*_SHIFT` and `*_MASK` constants from this header to extract status fields or update control fields.
4. It writes the new value back only when the target register is writable and the hardware sequence allows it.

The repeated lane register layout is the key structural signal. Lane margining and equalization fields are replicated per lane, so higher-level link management code can iterate over lanes by choosing the matching register address and field macros for a concrete lane.

## State and Persistence Behavior

The file itself persists no state. The state represented by these masks lives in GPU/NBIO hardware registers and PCIe configuration-space capability structures. Depending on the field, state may be:

- Static or strap-derived identity/capability state, such as vendor/device ID, class code, capability IDs, and supported ESM/DLF feature bitmaps.
- Negotiated or live link state, such as link speed/width, equalization completion, lane error status, remote DLF support, CCIX/ESM status, and DPC/AER status.
- Driver-programmed control state, such as PCI command enables, MSI control/data, PCIe device/link/root/slot controls, ACS controls, L1 PM substate controls, DPC controls, and ESM/DLF exchange enable bits.
- Error-log or sticky status state, such as AER uncorrectable/correctable error status, root error status, DPC status, RP PIO status/logs, TLP prefix logs, and parity mismatch status.

Because many PCIe status and error registers use write-one-to-clear or hardware-updated semantics, consumers must follow the PCIe/NBIO register specification rather than treating every masked field as a normal read/write bitfield.

## Dependencies and Integration Points

This header depends on the generated AMD register-header ecosystem:

- Companion NBIO address/index headers provide the register offsets that pair with these shift/mask definitions.
- AMDGPU register helper macros and MMIO/config-space helpers consume the `__SHIFT` and `_MASK` naming convention.
- PCIe/NBIO management code uses these definitions during GPU initialization, PCIe link setup, power management, error handling, and debug/status collection.
- Linux PCIe concepts are reflected directly in the register groups: PCI command/status, bridge windows, MSI, PCIe capability, AER, ACS, L1 PM substates, DPC, DLF, ESM, and PHY 16GT capabilities.

The chunk crosses an important address-block boundary: it finishes `BIFPLR3` lane margining/CCIX/ESM definitions and then enters `BIFPLR4` (`nbio_pcie0_bifplr4_cfgdecp`). Consumers must not mix `BIFPLR3` masks with `BIFPLR4` register addresses even when field names are semantically similar.

## Register Groups Covered

- `BIFPLR3` lane margining:
  - Lane 2 status tail.
  - Lane 3 through lane 15 control/status pairs.
  - Common fields: receiver number, margin type, usage model, and margin payload/status.
- `BIFPLR3` CCIX and ESM:
  - CCIX capability list/header fields.
  - CCIX capability bits, required/optional ESM capability maps, ESM status/control, and transition capability/control.
  - Per-lane 20GT and 25GT downstream/upstream transmit preset controls.
- `BIFPLR4` conventional PCI/bridge config:
  - Vendor/device ID, command/status, revision/class fields, bridge bus/window fields, ROM base, interrupt line/pin, bridge control, and vendor/PMI capability list data.
- `BIFPLR4` PCIe capability:
  - Device/link/slot/root capability, control, and status registers.
  - Secondary capability set, lane error status, and lane equalization controls for lanes 0-15.
- `BIFPLR4` interrupt and identity:
  - MSI capability/control/address/data fields.
  - subsystem ID and MSI map capability fields.
- `BIFPLR4` enhanced/error capabilities:
  - Vendor-specific enhanced capability.
  - VC/VC0/VC1 resource capability/control/status.
  - Device serial number.
  - AER uncorrectable/correctable status, mask, severity, header logs, root error command/status, error source ID, and TLP prefix logs.
  - ACS capability/control.
  - Multicast capability/control/address/receive/block/overlay fields.
  - L1 PM substate capability/control.
  - DPC capability/control/status/error-source and RP PIO status/mask/severity/system-error/exception/log fields.
  - ESM capability bitmaps covering granular speeds from 2.5 GT/s through 28.0 GT/s across `PCIE_ESM_CAP_1` through `PCIE_ESM_CAP_7`.
  - DLF enhanced capability, local/remote DLF feature support, and remote-valid state.
  - PHY 16GT enhanced capability, 16GT link status/equalization status, parity mismatch status, and initial lane 0-2 16GT preset controls.

## Risks and Edge Cases

- Generated-header drift is the main risk. A wrong mask or shift compiles cleanly but can corrupt unrelated hardware bits or misreport PCIe link state.
- Similar register names exist across `BIFPLR3` and `BIFPLR4`; address/mask mismatches are easy when adding manual code.
- PCIe status and error fields often have side effects or clear-on-write behavior. Code using these masks must preserve reserved bits and use the documented clear sequence.
- Lane-replicated fields invite copy/paste errors. In this chunk, lane-specific macro names and field names must stay aligned with the lane number.
- Some registers are reserved or capability-only. For example, `BIFPLR4_LINK_CAP_16GT` and `BIFPLR4_LINK_CNTL_16GT` are represented as full-width reserved fields, so callers should avoid programming them as if individual control fields are defined.
- Several masks represent multi-bit capability maps rather than scalar enums, such as ESM support bitmaps, DLF support maps, AER status/mask/severity fields, and RP PIO status families.

## Test Signals

Useful validation signals for changes touching this chunk or its consumers include:

- Build coverage for AMDGPU with this header included, catching missing or renamed macros in NBIO/PCIe paths.
- Static checks that generated `__SHIFT`/`_MASK` pairs are internally consistent, especially for lane-replicated registers and the dense ESM capability bitmaps.
- Runtime PCIe link diagnostics showing expected link speed/width, equalization completion, and lane error status on NBIO 7.2.0 hardware.
- AER/DPC exercise or fault-injection tests that confirm status fields decode correctly and clear sequences do not drop unrelated bits.
- MSI enablement tests that verify message address/data/control fields are programmed without disturbing adjacent fields.
- Power-management tests for L1 PM substate and DLF/ESM negotiation fields, especially across suspend/resume and link retraining.
