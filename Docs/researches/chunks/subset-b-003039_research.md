# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 83978-86503

## Scope And Purpose

This chunk is a generated bitfield metadata slice for NBIO 6.1 register definitions. It covers the tail of the DWC E12MP PHY x4 namespace instance `X4_1`, the KPFIFO/KPNP sideband blocks, and the beginning of the second DWC E12MP PHY x4 supervisor namespace instance `X4_2`. The file contains only preprocessor constants; it does not implement functions, structs, enums, or executable logic.

The exported interface is the conventional AMD register-field pair format: one `__SHIFT` macro and one `_MASK` macro for each register field. Consumers combine these field definitions with matching register-address macros from `nbio_6_1_offset.h`, reset/default values from `nbio_6_1_default.h`, and AMDGPU register access helpers to pack, update, read, or decode hardware register values.

This chunk contains 1,998 `#define` macros across 519 register-comment groups. Most of the opening section is 16-bit PHY memory data windows, followed by richer lane, FIFO, PHY-management, and supervisor PLL/analog control fields.

## Register Families Covered

The first large block continues `DWC_E12MP_PHY_X4_NS_X4_1_RAWCMNX_DIG_MEM_*` fields. It starts partway through common memory bank `CMN5_B4_R15` and continues through `CMN5_B7_R31`, then covers `CMN6_B0_R0` through `CMN6_B6_R31`. These registers expose a single `DATA` field at shift 0 with mask `0xFFFFL`, making them raw 16-bit memory/register windows rather than semantically named control fields.

After the memory windows, the chunk defines `X4_1` common digital controls:

- `RAWCMNX_DIG_CMN_CTL` exposes `PHY_FUNC_RST`.
- `RAWCMNX_DIG_MPLLA_*` and `RAWCMNX_DIG_MPLLB_*` override MPLL bandwidth and spread-spectrum controls, including SSC range, fractional-N control, SSC clock selection, SSC enable value, and override-enable bits.

The `X4_1_RAWLANEX` section describes lane-local PCS, PMA, FSM, interrupt, and analog-always-on fields. TX/RX PCS interface registers expose request/ack state, reset, P-state, low-power detect, link width, rate, MPLL selection/enables, RX detect, VCO and reference-load override values, RX loss threshold override, equalizer settings, adaptation controls, and TX pre/main/post cursor direction fields. The FSM fields include explicit override control (`FSM_JMP_ADDR`, `FSM_JMP_EN`, `FSM_CMD_START`, `FSM_OVRD_EN`), FSM address/status monitor fields, fast-calibration enable bits for RX startup, AFE/DFE, bypass, reference-level, IQ, VCO wait/calibration, TX common mode, TX RX detect, common calibration status, and many AON offset/calibration fields for AFE, CTLE, VGA, DFE, phase adjustment, RX adaptation, RTUNE, and coarse MPLL tuning.

The KPFIFO block (`nbio_lcu_kpfifo_kpfifo1_kpfifo_dir`) defines primary TX FIFO status/control fields. It includes `FIFOEmpty`, `FIFOFull`, `FIFOEntries`, per-lane `LinkID`, read-pointer offset, FIFO depth, bypass/init/standalone control, hardware-debug bits, and a PCS/PMA soft reset bit.

The KPNP block (`nbio_lcu_kpnp_kpnp1_kpnp_dir`) defines SNPS PHY node metadata and lane request/control fields. It includes hardware version fields, PHY technology/type/vendor identifiers, node start/end lanes, per-lane TX/RX request and acknowledge bits for lanes 0 through 3, PMA reference-pad and lane disable controls, RX VREF/TX vboost level fields, staggering mode/resolution, PHY and lane soft reset bits, and a register-reset-on-DXIO-PHY-reset control.

The final visible block begins `nbio_pipe_pcs_dwc_e12mp_phy_x4_ns2...` for `DWC_E12MP_PHY_X4_NS_X4_2_SUP_DIG_*`. It includes IDCODE low/high data fields, reference clock override controls, MPLLA/MPLLB divider and override inputs, supervisor override request/ack fields, level/ASIC inputs, analog MPLLA/MPLLB override outputs, RTUNE/RX termination analog outputs, analog status, MPLLA MPLL power-control calibration/override/status fields, MPLL timing thresholds, coarse-tune values, and MPLLA SSC phase/frequency fields. The chunk ends while defining the corresponding MPLLB MPLL power-control calibration fields, so the remainder of the `X4_2` supervisor definitions are in a later chunk.

## APIs, Types, And Functions

There are no callable APIs, C types, or control abstractions in this chunk. The important interface is the macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the already-shifted bit mask.
- Most DWC PHY fields in this chunk are 16-bit masks (`0xFFFFL`, `0x00FFL`, etc.); KPFIFO and KPNP fields use 32-bit masks where the associated registers expose wider state.

The expected consumer pattern is generated-register access code or AMDGPU hardware setup paths that read a register, clear the field mask, insert `(value << SHIFT) & MASK`, and write the new value through SMN/MMIO helpers. Read paths use the same masks and shifts to decode hardware state, status, acknowledgements, version IDs, calibration completion, FIFO state, or lane request status.

## Control Flow

This header has no runtime control flow. All effects occur through compile-time macro substitution in code that includes the header.

