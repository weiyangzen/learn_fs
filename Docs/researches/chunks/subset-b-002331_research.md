# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 102482-103385

## Purpose

This chunk is the final slice of AMD's generated DPCS 4.2.0 shift/mask header. It contains no executable C logic; it exports preprocessor constants that describe bit positions and masks for DPCS/RDPCS hardware registers used by AMDGPU display link-encoder code. Runtime code pairs these constants with offsets from `dpcs_4_2_0_offset.h` so register helpers can pack, update, or extract individual MMIO fields safely.

The requested range covers 785 `#define` lines across 115 register comment blocks: 391 `__SHIFT` macros and 414 `_MASK` macros. The extra masks are caused by the artificial chunk boundary, which starts at the tail of `DPCSSYS_CR4_RAWLANEX_DIG_PCS_XF_RX_PCS_IN` masks after that register's shifts appeared in the previous chunk. This range then covers RX PCS input/status fields, ATE and override controls, RX equalization and calibration controls, DPCS micro-FSM controls and monitors, interrupt status/mask/clear fields, PMA crossbar override fields, TX/RX control registers, and the final header guard `#endif`.

Although the path is under a local `ceph-client` source mirror, this header is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or runtime APIs in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a DPCS register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating or preserving that field during read-modify-write operations.

Major macro families in this range:

- `DPCSSYS_CR4_RAWLANEX_DIG_PCS_XF_RX_PCS_IN*`: RX request/rate/width/P-state/low-power/reset state, reference load value, VCO load value, AFE/DFE adaptation enables, CTLE/VGA/attenuation/equalizer tap fields, and continuous adaptation/off-cancellation controls.
- `DPCSSYS_CR4_RAWLANEX_DIG_PCS_XF_RX_OVRD_OUT*`, `RX_PCS_OUT`, `RX_ADAPT_ACK`, `RX_ADAPT_FOM`, and `RX_TX{PRE,MAIN,POST}_DIR`: RX acknowledge, RX clock/valid override output, adaptation acknowledge, figure-of-merit, and transmitter coefficient direction feedback fields.
- `DPCSSYS_CR4_RAWLANEX_DIG_PCS_XF_ATE_*` and related override inputs: automated-test or manufacturing override paths for RX/TX reset/request/data enable, adaptation AFE/DFE enable, rate, width, P-state, low-power detect, loopback, async data, beacon, VBoost, IBoost, master MPLL state, VCO/ref load values, LOS/LFPS threshold, and continuous adaptation/off-cancellation selection.
- `DPCSSYS_CR4_RAWLANEX_DIG_PCS_XF_RX_EQ_*`, `TXRX_TERM_CTRL*`, and `RX_PH2_CAL`: RX equalization override values for AFE gain, attenuation, DFE tap, CTLE boost/pole, delta IQ, TX/RX termination control, and phase-2 calibration request/acknowledge bits.
- `DPCSSYS_CR4_RAWLANEX_DIG_FSM_*`: micro-FSM override control, current memory address, status bits, fast calibration/adaptation bypass controls, common calibration status, fast flag aggregation, CR register/memory locks, TX DCC flags/status, OCLA debug enables, TX EQ update flag, RCAL status, and RX IQ phase offset.
- `DPCSSYS_CR4_RAWLANEX_DIG_IRQ_CTL_*`: RX/TX reset/request/rate/P-state/adaptation/phase-calibration/loopback/DCC interrupt status bits, clear bits, and interrupt masks.
- `DPCSSYS_CR4_RAWLANEX_DIG_PMA_XF_*`: PMA crossbar override inputs/outputs for MPLLA/MPLLB lane enable, supervisor state, TX/RX request/reset/data-enable/asynchronous/loopback controls, PMA acknowledge inputs, lane retune request/acknowledge, MPHY PWM/async/term controls, and RX IQ phase adjust override.
- `DPCSSYS_CR4_RAWLANEX_DIG_TX_CTL_*` and `RX_CTL_*`: TX FSM timing and RX detect allowance by power state, TX clock selection and async beacon wait, DCC continuous status, OCLA visibility, RX control FSM enable, LOS mask count, RX data enable override timing, and RX adaptation/off-cancellation continuous status.

All fields in this slice are 16-bit-style masks within `0x0000FFFFL`, even though the macro values are expressed as long constants. Reserved fields are explicitly named and masked; consumers should preserve them unless hardware documentation says otherwise.

## Control Flow

This header has no runtime control flow. It supplies constants to code that performs the actual sequencing:

1. DCN 3.1-family resource code includes `dpcs_4_2_0_offset.h` and this shift/mask header.
2. Register-list macros such as `DPCS_DCN31_REG_LIST(id)` select DPCS/RDPCS register offsets for each link encoder instance.
3. `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` and `DPCS_DCN31_MASK_SH_LIST(_MASK)` populate the link encoder shift and mask tables.
4. Runtime link-encoder code uses AMD display register helpers such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, and `REG_GET` against those tables while bringing up, training, disabling, or debugging links.

The macros do not encode ordering requirements. Consumers must still sequence PLL and clock enablement, power-state transitions, reset/request handshakes, RX/TX data enablement, calibration/adaptation, DCC, loopback, interrupt clear/mask operations, and suspend/resume restore in the correct hardware order.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed hardware state in the DPCS lane/PCS/PMA interface:

