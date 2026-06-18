# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 207252-209691

## Scope

This chunk is a generated DCN 3.2.0 register-field shift/mask slice for the AMD display C20 PHY `CR4` raw-lane digital namespace. It contains C preprocessor constants only: 2,120 `#define` entries in this range, split into 1,061 `_SHIFT` macros and 1,059 `_MASK` macros, with `//<REGISTER>` comments grouping fields by register. There are no functions, structs, enums, executable branches, loops, allocations, locks, direct MMIO reads, or direct MMIO writes in this range.

The range starts immediately after the `C20_PHY_CR4_RAWLANE1_DIG_FSM_SKIP_RX_DCC_RATE_CAL` mask tail, then covers the remaining lane-1 FSM skip/status fields. It covers the full visible `C20_PHY_CR4_RAWLANE2` digital TX/RX PCS, firmware, IRQ, control, PMA, and FSM field families. It then covers the beginning of the analogous `C20_PHY_CR4_RAWLANE3` digital TX side and part of its RX PCS context fields. The range ends mid-register in `C20_PHY_CR4_RAWLANE3_DIG_RX_PCS_XF_CNTX_CFG_1`: only `EQ_CTLE_ZERO` and `EQ_AFE_RATE` masks are present here, while the remaining masks for that register continue in the next chunk.

Although this file lives under a local `ceph-client` source mirror, the content is AMDGPU Display Core hardware metadata rather than Ceph or distributed filesystem logic.

## Purpose And Hardware Surface

This header supplies bit-layout constants for programming DCN 3.2.0 C20 PHY registers. Companion generated offset headers name the indexed PHY registers; this `*_sh_mask.h` file defines the bit positions and masks used by AMDGPU display register helpers to pack writes and decode reads.

The hardware surface in this chunk is concentrated on CR4 raw-lane PCS, PMA, firmware, IRQ, and FSM control:

- `C20_PHY_CR4_RAWLANE1_DIG_FSM_*` tail fields expose single-bit controls to skip specific RX startup/rate/continuous calibration or adaptation steps and a reset-calibration done status bit.
- `C20_PHY_CR4_RAWLANE2_DIG_TX_PCS_XF_*` defines TX PCS cross-interface lane override/input/output, reset/request handshakes, power-state, low-power/data/invert/clock/beacon/MPLL controls, master MPLL and deskew controls, TX context configuration, and TX rate/width/MPLL selection.
- `C20_PHY_CR4_RAWLANE2_DIG_TX_FW_XF_*` defines the TX firmware cross-interface request/ack, rate request/ack, TX coefficient and term-control direction requests, lane transceiver mode, and lane-number reporting.
- `C20_PHY_CR4_RAWLANE2_DIG_TX_IRQ_CTL_*` defines TX interrupt mask, enable flag, status, and clear fields for reset, request, rate change, RX-to-TX loopback enable/disable, rtune, TX termination control, and lane transceiver mode events.
- `C20_PHY_CR4_RAWLANE2_DIG_TX_CTL_*` defines TX FSM control enables, stage selection, lock/reset/disable knobs, clock and off-cancel status, rate IRQ acknowledgement, termination code, firmware power-up done, and MPLLA/MPLLB restart-calibration controls.
- `C20_PHY_CR4_RAWLANE2_DIG_TX_PMA_XF_*` defines PMA-facing TX lane override/input/output and support handshakes, including TX request/reset, TX ACK, LPD/enable/invert/width/MPLL selection, rtune request/ack, and lane state readback.
- `C20_PHY_CR4_RAWLANE2_DIG_RX_PCS_XF_*` defines RX PCS reset/request and power/data/invert/CDR/adaptation controls, RX margining controls, recalibration force/skip/bank selection, loopback selection, context selection, output ACK, and context EQ configuration fields.
- `C20_PHY_CR4_RAWLANE2_DIG_RX_FW_XF_*` defines RX firmware request/ack, rate, data width, PLL request, adaptation request/done/FOM, direction requests for TX pre/main/post coefficients, and RX clock-control acknowledgements.
- `C20_PHY_CR4_RAWLANE2_DIG_RX_IRQ_CTL_*` defines RX interrupt masks/enables/status/clears for reset, request, rate, pstate, adaptation request/disable, termination control, and RX margining start/init/finish/global/error-clear events.
- `C20_PHY_CR4_RAWLANE2_DIG_RX_CTL_*` defines RX termination/status, adaptation mode and selection, PPM drift and CDR status, PMA misc control, adaptation FOM/reference-error/IQ readback, phase-adjustment controls, margin deltas/status/error, RX FSM control, IQ code read/write, and phase-adjust update enable.
- `C20_PHY_CR4_RAWLANE2_DIG_FSM_*` defines the raw-lane firmware/FSM debug and policy surface: override control, jump bank, reset/interrupt control, breakpoints, memory and status monitors, firmware stage and scratch registers, CR lock, fast-supervisor flags, TX/RX fast-path controls, and extensive TX/RX calibration/adaptation skip bits.
- `C20_PHY_CR4_RAWLANE3_DIG_TX_*` repeats the visible lane-2 TX PCS, firmware, IRQ, control, and PMA families for raw lane 3.
- `C20_PHY_CR4_RAWLANE3_DIG_RX_PCS_XF_*` begins the lane-3 RX PCS controls, including reset/request, pstate/LPD/data/invert/CDR/adaptation, margin/recalibration, loopback, context selection, ACK, and the first RX EQ context configuration fields.

