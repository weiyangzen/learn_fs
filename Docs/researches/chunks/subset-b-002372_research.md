# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 83441-85817

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice for display PHY register fields. It contains no executable C logic. Its exported surface is preprocessor metadata that maps hardware register fields to bit positions (`__SHIFT`) and bit masks (`_MASK`) for AMDGPU display register helpers.

The requested range contains 2,132 `#define` entries across 2,377 source lines, plus 243 register/address-block comment markers. It starts at the field definitions for `DPCSSYS_CR3_RAWLANEX_DIG_FSM_RX_IQ_PHASE_OFFSET`, then covers the rest of the visible CR3 raw-lane IRQ, PMA, TX/RX control, and PCS/ATE override groups. It then enters `addressBlock: dpcssys_cr4_rdpcstxcrind`, covering CR4 supervisor digital and analog controls, MPLLA/MPLLB clocking and RTUNE metadata, CR4 lane0 ASIC and TX power/DCC controls, TX clock alignment/LBERT fields, and the beginning of lane0 RX statistic controls through the early shift definitions of `DPCSSYS_CR4_LANE0_DIG_RX_STAT_STAT_CTL0`.

Although the source path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The only interface is generated macro data:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit index of a hardware field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for extracting, composing, or updating that field.

The main register-field families in this chunk are:

- CR3 raw-lane FSM tail: `DPCSSYS_CR3_RAWLANEX_DIG_FSM_RX_IQ_PHASE_OFFSET` exposes the RX IQ phase offset field. The register marker is just before the requested line range, so this chunk starts inside that register group but includes its shift and mask definitions.
- CR3 raw-lane IRQ controls: `DPCSSYS_CR3_RAWLANEX_DIG_IRQ_CTL_*` defines reset-return request, RX reset/request/rate/pstate/adaptation IRQ status bits, matching clear bits, aggregate IRQ masks, TX reset/request IRQ status and clear bits, lane transceiver-mode IRQs, RX phase-2 calibration IRQs, serial loopback IRQs, and DCC on-demand IRQ state.
- CR3 raw-lane PMA cross-interface fields: `PMA_XF_LANE_OVRD_IN/OUT`, `SUP_OVRD_IN`, `SUP_PMA_IN`, `TX_OVRD_OUT`, `TX_PMA_IN`, `RX_OVRD_OUT`, `RX_PMA_IN`, `LANE_RTUNE_CTL`, `SUP_PMA_IN_1`, `MPHY_OVRD_IN/OUT`, and `RX_ADAPT_OVRD_OUT` describe lane and supervisor PMA override values/enables, TX/RX request/reset/data-enable handshakes, PMA ACK inputs, RTUNE controls, MPHY PWM/termination override paths, and RX adaptation override outputs.
- CR3 raw-lane TX/RX local control: `TX_CTL_TX_FSM_CTL`, `TX_CLK_CTL`, `TX_DCC_CONT_STATUS`, `TX_CTL_OCLA`, `TX_CTL_UPCS_OCLA`, `RX_CTL_RX_FSM_CTL`, `RX_LOS_MASK_CTL`, `RX_DATA_EN_OVRD_CTL`, `OFFCAN_CONT_STATUS`, `ADAPT_CONT_STATUS`, and `RX_CTL_UPCS_OCLA` define TX FSM and clock controls, DCC/off-cancel/adaptation continuous-status enables, RX LOS and data-enable override timing, and observation controls.
- CR3 PCS/ATE override controls: `PCS_XF_ATE_RX_OVRD_IN`, `PCS_XF_ATE_TX_OVRD_IN`, `PCS_XF_ATE_TX_OVRD_IN_1`, `PCS_XF_MASTER_MPLL_LOOP`, `PCS_XF_ATE_RX_OVRD_IN_1/2/3`, `PCS_XF_RX_OVRD_OUT_2`, and `PCS_XF_TX_OVRD_IN_2` cover automated-test and forced-lane paths for RX/TX rate, width, pstate, resets, adaptation controls, DETRX/VBOOST/IBOOST, loopback, LOS/LFPS thresholds, VCO/ref load overrides, RX-valid forcing, master MPLL loop selection, and additional TX/RX override outputs.
- CR4 supervisor digital controls: ID-code words, reference-clock overrides, MPLLA/MPLLB divided and HDMI clock overrides, MPLLA/MPLLB fractional-N, SSC, divider, multiplier, enable/reset/power-state, charge-pump, gain-switch, level, ASIC-input, bandgap, prescaler, and supervisor override/output fields.
- CR4 supervisor analog and calibration controls: prescaler, RTUNE, bandgap, switch power measurement, MPLLA/MPLLB miscellaneous/override/ATB/control/reserved fields, MPLL power-control status, timers, calibration, DAC range/output, SSC spread type, clock/reset power-up timers, RTUNE configuration/status/set/stat/code fields, and analog override/status outputs.
- CR4 lane0 ASIC and TX power controls: lane/TX/RX ASIC override inputs/outputs, lane ASIC status, TX pstate definitions for P0/P0s/P1/P2, TX power-up timers, DCC CR-bank address/data, DCC DAC control/range/select/ACK/address, TX clock-alignment controls, and LBERT pattern/error injection control.
- CR4 lane0 RX statistic controls: `RX_STAT_LD_VAL_1`, `RX_STAT_DATA_MSK`, `RX_STAT_MATCH_CTL0`, `RX_STAT_MATCH_CTL1`, and the start of `RX_STAT_STAT_CTL0` define statistic load/start, data mask, pattern matching, correction/statistic source selection, statistic shift selection, RX clock selection, sample-counter mode, and skip-enable fields. The requested range ends before the remaining `STAT_CTL0` shifts and masks.