- Link lane state for RX/TX request, reset, acknowledge, rate, width, P-state, low-power detect, clock/data enable, RX valid, lane number, and lane loopback.
- Analog and calibration state for VCO/ref load values, CTLE/VGA/DFE/equalizer settings, IQ phase offset, RX phase-2 calibration, RX adaptation acknowledge/FOM, TX coefficient direction feedback, TX/RX termination, DCC, RCAL, and common MPLL calibration.
- Override state for ATE/manufacturing paths and software-forced PMA/PCS values, including paired value/enable bits throughout the RX, TX, PMA, MPHY, MPLL, and continuous adaptation controls.
- Micro-FSM state for override execution, jump address, command start, break, current memory address, command-ready flag, ALU flags, wait count, CR locks, fast calibration/adaptation flags, and OCLA debug visibility.
- Interrupt state for RX and TX events, interrupt masks, and explicit clear fields.

Persistence is hardware-defined. Configuration and override fields can remain programmed until modeset, link retraining, power gating, suspend/resume, driver reset, or ASIC reset. Status, acknowledge, interrupt, calibration, clear, and monitor fields may be read-only, sticky, self-clearing, write-one-to-clear, or valid only while related clocks and power domains are active. This generated header does not distinguish those access semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated DPCS 4.2.0 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h`, which provides the matching MMIO offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h`, which defines `DPCS_DCN31_REG_LIST` and `DPCS_DCN31_MASK_SH_LIST`.
- DCN 3.1-family resource files that instantiate link encoder register, shift, and mask tables using the DPCS macros, including `dcn31_resource.c`, `dcn314_resource.c`, `dcn315_resource.c`, and `dcn316_resource.c`.

In the inspected tree, `dcn31_resource.c` directly includes `dpcs_4_2_0_offset.h` and `dpcs_4_2_0_sh_mask.h`, then initializes `link_enc_regs`, `le_shift`, and `le_mask` with `DPCS_DCN31_REG_LIST(id)` and `DPCS_DCN31_MASK_SH_LIST(...)`. Later DCN resource files either reuse the same mask-list pattern or comment it out for hardware generations that moved away from this DPCS table shape.

The behavioral integration is display link management: DP/HDMI/USB-C alternate-mode PHY control, lane power and clock control, PLL state, transmitter and receiver data paths, calibration/adaptation, loopback/test paths, and DPCS debug/interrupt handling.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while programming the wrong MMIO bit, corrupting an adjacent field, failing to preserve reserved bits, or silently breaking only one lane state.
- The range is chunk-boundary sensitive. It starts with the last masks for `RX_PCS_IN` while the matching shifts are in the previous chunk, so whole-register consistency checks must merge adjacent chunks.
- Override registers are high risk because many fields use paired value/enable bits. Setting an override value without the enable bit, or leaving an enable bit asserted after test/debug use, can pin RX/TX reset, request, data enable, loopback, MPLL, LOS, or adaptation state.
- Calibration and adaptation fields are timing-sensitive. Incorrect VCO/ref load, CTLE/VGA/DFE, IQ phase, DCC, RCAL, or continuous adaptation controls can cause link training failures, marginal signal integrity, resume-only failures, or rate-specific instability.
- Interrupt and clear fields are side-effect-sensitive. Confusing status, mask, and clear bits can cause missed RX/TX state changes, stuck DCC or loopback interrupts, or interrupt storms.
- PMA/PCS crossbar fields bridge digital control into analog PHY behavior. Wrong PMA override, MPHY PWM/async, MPLL state, retune, or lane enable fields can break DP Alt Mode, USB-C muxing, low-power transitions, or multi-lane link bring-up.
- The header does not encode read-only, write-one-to-clear, sticky, or self-clearing semantics. Any tooling that blindly writes every mask in the range would be unsafe.

## Test Signals

Useful validation combines generated-header checks with hardware behavior:

- Build AMDGPU display support with DCN 3.1, DCN 3.1.4, DCN 3.1.5, and DCN 3.1.6 resource paths enabled. Missing or renamed DPCS shift/mask macros should fail in link encoder table construction.
- Mechanically verify that every field in lines 102482-103385 has the expected `__SHIFT`/`_MASK` pair, allowing the known artificial-boundary exception for `DPCSSYS_CR4_RAWLANEX_DIG_PCS_XF_RX_PCS_IN` masks whose shifts are immediately before this range.
- Diff this chunk against AMD's authoritative DPCS 4.2.0 register database and against nearby generated DPCS/RDPCS headers where compatible field layouts are expected.
- Exercise real DCN 3.1-family hardware across DP and HDMI link bring-up, link retraining, hotplug, suspend/resume, lane-count and link-rate changes, USB-C/DP Alt Mode if available, and low-power state transitions.
- Validate calibration/adaptation paths by checking stable links at high data rates, no repeated training fallback, no clock/data-enable timeouts, and no signal-integrity regressions after resume or mode changes.
- Test interrupt behavior by forcing RX/TX reset/request transitions, adaptation requests, phase calibration, loopback enablement, and DCC on-demand events where supported, then checking that status, mask, and clear handling does not leave stale or storming interrupts.
- Use debug/OCLA and FSM monitor fields to confirm expected FSM state progression, command-ready behavior, calibration completion, and absence of CR lock or ALU/wait-count anomalies.
- Watch kernel logs and display diagnostics for AUX/link-training timeouts, blank display after modeset, high-rate-only failures, DP Alt Mode failures, stuck low-power state, repeated hotplug events, or resume-only display loss.

## Cross-Chunk Notes

Previous chunks cover the beginning of the `DPCSSYS_CR4_RAWLANEX` DPCS namespace and the missing `RX_PCS_IN` shifts for the first masks in this range. This chunk reaches the physical end of `dpcs_4_2_0_sh_mask.h`; there is no later chunk for this file after line 103385. The final per-file research document should merge this tail with earlier chunks before making complete claims about all DPCS 4.2.0 register fields.