## Important Definitions

The generated naming convention is consistent across the chunk:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted bit mask for that field.
- `//<REGISTER>` comments identify the register whose field definitions follow.

Important macro families visible here:

- FSM skip and fast-path controls: `DIG_FSM_SKIP_*`, `DIG_FSM_FAST_*`, `DIG_FSM_FSM_*`, and `DIG_FSM_RX_CAL_STATUS` fields control whether hardware/firmware runs or bypasses TX DCC, RX AFE, DFE, IQ, phase, VGEN, signal-detect, DCC data/bypass/phase/range, VGA, CTLE, ATT, margining, adaptation reload, startup, rate, and continuous calibration/adaptation stages. Most of these are single-bit fields paired with `RESERVED_15_1`.
- PCS override/input/output handshakes: `DIG_TX_PCS_XF_*` and `DIG_RX_PCS_XF_*` fields represent reset, request, ACK, pstate, low-power disable, data enable, invert, clock ready, beacon, MPLL, CDR SSC, adaptation, margin, recalibration, loopback, lane number, and deskew signals. Override registers pair each value field with an `*_OVRD_EN` bit.
- Context EQ configuration: `RX_PCS_XF_CNTX_CFG_*` fields encode equalizer ATT/VGA/CTLE/AFE/DFE/adaptation/rate/width/VCO and DCC settings such as `EQ_ATT_LVL`, `EQ_VGA_GAIN`, `EQ_CTLE_*`, `EQ_AFE_*`, `EQ_DFE_TAP1`, `ADAPT_MODE`, `DELTA_IQ`, `CDR_VCO_CONFIG`, `RATE`, `WIDTH`, and load values.
- Firmware cross-interface fields: `TX_FW_XF_*` and `RX_FW_XF_*` expose firmware-visible request/ack pairs, TX/RX rate requests, TX coefficient direction requests, lane transceiver mode, adaptation ACK/FOM, and RX clock-control state.
- IRQ fields: `TX_IRQ_CTL_*` and `RX_IRQ_CTL_*` provide mask, enable, status, and clear bits. The TX side covers rate/reset/request/loopback/rtune/termination/transceiver-mode events; the RX side covers reset/request/rate/pstate/adaptation/termination/margining events.
- Control/status fields: `TX_CTL_*` and `RX_CTL_*` expose FSM control enables, stage selection, lock/reset/disable controls, clock/off-cancel status, firmware power-up completion, MPLL restart calibration, term codes, CDR and PPM status, adaptation FOM/reference-error/IQ values, phase-adjust update controls, margin status/error, and IQ code read/write fields.
- PMA cross-interface fields: `TX_PMA_XF_*` and `RX_PMA_XF_*` bridge PCS/control logic to the PMA with request/reset/ACK, lane state, TX disable and PMA reset outputs, rtune handshakes, RX termination/VREF outputs, and PMA input state.
- Firmware scratch/debug fields: `DIG_FSM_FW_SCRATCH_0` through `DIG_FSM_FW_SCRATCH_11`, breakpoints, memory address/status monitors, and firmware stage fields define opaque or diagnostic 16-bit values used by firmware or debug tooling.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears when AMDGPU Display Core and low-level PHY code combine these constants with generated register offsets and helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, indexed PHY register accessors, and generated shift/mask tables.

