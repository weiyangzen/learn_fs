# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 204788-207251

## Purpose

This chunk is generated AMD DCN 3.2 register field metadata for the C20 PHY CR4 raw-lane digital interface. It contains no executable C; it exports preprocessor constants that describe bit positions and masks for MMIO-indexed PHY registers. Consumers pair these field macros with register offsets from `dcn_3_2_0_offset.h` and helper macros such as `FD_SHIFT`, `FD_MASK`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

The range starts in the tail of `C20_PHY_CR4_RAWLANE0_DIG_RX_PCS_XF_CNTX_CFG_3`, covers the rest of raw lane 0 receive PCS/firmware/IRQ/control/FSM fields, then covers raw lane 1 transmit PCS/firmware/IRQ/control/PMA fields, raw lane 1 receive PCS/firmware/IRQ/control/PMA fields, and the beginning of raw lane 1 FSM fields. The final line stops inside `C20_PHY_CR4_RAWLANE1_DIG_FSM_SKIP_RX_DCC_RATE_CAL`; the following reserved-field mask belongs to the next line and adjacent chunk.

Although the repository path is under a local `ceph-client` source mirror, this header is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed-filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, types, structs, enums, includes, globals, locks, or allocation paths in this chunk. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a field inside a 16-bit PHY register payload.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field.

The requested range contains 2,102 `#define` lines: 1,051 `__SHIFT` macros and 1,051 `_MASK` macros. Most registers are 16-bit logical PHY registers, with masks such as `0x0001L`, `0x00E0L`, `0xFFFEL`, and `0xFFFFL`.

Major register families in this slice:

- `C20_PHY_CR4_RAWLANE0_DIG_RX_PCS_XF_*`: receive PCS cross-front-end context configuration for equalizer, CDR/VCO, DCC range, rate, width, signal detect thresholds, term control, adaptation selection/mode, DFE bypass, LFPS filtering, and context identity.
- `C20_PHY_CR4_RAWLANE0_DIG_RX_FW_XF_*`: firmware-visible receive handshake and override fields for reset, request, pstate, low-power detect, rate, width, DFE bypass, adaptation request, delta-IQ, ACK, RX-valid override, adaptation FOM, TX pre/main/post cursor direction feedback, and receive clock enables.
- `C20_PHY_CR4_RAWLANE0_DIG_RX_IRQ_CTL_*`: receive interrupt mask, enable/status flags, individual status bits, and clear bits for reset, request, rate, pstate, adaptation request/disable, term-control, and margining events including IQ start, VDAC start, error clear, init, finish, and global margin interrupts.
- `C20_PHY_CR4_RAWLANE0_DIG_RX_CTL_*`: receive control/status fields for term code, continuous off-cancel/adaptation status, adaptation mode/selection, PPM drift, CDR detect, PMA misc controls, adaptation FOM, reference errors, IQ left/right margins, phase-adjust linear/map values, margin deltas/status/error, receive FSM control, IRQ acknowledge, IQ code read/write, and phase-adjust update enable.
- `C20_PHY_CR4_RAWLANE0_DIG_RX_PMA_XF_*`: receive PMA exchange fields for ACK, pstate, and low-power detect override/input paths.
- `C20_PHY_CR4_RAWLANE0_DIG_FSM_*`: firmware/FSM override, jump-bank, memory breakpoints, memory address monitor, status monitor, firmware stage, scratch registers, CR lock state, fast-path controls, and skip bits for transmit and receive calibration/adaptation steps.
- `C20_PHY_CR4_RAWLANE1_DIG_TX_*`: raw lane 1 transmit PCS, firmware, IRQ, control, and PMA fields. These include lane loopback/link-number overrides, reset/request/pstate/data-enable/invert/clock-ready/beacon/MPLL controls, PLL state, deskew, rate/width/term/voltage swing/pre-emphasis/post-cursor controls, TX interrupt handling, TX FSM control, clock control, power-up done, MPLL restore calibration, PMA lane/supervisor overrides, and RTUNE controls.
- `C20_PHY_CR4_RAWLANE1_DIG_RX_*`: raw lane 1 receive PCS, firmware, IRQ, control, and PMA fields mirroring the raw lane 0 receive families, with additional visible PCS input fields for margin IQ/VDAC, reset/request/rate/width/pstate, signal detect, calibration-bank selection, LFPS, and context selection.
- `C20_PHY_CR4_RAWLANE1_DIG_FSM_*`: raw lane 1 FSM override/status/scratch/lock/fast-path fields and the start of receive calibration skip controls.

