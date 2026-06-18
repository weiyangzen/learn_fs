# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 76454-78883

## Scope

This chunk is a generated AMDGPU NBIO 6.1 shift/mask header segment. It contains 2,069 `#define` field-layout macros across 2,430 source lines. There are no C functions, structs, enums, global objects, locks, allocations, or executable statements in this range.

The range covers the Synopsys/DesignWare-style `DWC_E12MP_PHY_X4_NS_X4_1` PCIe PHY register field layout for the second, third, and fourth raw lanes of the x4 PHY instance. It starts mid-register in the tail of `RAWLANE1_DIG_PCS_XF_RX_PCS_IN_4`, continues through most of the RAWLANE1 digital receive/FSM/always-on/IRQ/PMA/TX/RX control blocks, repeats the same lane-local digital register families for RAWLANE2 and RAWLANE3, then enters the shared `SUPX_DIG` block for ID, reference-clock, MPLLA/MPLLB, supervisor override, voltage-level, and ASIC input fields. The source boundary is artificial: the previous chunk is needed for the beginning of RAWLANE1 PCS input fields, and the next chunk is needed for the remainder of `SUPX_DIG_ASIC_IN` and later shared PHY fields.

## Purpose

`nbio_6_1_sh_mask.h` is the bitfield half of AMD's generated NBIO 6.1 hardware register interface. For each named register, it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the bit index used to position a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, or update that field.

The companion `nbio_6_1_offset.h` supplies matching register offsets, and `nbio_6_1_default.h` supplies reset/default values for many of the same register names. Runtime AMDGPU code includes these generated headers and combines offsets with these masks through AMD register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, and SOC15/NBIO SMN access paths.

This chunk specifically describes bit layout for low-level PCIe PHY lane control, adaptation, calibration, interrupt, PMA/PCS handoff, and shared PLL/reference-clock programming. These are hardware-facing definitions used by NBIO, power-management, SR-IOV, reset, link-training, and diagnostic code rather than by filesystem or Ceph logic.

## Important Macro Families

The RAWLANE1 portion begins with remaining RX PCS input masks for equalization CTLE pole and DFE tap 1, then covers:

- PCS cross-function RX handshakes and outputs: `RX_OVRD_OUT`, `RX_PCS_OUT`, `RX_ADAPT_ACK`, `RX_ADAPT_FOM`, TX pre/main/post direction feedback, and lane number reporting.
- Lane-local FSM controls and monitors: `FSM_OVRD_CTL`, `MEM_ADDR_MON`, `STATUS_MON`, fast-path enables for RX startup, adaptation, AFE/DFE/bypass/reference-level/IQ calibration, supervisor and TX/RX power-up/VCO steps, and common-calibration status.
- Always-on analog/digital calibration trim and observation fields: AFE attenuator/CTLE/VGA IDAC offsets, DFE summer/phase/data/bypass/error VDAC offsets for even and odd slicers, RX phase-adjust linear/map controls, IQ phase adjust, MPLLA/MPLLB coarse tune, RX/TX RTUNE values, initial power-up done, RX adaptation ATT/VGA/CTLE/DFE tap results, adaptation done, fast flags, slicer controls, lane common-calibration status, and `ADPT_CTL_0` through `ADPT_CTL_7`.
- Lane interrupt status, clear, and mask fields for reset, request, rate, power-state, adaptation request, and adaptation disable events.
- PMA cross-function and lane controls: lane/supervisor override input/output, TX/RX override output, TX/RX PMA input, lane RTUNE control, TX FSM/clock control, RX FSM/loss-of-signal/data-enable override controls, and continuous off-can/adaptation status.

RAWLANE2 and RAWLANE3 repeat the same lane-local pattern more completely from their PCS TX override/input/output groups through RX PCS inputs, RX adaptation feedback, FSM controls, always-on calibration/adaptation registers, IRQ controls, PMA handoff registers, and TX/RX control/status registers. The repetition is intentional generated hardware metadata: per-lane macro names differ by `RAWLANE2` or `RAWLANE3`, while field shapes should remain consistent unless the underlying PHY lane is intentionally asymmetric.

The `SUPX_DIG` shared block at the end covers:

- Shared identification and reference clock controls: `IDCODE_LO`, `IDCODE_HI`, `REFCLK_OVRD_IN`, and reference-clock enable/divider/source override fields.
- Shared MPLL controls for `MPLLA` and `MPLLB`: override and ASIC input fields for PLL enable, reference divide-by-2, divided clock enables, fractional/SSC controls, SSC range/clock selection, multiplier, bandwidth, and divided-clock multipliers.
- Shared supervisor and level controls: RTUNE request/acknowledge, reset request/acknowledge handshakes, MPLLA/MPLLB state bits, override enablement, RX VREF control and enable, and TX vboost level and enable.
- Shared ASIC input fields at the chunk end: PHY reset, reference-clock enables, pad/reference selection, burn-in and powerdown test bits, RTUNE and reset handshakes, MPLLA/MPLLB state, and bandgap enable. This register is truncated by the line boundary after `RES_REQ_IN_MASK`.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the macro namespace. Consumers rely on the generated register names, field names, shifts, and masks remaining synchronized with AMD's NBIO 6.1 register database, companion offset/default headers, and the actual GPU hardware.

The constants are untyped preprocessor integer literals, generally with an `L` suffix. They encode bit positions and masks only. They do not encode register access width, reset value, volatility, read/write permission, write-one-to-clear behavior, sequencing constraints, lane ownership, firmware ownership, or side effects. Those semantics must come from the hardware specification and the driver access path.