Typical runtime flow using this slice:

1. Link bring-up or retraining code configures raw-lane TX/RX PCS and PMA handshakes, selects lane/link state, sets pstate/LPD/data/invert/clock/MPLL controls, and monitors request/ACK status.
2. Firmware-assisted PHY flows use `TX_FW_XF_*`, `RX_FW_XF_*`, firmware scratch registers, status monitors, breakpoints, and FSM stage fields to coordinate rate changes, adaptation, TX coefficient direction requests, and lane recovery.
3. PHY calibration policy code programs FSM fast and skip fields before startup, rate-change, or continuous calibration/adaptation sequences, then reads calibration done/status fields.
4. Interrupt handling code masks, enables, reads, and clears lane-local TX/RX events for rate, reset, request, loopback, rtune, term-control, adaptation, pstate, and margining transitions.
5. Diagnostic, validation, or lab tooling reads context EQ configuration, adaptation FOM/reference-error/IQ data, PPM/CDR status, margin status/error, IQ step/linear codes, and PMA/PCS input/output state.

The state described here is hardware register state:

- Persistent programmed state includes PCS/PMA override enables and values, pstate/LPD/data/invert/clock/MPLL controls, TX/RX FSM control policy, calibration/adaptation skip and fast flags, IRQ masks/enables, context EQ settings, adaptation mode/selection, phase-adjust controls, margin delta controls, IQ code writes, CR locks, breakpoints, jump bank, firmware scratch values, and MPLL restart-calibration controls.
- Volatile readback includes ACK/request status, off-cancel and adaptation continuous status, firmware power-up done, RX CDR and PPM status, adaptation FOM and reference-error data, IQ left/right and code readbacks, margin status/error, FSM status monitor fields, firmware stage, calibration-done bits, PMA input/output state, and IRQ status bits.
- Side-effecting or sequencing-sensitive fields include interrupt clear bits, reset/request/ACK overrides, FSM reset/interrupt controls, calibration skip/fast flags, CR lock, rate IRQ ACK, phase-adjust update bits, margin error clear, recalibration force/skip controls, IQ write fields, and PMA reset/TX disable outputs.

There is no persistence to disk or driver-owned durable storage. Values persist only as hardware register programming until the relevant lane is reconfigured, power-gated, reset, retrained, or overwritten by firmware/driver code.

## Dependencies And Integration Points

This chunk depends on exact generated-name and numeric consistency across AMD's DCN 3.2.0 register header set. The field names must match indexed offsets in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`, including CR4 raw-lane offsets such as `ixC20_PHY_CR4_RAWLANE2_DIG_TX_IRQ_CTL_IRQ_MASK`, `ixC20_PHY_CR4_RAWLANE2_DIG_RX_IRQ_CTL_IRQ_MASK`, `ixC20_PHY_CR4_RAWLANE3_DIG_TX_IRQ_CTL_IRQ_MASK`, and `ixC20_PHY_CR4_RAWLANE3_DIG_RX_IRQ_CTL_IRQ_MASK`.