## Control Flow

This chunk has no local runtime control flow. Runtime sequencing is supplied by AMDGPU display code:

1. DCN 3.2 display/DMUB/resource/IRQ/GPIO/GMC code includes `dcn_3_2_0_offset.h` and `dcn_3_2_0_sh_mask.h`.
2. Register table builders paste register and field names into generated constants. For example, `FD_SHIFT(reg, field)` expands to `reg##__##field##__SHIFT`, and `FD_MASK(reg, field)` expands to `reg##__##field##_MASK`.
3. Higher-level helpers store offsets, shifts, and masks in ASIC-specific register structs or use them directly through `REG_GET`, `REG_SET`, `REG_UPDATE`, and related helpers.
4. Hardware-facing code sequences the actual PHY programming: reset/request handshakes, pstate transitions, lane enablement, link-rate/width changes, adaptation, margining, interrupt clear/ack, and calibration bypass/fast-mode control.

The macros do not encode legal ordering. They only provide field extraction/update metadata; consumers must still handle link training, clock/power state, firmware ownership, interrupt clearing, and calibration timing correctly.

## State And Persistence Behavior

The header stores no software state and persists nothing. It describes bitfields for MMIO/indirect PHY state. The represented hardware state includes:

- Per-lane TX/RX control state for reset, request, pstate, low-power detect, rate, width, PLL, deskew, data enable, inversion, beacon, and term controls.
- Receive adaptation and calibration state for DFE bypass, CTLE/VGA/AFE parameters, CDR/VCO configuration, signal detect, delta-IQ, FOM values, phase adjust, IQ code read/write, PPM drift, CDR detect, and margining status.
- Firmware/PCS/PMA handshake state through override-enable/value pairs, raw input/output views, ACK bits, RX-valid override, clock enable/reset controls, and firmware scratch/stage registers.
- Interrupt state for TX and RX reset/request/rate/pstate/term/margin/loopback/RTUNE events, including mask, enable/status, individual event, and clear registers.
- FSM/debug/calibration state through override controls, jump-bank selection, memory breakpoints, monitor registers, CR locks, fast-mode controls, and skip bits for DCC, AFE, DFE, IQ, phase, VGA, CTLE, attenuation, signal-detect, VGEN, and related startup/continuous calibration steps.