## Control Flow

This header has no local control flow. Runtime flow is external:

1. AMDGPU NBIO, power-management, virtualization, or diagnostics code selects an NBIO 6.1 register offset from `nbio_6_1_offset.h`.
2. The code reads the hardware register through SMN/MMIO helpers, decodes fields using this header's masks and shifts, or composes an updated value by preserving unrelated bits and inserting field values.
3. The decoded or updated value participates in PCIe PHY initialization, link bring-up, lane calibration/adaptation, clock/PLL programming, reset, interrupt handling, power-state transitions, SR-IOV policy, or debug collection.

Likely flows using fields from this chunk include lane power-up, RX adaptation and calibration sequencing, equalization feedback, PLL/SSC programming, PHY reset and reference-clock gating, lane-local interrupt acknowledgement, loss-of-signal/data-enable handling, RTUNE handshakes, and per-lane or shared PHY status dumps.

## State And Persistence Behavior

The header itself stores no state. It names state held in NBIO 6.1 PCIe PHY registers. Persistence is determined by the GPU reset domain, PHY reset, PCIe link reset, suspend/resume save-restore, firmware/SMU initialization, PF/VF partitioning, and explicit driver writes.

Represented state includes lane handshake status, RX adaptation figure-of-merit and done bits, equalization and DFE/AFE adaptation results, calibration offset trims, FSM state and command readiness, interrupt status/clear/mask bits, PMA/PCS override state, lane RTUNE values, TX/RX FSM and clock controls, shared PHY identity, reference-clock routing, MPLLA/MPLLB multipliers/bandwidth/SSC configuration, RX VREF and TX vboost levels, supervisor request/acknowledge handshakes, PHY reset, test-mode controls, and bandgap enable.

Several fields are not passive storage. FSM override/start/jump fields can redirect lane microsequencing; interrupt clear fields acknowledge latched events; reset and powerdown bits affect live PHY availability; reference-clock and PLL controls affect link clocking; RTUNE request/acknowledge fields participate in analog tuning handshakes; and adaptation/calibration controls interact with ongoing link training. Call sites must provide ordering, polling, timeout, and reset handling.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 6.1 register data and must stay aligned with sibling generated headers:

- `nbio_6_1_offset.h` supplies matching offsets for the `DWC_E12MP_PHY_X4_NS_X4_1_*` register names.
- `nbio_6_1_default.h` supplies default values for the same PHY families, including `SUP_DIG`/`SUPX_DIG`, lane, PLL, RTUNE, and analog/default registers.
- AMDGPU register helper macros consume these constants for field extraction and update.

Direct include users in this tree include `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`, and Vega power-management include bundles such as `pm/powerplay/hwmgr/vega10_inc.h` and `vega12_inc.h`. The surrounding AMDGPU stack integrates these definitions with NBIO initialization, GPU reset, SR-IOV/mxGPU support, power management, PCIe link management, and hardware diagnostics.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware metadata. It has no direct Ceph or distributed-filesystem control flow.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while causing software to program the wrong PHY bit. This is especially risky for reset, PLL, clock, RTUNE, adaptation, interrupt-clear, and override fields.
- The chunk starts and ends mid-register family. The previous chunk is needed for the complete RAWLANE1 RX PCS input context, and the next chunk is needed for the remainder of `SUPX_DIG_ASIC_IN` plus later shared PHY definitions.
- RAWLANE2 and RAWLANE3 are highly repetitive. A lane-specific typo can be hard to notice in review, but can disable or misdiagnose only one physical lane.
- Override fields can bypass normal hardware/firmware sequencing. Incorrect use may leave a lane stuck in calibration, hold a reset or request line asserted, or conflict with SMU/firmware ownership.
- PLL and reference-clock fields control shared resources. Bad masks can destabilize all lanes on the x4 PHY instance, not just the lane being debugged.
- Interrupt clear and mask fields must match the hardware's clear semantics. Treating a clear bit as ordinary storage can lose events; failing to clear a latched bit can produce repeated interrupts or false diagnostics.
- Adaptation and calibration result fields are meaningful only when corresponding done/status bits indicate valid data and the lane is in a suitable power/link state.
- Reserved masks are generated for full register preservation, but driver code should avoid intentionally writing reserved bits unless the hardware programming sequence explicitly requires preserving read values.

## Test Signals

- Build AMDGPU with NBIO 6.1 support enabled. Direct macro users should catch missing, renamed, or malformed generated symbols.
- Run generated-header consistency checks against the authoritative NBIO 6.1 register database: offset-to-field pairing, shift/mask width checks, non-overlap checks within registers, reserved-field coverage, and RAWLANE1/2/3 repetition checks.
- Compare `nbio_6_1_sh_mask.h`, `nbio_6_1_offset.h`, and `nbio_6_1_default.h` for matching `DWC_E12MP_PHY_X4_NS_X4_1_*` register families and default-compatible field widths.
- Runtime probe on affected Vega/NBIO 6.1 GPUs should show stable PCIe link training, negotiated width/speed, PLL lock behavior, and absence of unexpected PHY reset or link flapping.
- PHY diagnostics should decode lane adaptation results, FSM status, lane number, RTUNE values, and common-calibration done/status bits consistently across RAWLANE1, RAWLANE2, and RAWLANE3.
- Interrupt validation should exercise lane reset/request/rate/power-state/adaptation events, mask behavior, clear behavior, and absence of repeated stale events.
- Suspend/resume, GPU reset, and SR-IOV/PF-VF tests should verify that shared clock/PLL/reset/RTUNE state is restored or reinitialized in the expected ownership domain.