Known consumers of `dcn_3_2_0_sh_mask.h` in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`

The direct lane-level integration is with AMDGPU Display Core link encoder, PHY, DMUB/firmware, interrupt, diagnostics, and power-management paths that access indexed C20 PHY registers. Missing macros generally fail at compile time. Wrong numeric shifts or masks can compile successfully and only appear as link-training, calibration, interrupt, or low-power failures on DCN 3.2 hardware.

## Risks And Maintenance Notes

- Numeric drift from the DCN 3.2.0 C20 PHY register specification is the main risk. These macros form a hardware ABI; an off-by-one shift or wrong mask can program the wrong bit in a densely packed 16-bit register.
- Repeated lane families are copy-generation sensitive. Lane 2 and lane 3 definitions are structurally similar, while the range starts with the tail of lane 1 and ends inside lane 3. Instance-prefix mistakes may compile but affect only one physical lane or connector path.
- Skip and fast-path fields alter calibration execution. Incorrect masks can bypass required TX DCC, RX AFE/DFE/IQ/phase/DCC/VGEN/signal-detect/CTLE/VGA/ATT/margining steps, causing marginal links, intermittent black screens, or failures limited to specific link rates, cables, or resume paths.
- IRQ clear/status fields are side-effect sensitive. Confusing mask, enable, status, and clear definitions can drop lane events, leave interrupts stuck, or acknowledge the wrong condition.
- Override fields can force hardware handshakes. Bad `*_OVRD_EN` or value masks for reset, request, ACK, pstate, LPD, data enable, invert, MPLL, CDR, adaptation, recalibration, loopback, TX disable, or PMA reset can fight firmware/hardware sequencing.
- Context EQ and adaptation fields are signal-integrity sensitive. Mistakes in ATT/VGA/CTLE/AFE/DFE/rate/width/VCO/adaptation fields may only show up under high bandwidth, long cable, MST, retraining, or thermal/voltage corners.
- Firmware scratch and generic debug fields are opaque 16-bit contracts. Renaming or changing their full-width masks may break firmware/debug interactions that are not obvious from C code.
- Boundary completeness is a chunking risk. The first line depends on preceding lane-1 definitions, and `RAWLANE3_DIG_RX_PCS_XF_CNTX_CFG_1` is incomplete at the end of this chunk. The final per-file document should merge adjacent chunks before making complete claims about lane 1 or lane 3 register coverage.

## Test Signals

Useful validation combines generated-header checks, compile coverage, and DCN32 hardware behavior:

- Build AMDGPU Display Core with DCN 3.2 support enabled and confirm all referenced CR4 raw-lane field macros resolve in resource, IRQ, DMUB, GPIO, clock-manager, and PHY-related consumers.
- Run generated-register consistency checks for lines 207252-209691: every complete register should have paired `_SHIFT` and `_MASK` definitions, masks should fit the expected 16-bit indexed PHY register width, and fields within a register should not overlap unexpectedly.
- Compare lane-2 and lane-3 repeated TX PCS/FW/IRQ/CTL/PMA fields against the authoritative DCN 3.2.0 C20 PHY register database and against neighboring RAWLANE0/1 definitions where the hardware is expected to repeat.
- Exercise DisplayPort link training and retraining on CR4-backed lanes across supported link rates and lane counts, including hotplug, link loss/recovery, MST if available, high-bandwidth modes, and suspend/resume.
- Validate TX and RX IRQ behavior by triggering representative rate, reset, request, loopback, rtune, termination, pstate, adaptation, and margining events, then checking mask/enable/status/clear semantics.
- Validate calibration policy by reading calibration-done/status fields and link stability after startup, rate-change, and continuous calibration/adaptation paths with skip/fast flags at their expected defaults.
- Validate RX adaptation and margining diagnostics by decoding context EQ fields, adaptation FOM/reference-error/IQ values, PPM/CDR status, phase-adjust readbacks, margin status/error, and IQ code read/write paths.
- Use register dumps before and after lane power-up, link training, retraining, power-down, and resume to confirm persistent programmed fields and volatile readback fields decode coherently through these masks.

## Chunk-Specific Summary

Lines 207252-209691 define DCN 3.2.0 C20 PHY CR4 raw-lane digital register shifts and masks for the tail of lane-1 FSM skip/status fields, the full visible lane-2 PCS/FW/IRQ/CTL/PMA/FSM control surface, and the start of lane-3 TX plus RX PCS fields. The content is generated register ABI, not executable driver logic. Correctness depends on exact mask/shift values, repeated lane consistency, safe handling of calibration skip/fast/override and interrupt clear bits, and hardware validation through link training, firmware handshakes, adaptation, margining, and suspend/resume flows.