Persistence is hardware-defined. Some fields are configuration bits that retain values until a modeset, link reconfiguration, power-gate transition, suspend/resume, or ASIC reset. Status, IRQ, ACK, clear, monitor, and calibration fields may be read-only, sticky, self-clearing, write-one-to-clear, or sequencing-sensitive; this generated mask header does not distinguish those semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.2 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`, which provides matching `ixC20_PHY_CR4_RAWLANE*` register offsets.
- Low-level register helper headers such as `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_reg.h`, where `FD_SHIFT` and `FD_MASK` paste names into these macros.
- DCN 3.2 include sites in this tree, including `dmub_dcn32.c`, `irq_service_dcn32.c`, `dcn32_clk_mgr.c`, `gmc_v11_0.c`, `hw_translate_dcn32.c`, `hw_factory_dcn32.c`, and `dcn32_resource.c`.

The visible include path confirms the generated mask header is part of the DCN 3.2 hardware contract. In `dmub_dcn32.c`, `dmub_srv_dcn32_regs_init()` loads field masks and shifts through `DMUB_DCN32_FIELDS()`, `FD_MASK`, and `FD_SHIFT`; the same register-helper pattern underpins later `REG_GET`, `REG_SET`, and `REG_UPDATE` operations. Direct C references to the specific `C20_PHY_CR4_RAWLANE*` field names were not visible in the searched display/AMDGPU C sources, so these fields appear to be exported hardware metadata for low-level PHY support and generated register-table compatibility rather than directly named in ordinary control code in this mirror.

## Risks And Edge Cases

- Field drift is the central risk. A wrong shift or mask compiles cleanly but can update the wrong PHY bits, corrupting link setup, lane calibration, interrupt routing, or firmware handshakes.
- Override-enable/value pairs are high risk. Accidentally setting an override enable with a stale value can force reset, pstate, rate, width, DFE bypass, RX-valid, PLL, loopback, data-enable, or term state away from firmware/hardware control.
- IRQ fields are side-effect-sensitive. Confusing mask, enable/status, event, and clear registers can cause missed events, stuck interrupts, or interrupt storms during link training, margining, resets, RTUNE, or loopback transitions.
- Calibration skip and fast-mode fields can hide analog setup failures. Incorrect skip masks for DCC, AFE, DFE, IQ, phase, CTLE, VGA, VGEN, signal detect, or RX margining may only fail on specific link rates, boards, cables, or resume paths.
- Raw lane symmetry is copy-sensitive. Lane 0 RX and lane 1 TX/RX blocks share many patterns but are not interchangeable; a lane-specific typo may only surface on multi-lane links or certain PHY routing configurations.
- The chunk boundaries are artificial. The first register is missing the preceding `DFE_BYPASS__SHIFT` line from the previous chunk, and the last register is missing its `RESERVED_15_1_MASK` line in the next chunk; final file-level conclusions must merge adjacent chunks.
- Reserved masks are part of generated metadata. Driver writes should preserve reserved bits according to hardware rules; blindly writing masked values without read/modify/write discipline can disturb undocumented state.

## Test Signals

Useful validation combines generated-header consistency with hardware behavior:

- Build AMDGPU/DC with DCN 3.2 support enabled; missing or renamed field macros should fail wherever register tables instantiate `FD_SHIFT` or `FD_MASK`.
- Mechanically verify that every visible `__SHIFT` macro in lines 204788-207251 has a matching `_MASK` macro in the same range, except for known boundary artifacts owned by adjacent chunks, and that the field names match exactly.
- Cross-check `C20_PHY_CR4_RAWLANE0/1` register names against `dcn_3_2_0_offset.h` so every field block has a matching register offset.
- Compare this generated slice against AMD's authoritative DCN 3.2 register database or neighboring DCN 3.x headers where C20 PHY field layout is expected to be stable.
- Exercise DCN 3.2 hardware with DisplayPort/USB-C PHY paths across link rates, lane counts, pstate changes, suspend/resume, hotplug, and link retraining.
- Test TX/RX interrupt paths for reset, request, rate, pstate, term-control, margining, loopback, and RTUNE events; watch for stuck IRQ bits, missed clear operations, or repeated interrupts.
- Validate PHY calibration and adaptation behavior with margining, DFE/CTLE/VGA/AFE adaptation, CDR lock, signal detect, and PPM drift scenarios.
- Watch kernel logs and display diagnostics for link-training failures, AUX/HPD symptoms caused by PHY state, blank displays, unstable high-rate links, resume failures, CRC or underrun issues, and firmware/DMUB handshake timeouts.

## Cross-Chunk Notes

Previous chunks contain the beginning of the C20 PHY CR4 raw lane 0 TX/RX field namespace and the first field of `RAWLANE0_DIG_RX_PCS_XF_CNTX_CFG_3`. Later chunks continue raw lane 1 FSM skip controls after `RAWLANE1_DIG_FSM_SKIP_RX_DCC_RATE_CAL` and cover the remaining generated DCN 3.2 mask namespace. The final per-file research document should merge all chunks before making complete claims about every C20 PHY raw lane, every FSM calibration skip field, or the complete `dcn_3_2_0_sh_mask.h` contract.