Most fields are 16-bit register slices with an `L`-suffixed mask value. Some logical values are split across multiple registers, such as MPLL fractional/SSC high and low words, multiword TX power-up timing, and repeated MPLLA/MPLLB analog override/status banks.

## Control Flow

This header has no runtime control flow. It contributes compile-time constants to the AMDGPU display stack:

1. DPCS 4.2.2 register address metadata comes from the companion `dpcs_4_2_2_offset.h` file.
2. This file supplies matching field shifts and masks for those indexed registers.
3. DCN resource and link-encoder code token-pastes register, shift, and mask names into register tables.
4. Runtime display code uses those tables through AMD register helper macros such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.
5. Hardware and firmware sequencing for PHY reset, clock selection, PLL programming, pstate changes, lane power, AUX/ATE forcing, RX adaptation, RX statistics, and analog calibration lives outside this generated header.

The macro names describe field location only. They do not encode access type, reset value, polling order, write-one-to-clear behavior, self-clearing behavior, sticky status behavior, clock-domain restrictions, power-domain validity, or reserved-bit policy.

## State And Persistence Behavior

This chunk stores no software state and persists nothing itself. It names hardware-visible state in CR3 and CR4 DPCS/PHY registers:

- CR3 IRQ state includes latched RX/TX reset and request events, RX rate and pstate events, RX adaptation request/disable events, lane transceiver-mode events, phase-2 calibration events, serial loopback events, DCC on-demand events, clear registers, reset-return request bits, and interrupt-mask registers.
- CR3 PMA/PCS override state includes forced request/reset/data-enable values, override-enable bits, TX/RX loopback state, PMA/RTUNE ACK state, MPHY PWM and termination controls, RX phase-map adaptation override, ATE rate/width/pstate forcing, DETRX/VBOOST/IBOOST forcing, LOS/LFPS and adaptation controls, VCO/ref-load overrides, master MPLL loop enables, and RX-valid forcing.
- CR3 TX/RX control state includes TX FSM enable/timing, TX clock enable/source selection, RXDET permission by pstate, DCC/off-cancel/adaptation continuous-status enables, RX LOS masking, RX data-enable override timing, and OCLA/UPCS observation gates.
- CR4 supervisor state includes MPLLA/MPLLB reference/divided/HDMI clock paths, fractional-N and SSC parameters, dividers, multipliers, enable/reset/power state, charge-pump and gain-switch tuning, bandgap and prescaler controls, RTUNE set/stat/calibration state, and clock/reset power-up timing.
- CR4 analog state includes MPLLA/MPLLB analog override, ATB, control, reserved, power-control, timer, calibration, DAC, and status readback fields.
- CR4 lane0 state includes ASIC override/in/out buses, TX pstate and power-up timing, DCC CR-bank and DAC access, TX clock alignment, LBERT control, and RX statistic matching/source-selection state.

