# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 33366-35753

## Scope

This chunk covers a generated AMD DPCS 4.2.0 register shift/mask header section for `DPCSSYS_CR1_RAWLANE*` digital lane registers. The range starts inside RAWLANE0 FSM fast-calibration fields, covers the remainder of RAWLANE0, all visible RAWLANE1 PCS/FSM/IRQ/PMA/TX/RX control masks, and begins RAWLANE2 PCS/FSM/IRQ masks through `DPCSSYS_CR1_RAWLANE2_DIG_IRQ_CTL_IRQ_MASK`.

## Purpose

The header provides preprocessor constants that describe bit positions and masks for memory-mapped DPCS hardware registers. Each register field is represented as two constants:

- `<register>__<field>__SHIFT`: the bit offset inside a 16-bit hardware register field window.
- `<register>__<field>_MASK`: the already-shifted mask used to isolate or update that field.

There are no functions, structs, or runtime algorithms in this chunk. Its purpose is to feed AMD display register accessor macros with stable field metadata matching the DPCS 4.2.0 register map.

## Covered Register Blocks

- RAWLANE0 FSM tail: fast TX/RX sequencing, common calibration status, continuous RX calibration/adaptation, DCC flags/status, FSM lock, OCLA debug enables, TX EQ update, RCAL status, and IQ phase offset.
- RAWLANE0 IRQ control: reset/request/rate/pstate/adaptation/phase-2-calibration/loopback/DCC/TX IRQ status, clear, and mask registers.
- RAWLANE0 PMA bridge: lane/MPLL override inputs and outputs, PMA supervisor state, TX/RX request and reset overrides, loopback enables, PMA data enables, retune request/ack, MPHY PWM/term controls, and RX adaptation IQ phase map override.
- RAWLANE0 TX/RX controls: TX FSM timing, RXDET gating by power state, TX clock control, DCC continuous status, RX FSM enable/rate-change behavior, LOS mask count, RX data enable override count, off-candidate/adaptation continuous status, and OCLA/UPCS debug controls.
- RAWLANE0 and RAWLANE1/2 PCS transfer blocks: TX/RX PCS inputs and outputs, override inputs, ATE override inputs, RX EQ/adaptation feedback, FOM, TX pre/main/post direction fields, lane number, reserved scratch registers, PH2 calibration handshakes, and TX/RX termination controls.
- RAWLANE1 complete visible lane block: PCS transfer registers, FSM override/status/fast-calibration registers, IRQ status/clear/mask registers, PMA bridge registers, TX/RX control registers, and ATE override copies.
- RAWLANE2 partial lane block: PCS transfer and EQ registers, FSM override/status/fast-calibration registers, and IRQ control through the first IRQ mask register. The chunk ends before the rest of RAWLANE2 IRQ/PMA/TX/RX definitions.

## Important Definitions

The most important macro families in this chunk are:

- `DPCSSYS_CR1_RAWLANE*_DIG_PCS_XF_*`: PCS-side transfer and override fields. These carry lane power state (`PSTATE`), low-power disable (`LPD`), lane `WIDTH`, link `RATE`, MPLL selection/enables, TX/RX request/reset handshakes, data enables, adaptation controls, RX equalization results, and ATE override controls.
- `DPCSSYS_CR1_RAWLANE*_DIG_FSM_*`: firmware/hardware FSM control and monitor fields. `FSM_FSM_OVRD_CTL` exposes jump address/start/override/break controls; `FSM_STATUS_MON` exposes state, command-ready, ALU, wait, and mask-disable status; `FAST_*` fields shortcut calibration/adaptation states.
- `DPCSSYS_CR1_RAWLANE*_DIG_IRQ_CTL_*`: lane-local interrupt status, clear, and mask bits for RX/TX reset/request/rate/pstate/adaptation, lane transceiver mode, RX phase-2 calibration, serial loopback, and DCC on-demand activity.
- `DPCSSYS_CR1_RAWLANE*_DIG_PMA_XF_*`: PMA-side bridge fields for MPLL state, TX/RX request/reset overrides, PMA data enables, loopback, RTUNE, MPHY PWM/async/termination controls, and IQ phase-adjust override.
- `DPCSSYS_CR1_RAWLANE*_DIG_TX_CTL_*` and `DPCSSYS_CR1_RAWLANE*_DIG_RX_CTL_*`: lane TX/RX control timing and debug fields, including TX MPLL-off wait time, RXDET permission per power state, TX clock select, async beacon wait, RX LOS masking, and continuous adaptation status.

Field widths vary from one-bit controls to multi-bit hardware values. Examples visible in the chunk include 2-bit or 3-bit `RATE`, `WIDTH`, `PSTATE`, term-control, and direction fields; 4-bit lane number/IQ/equalization fields; 5-bit or wider timing and state counters; 7-bit/13-bit reference/VCO load values; 8-bit adaptation FOM and DFE tap values; and 16-bit reserved registers.