The hardware protocols implied by the field names are sequencing-sensitive even though the sequencing is not encoded here. Examples include reset and request/ack handshakes in PCS TX/RX and KPNP lane-control fields, RX adaptation request/ack/FOM reporting, PHY and lane soft reset ordering, FIFO initialization/bypass state, RTUNE request/ack, MPLL calibration start/done/status flows, and PLL power-up/power-down timing thresholds. Driver code must supply the ordering, polling, timeout handling, and privilege checks around those fields.

## State And Persistence Behavior

The header stores no software state and performs no persistence. It describes hardware state that persists in NBIO PHY/FIFO/PLL registers until reset, power-gate, firmware/hardware state-machine update, or driver write.

Important state categories include raw PHY memory-window data; functional and soft reset bits; MPLLA/MPLLB bandwidth, divider, multiplier, SSC, and calibration controls; TX/RX PCS request, P-state, rate, width, reset, low-power, RX detect, and ack state; RX AFE/DFE adaptation and equalization values; FSM command/status and fast-calibration bits; AON analog offset values; FIFO occupancy/configuration/debug fields; lane request/ack state; lane TX/RX disable state; reference clock source/range controls; RTUNE, RX termination, and analog comparator state; and MPLL status/timing/coarse-tune state.

Fields named `RESERVED_*` are part of the documented mask layout but should not be used as writable feature state. For write-modify-write paths, preserving reserved bits is important unless hardware documentation explicitly says otherwise.

## Dependencies And Integration Points

This chunk depends on the rest of the generated NBIO 6.1 register package:

- `nbio_6_1_offset.h` supplies the corresponding SMN/MMIO register addresses.
- `nbio_6_1_default.h` supplies reset/default values for many of these names, including PCS RX override defaults, KPFIFO/KPNP defaults, and MPLLA power-control timing defaults.
- Other chunks of `nbio_6_1_sh_mask.h` define the adjacent fields before and after this line range.
- AMDGPU register helper macros/functions provide the actual MMIO/SMN access and field packing/extraction mechanics.

Integration is hardware-facing. These fields sit below AMDGPU PCIe/NBIO and PHY bring-up flows, lane power/reset handling, link training or PHY tuning paths, low-level diagnostic/debug paths, and any firmware or driver sequences that program Synopsys DWC E12MP PHY state. A tree search did not show direct non-header consumers for the sampled field names in this repository snapshot; the matching default header references them, so they appear to be generated register data available for ASIC-specific code, bring-up tooling, or downstream/conditional users.

## Risks And Edge Cases

Generated shift/mask headers are easy to treat as passive data, but incorrect values can corrupt hardware programming. A wrong mask or shift can redirect a write into reserved bits, reset bits, PLL controls, lane disable fields, or calibration state, with symptoms ranging from link-training failure to a wedged PHY.

The raw memory-window block is repetitive and vulnerable to off-by-one generation mistakes. Each `CMN*_B*_R*` entry has only a full-width `DATA` field, so the semantic meaning is not recoverable from this chunk alone; consumers need the matching address map and external hardware documentation or generated tables.

Many fields are override controls paired with override-enable bits. Setting values without the matching enable, or enabling stale override values, can produce confusing behavior during PHY bring-up and debug. This is especially true for `MPLLA/MPLLB_*_OVRD_*`, PCS TX/RX override inputs, supervisor overrides, RTUNE, RX termination, and analog MPLL outputs.

Request/ack and calibration/status fields require polling discipline. Code using lane request/ack, TX/RX PCS request/ack, RX adaptation, RTUNE, CMNCAL, or MPLL calibration status needs bounded waits and clear timeout reporting rather than assuming immediate hardware response.

The KPFIFO/KPNP fields use 32-bit masks, unlike most 16-bit DWC PHY registers in this chunk. Generic helpers must not assume all registers in the chunk are 16-bit just because the DWC memory and supervisor fields are 16-bit.

Reserved masks are explicitly generated throughout the chunk. Read-modify-write code should preserve them, and tests should catch writes that clear or set reserved fields unintentionally.

## Test Signals

The primary validation signal is successful compilation of NBIO 6.1 AMDGPU code and generated headers that include these names. Because this chunk has no executable logic, behavioral validation comes from hardware, simulator, or register-trace coverage.

Useful test and debug signals include:

- Register-pack/unpack checks that verify representative masks and shifts, especially full-width `DATA`, PCS TX/RX rate/width/P-state fields, KPFIFO 32-bit fields, KPNP per-lane request/ack bits, and MPLL timing/coarse-tune fields.
- PHY reset and bring-up traces showing correct use of `PHY_FUNC_RST`, KPNP PHY/lane soft reset, PCS reset/request fields, and expected ack/status transitions.
- Link-training or lane-management tests that exercise lane disable, lane request/ack, TX/RX rate/width/P-state, low-power, RX detect, and TX pre/main/post direction fields.
- RX adaptation and equalization tests that observe AFE/DFE enable, adaptation request/ack, FOM, EQ gain/boost/tap, phase-adjust, and loss-threshold fields.
- PLL/clock tests that verify MPLLA/MPLLB divider, multiplier, SSC, bandwidth, calibration, power-state, timing-threshold, coarse-tune, and status fields against expected hardware traces.
- FIFO diagnostics that check KPFIFO empty/full/entry counts, per-lane link IDs, FIFO depth, bypass/init, and soft reset behavior.
- Static checks over generated headers confirming every field has both a shift and a mask, reserved bits do not overlap active masks, and masks match the declared shift/width patterns.

Merged per-file research should connect this chunk with adjacent `nbio_6_1_sh_mask.h` chunks for the complete NBIO 6.1 field map and with `nbio_6_1_offset.h` for the addresses that make these masks actionable.