Persistence is hardware-defined. Configuration fields generally remain until link reprogramming, modeset, suspend/resume, power-gating, GPU reset, ASIC reset, firmware ownership changes, or explicit driver reinitialization changes them. Status, ACK, IRQ, calibration, statistic-done, and handshake fields may be transient, latched, write-one-to-clear, self-clearing, sampled only under an active clock domain, or invalid while PHY power is gated. This generated header does not distinguish those cases.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.2 register database and its companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies matching `ix...` offsets. In that file, `ixDPCSSYS_CR3_RAWLANEX_DIG_IRQ_CTL_RESET_RTN_REQ` is mapped at `0xe040`, the CR4 block starts with `ixDPCSSYS_CR4_SUP_DIG_IDCODE_LO` at `0x0000`, and the end-boundary register `ixDPCSSYS_CR4_LANE0_DIG_RX_STAT_STAT_CTL0` is mapped at `0x1084`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` includes the DPCS 4.2.2 offset and shift/mask headers when constructing DCN 3.1.5 display resources.
- DIO/HPO link encoder and display core register-list code consume these macros indirectly through generated register, shift, and mask tables.
- Low-level display link, PHY, PLL, lane-training, hotplug/AUX/DDC, diagnostics, hardware sequencing, and reset/power-management paths rely on these field locations when programming or decoding DPCS registers.

Behaviorally, this chunk sits below user-facing display code. It provides the bitfield layer for operations such as masking and clearing lane IRQs, forcing or observing PMA/PCS handshakes, programming MPLL and SSC parameters, controlling PHY power and clocking, running RTUNE and DCC calibration, configuring TX pstate timing, collecting RX statistics, and driving test/diagnostic override paths.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while updating the wrong field, corrupting adjacent reserved bits, or decoding status incorrectly.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the companion offset header, firmware assumptions, and silicon documentation.
- The chunk starts inside `DPCSSYS_CR3_RAWLANEX_DIG_FSM_RX_IQ_PHASE_OFFSET`; the register comment is immediately before the requested range. Whole-register analysis should reconcile the preceding chunk for the marker and local context.
- The chunk ends inside `DPCSSYS_CR4_LANE0_DIG_RX_STAT_STAT_CTL0`; later shifts and all masks for that register continue after line 85817. Consumers of this research must not treat this chunk as owning the whole RX statistic control register.
- CR3 and CR4 layouts are repetitive across lanes, PLLs, and analog banks. A generator or copy error can affect only one lane, MPLL, or transmitter path while neighboring definitions look correct.
- IRQ status, clear, and mask fields use similar names but have different hardware semantics. Mixing them can drop events, leave stale events latched, or cause repeated interrupts.
- Override-enable and override-value pairs must be handled carefully. Enabling an override with a stale value, or setting a value bit without the corresponding enable bit, can force unexpected PHY state.
- PLL, SSC, divider, multiplier, charge-pump, gain-switch, bandgap, power-up timer, RTUNE, DCC, and TX pstate fields are timing- and silicon-sensitive. Incorrect field definitions can cause link-training failures, unstable clocks, blank displays, excessive bit errors, calibration timeouts, or bad resume behavior.
- Status, ACK, statistic-done, calibration-result, and IRQ fields may be read-only, latched, or dependent on active power and clock domains. Treating them like ordinary writable configuration fields can hide real hardware state or clear diagnostics.
- RX statistic and LBERT fields are diagnostic/test-oriented. Incorrect masks can make validation tools report misleading pass/fail results even when normal link operation appears unchanged.
- Reserved masks are emitted throughout the chunk. Generic register writes must preserve reserved bits unless the hardware programming guide explicitly requires a value.

## Test Signals

Useful validation combines generated-header checks with display hardware behavior:

- Build or preprocess AMDGPU display support for DCN 3.1.5 with `dcn315_resource.c`, `dpcs_4_2_2_offset.h`, and `dpcs_4_2_2_sh_mask.h`. Missing, renamed, or malformed macros should fail where generated register, shift, and mask tables are initialized.
- Mechanically verify that complete fields in this range have paired `__SHIFT` and `_MASK` definitions, allowing the known boundary exceptions for `DPCSSYS_CR3_RAWLANEX_DIG_FSM_RX_IQ_PHASE_OFFSET` at the start and `DPCSSYS_CR4_LANE0_DIG_RX_STAT_STAT_CTL0` at the end.
- Cross-check every complete register group against `dpcs_4_2_2_offset.h` and AMD's source register database.
- Diff CR3/CR4 replicated lane, MPLLA/MPLLB, and analog-bank field layouts against neighboring generated DPCS versions where the hardware specification expects matching fields.
- Exercise DisplayPort and HDMI link bring-up on ports mapped to the affected DPCS/UNIPHY instances. Expected signals are stable link training, correct PLL lock behavior, completed RX adaptation, expected lane request/ACK transitions, and no recurring RX/TX calibration or IRQ failures.
- Run modeset, stream disable/enable, hotplug, suspend/resume, GPU reset, and power-gating tests to catch stale pstate, clock, reset, MPLL, analog override, RTUNE, and DCC state.
- Use register dumps or PHY debug traces during failures to confirm that IRQ clear/mask bits, PMA/PCS overrides, MPLLA/MPLLB settings, RTUNE/DCC status, TX pstate timers, RX statistic match controls, and analog override/status fields decode as expected.
- On validation hardware, run available OCLA/UPCS OCLA, LBERT, RX statistic, ATE, DCC on-demand, RTUNE, and phase-2 calibration paths to verify diagnostic counters, sample-done bits, ACK/status fields, and forced override paths use the intended field positions.

## Cross-Chunk Notes

The previous chunk owns the marker and surrounding context for `DPCSSYS_CR3_RAWLANEX_DIG_FSM_RX_IQ_PHASE_OFFSET`. This chunk owns that register's visible field definitions, the CR3 raw-lane IRQ/PMA/TX/RX/ATE tail, the CR4 supervisor and analog/control sections, and the CR4 lane0 TX power/statistic lead-in through early `RX_STAT_STAT_CTL0` shifts. The next chunk should finish `DPCSSYS_CR4_LANE0_DIG_RX_STAT_STAT_CTL0` and continue the remaining CR4 lane0 RX statistic, analog TX/RX, and later lane blocks. The final per-file report should reconcile these artificial chunk boundaries before making whole-file claims about DPCS 4.2.2 CR3/CR4 coverage.