## Control Flow

This header has no control flow on its own. Control flow is introduced by consumers that include the offset header and this shift/mask header, then use generated register descriptor tables and `REG_GET`, `REG_SET`, or `REG_UPDATE` style accessors to read or modify fields.

The nearby integration observed in `drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` includes `dpcs/dpcs_4_2_0_offset.h` and `dpcs/dpcs_4_2_0_sh_mask.h`, then builds link encoder register tables with `DPCS_DCN31_REG_LIST(id)`, `DPCS_DCN31_MASK_SH_LIST(__SHIFT)`, and `DPCS_DCN31_MASK_SH_LIST(_MASK)`. That pattern means these macros are compile-time data for register table initialization rather than directly executed logic.

## State and Persistence Behavior

The constants are stateless at runtime, but they describe persistent hardware state in DPCS lane registers. Writes through these masks can affect:

- Lane power/link state transitions such as reset, request, pstate, width, and rate.
- MPLL enable/selection and common calibration status.
- RX/TX equalization, DCC calibration, RX adaptation, PH2 calibration, and VCO/reference load values.
- Interrupt masks and clear registers, which determine whether hardware events remain latched or visible.
- Debug and override state such as FSM override, ATE override, PMA/PCS override enables, OCLA controls, and loopback enables.

Reserved fields are explicitly masked. Consumers should preserve reserved bits unless hardware documentation says otherwise; many registers expose `RESERVED_*_MASK` values covering the unused high bits of a 16-bit register.

## Dependencies

- The corresponding address definitions live in the matching DPCS offset header, especially `dpcs_4_2_0_offset.h`.
- AMD display resource code maps offsets and masks into register structures through generated macros such as `DPCS_DCN31_REG_LIST` and `DPCS_DCN31_MASK_SH_LIST`.
- Low-level register access depends on the AMD display register helper layer that expands register/field names into offset, shift, and mask lookups.
- The definitions are ASIC/IP-version specific. Similar names appear in other generated DPCS/DCN headers, but mask widths and literal formatting may differ by IP version.

## Integration Points

- Link encoder resource initialization: the DPCS mask and shift tables are part of the per-link encoder register metadata used by DCN 3.1 resource setup.
- DisplayPort/PHY bring-up and link training: fields in PCS/PMA/FSM blocks correspond to lane request/reset, rate, width, MPLL, RX adaptation, and equalization handshakes that link training and PHY control paths rely on.
- Interrupt handling and diagnostics: IRQ status/clear/mask fields provide the bit layout for lane events such as RX/TX reset/request, rate changes, pstate changes, adaptation requests, PH2 calibration, loopback, and DCC on-demand.
- Hardware debug/test paths: ATE override, OCLA, FSM override, loopback, reserved scratch, and PMA/PCS override registers are likely used by diagnostics, validation, or firmware-assisted debug flows rather than normal display modes.

## Risks

- A wrong shift or mask silently writes the wrong hardware bit. In this domain that can break link bring-up, corrupt lane training, leave IRQs stuck, or alter analog PHY tuning.
- Lane definitions are repetitive but not interchangeable. RAWLANE0, RAWLANE1, and RAWLANE2 have mostly parallel fields, but chunk boundaries and per-lane offsets come from the offset header; copy/paste edits can misalign a lane with its address table.
- Multi-bit fields need value-range discipline. Callers must shift and mask values through the helper macros; writing raw values without masking can clobber neighboring reserved or enable bits.
- Override enable/value pairs are high risk. Many fields follow `<signal>_OVRD_VAL` plus `<signal>_OVRD_EN`; enabling an override with stale values can force reset/request/data/loopback/calibration behavior unexpectedly.
- IRQ clear bits are separate from status and mask bits. Confusing status, clear, and mask registers can either drop events or leave latched interrupts uncleared.
- The chunk ends mid-RAWLANE2 IRQ block, so whole-file reasoning must combine this with the next chunk before claiming complete RAWLANE2 coverage.

## Test Signals

- Compile coverage is the primary guard: any renamed or missing macro should fail consumers that build DPCS register lists or field tables.
- Register table smoke tests should verify that `dcn31_resource.c` still builds link encoder `le_shift` and `le_mask` tables with the DPCS shift/mask lists.
- Hardware or emulator validation should exercise link training across supported rates/widths and watch for failures in lane reset/request handshakes, RX adaptation, DCC calibration, and IRQ handling.
- Debug register readback can validate that `REG_UPDATE` on representative fields affects only the intended mask bits and preserves reserved bits.
- Regression signals include DisplayPort link training failures, PHY reset timeouts, unexpected RX/TX IRQ storms, DCC-on-demand interrupt issues, stuck PH2 calibration requests, and broken loopback/ATE diagnostics.
