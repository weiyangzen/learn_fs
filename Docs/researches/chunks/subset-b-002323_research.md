# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 83444-85815

## Purpose

This chunk is a generated AMD DPCS 4.2.0 shift/mask header slice for display PHY and lane-control register fields. It contains no executable logic; its exported surface is preprocessor metadata that maps hardware register fields to bit positions (`__SHIFT`) and bit masks (`_MASK`) for AMDGPU display register helpers.

The requested range contains 2,136 `#define` entries over 2,372 source lines and 234 register comment markers. It begins inside `DPCSSYS_CR3_RAWLANEX_DIG_PMA_XF_TX_OVRD_OUT`, after several of that register's shift definitions have already appeared in the previous chunk, and then covers the rest of the CR3 raw-lane PMA/PCS, TX/RX control, ATE override, and MPLL-loop definitions. It then enters `addressBlock: dpcssys_cr4_rdpcstxcrind`, covering CR4 supervisor, MPLL, bandgap, RTUNE, ASIC interface, lane0 TX power/DCC, RX statistics, and lane0 analog TX equalization/status fields through `DPCSSYS_CR4_LANE0_DIG_ANA_STATUS_0`.

Although the source path is under a local `ceph-client` tree, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or direct MMIO operations in this range. The only public interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit index of a hardware field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for extracting or updating that field.

The main register-field families in this chunk are:

- CR3 raw-lane PMA cross-interface controls: TX/RX override values and enable bits, PMA request/reset/data-enable handshakes, PMA ACK inputs, lane TX-to-RX and RX-to-TX loopback enables, RTUNE request/ACK, MPHY PWM/term/async overrides, RX adaptation phase-map override, and PMA data/clock enable controls.
- CR3 raw-lane TX/RX control: TX FSM timing and receive-detect permission in P-states, TX clock enables/selectors, DCC continuous-status enables, OCLA observation controls, RX FSM enable/rate-change controls, loss-of-signal mask counters, RX data-enable override counters, off-cancel/adaptation continuous-status flags, and UPCS OCLA data/clock gates.
- CR3 PCS/ATE override controls: RX/TX rate, width, pstate, reset, beacon, async, data-enable, DETRX, VBOOST, IBOOST, loopback, LOS/LFPS threshold, adaptation/off-cancel continuous control, VCO/ref load overrides, RX-valid override, master MPLLA/MPLLB loop enables, and TX/RX override fields used for automated test or forced-lane operation.
- CR4 supervisor digital controls: ID-code registers, reference clock and MPLLA/MPLLB divided/HDMI clock override inputs, MPLLA/MPLLB fractional-N, SSC, divider, multiplier, enable, reset, prescaler, charge-pump, gain-switch, level, ASIC-input, bandgap, and supervisor override/output fields.
- CR4 supervisor analog controls: prescaler, RTUNE, bandgap, switch power measurement, MPLLA/MPLLB miscellaneous, override, ATB, control, and reserved analog fields, plus digital MPLL power-control status, timers, calibration, DAC range/output, SSC spread type, clock/reset power-up timers, RTUNE configuration/status/set/stat/code fields, and analog override/status outputs.
- CR4 lane0 ASIC interface and TX power controls: lane/TX/RX ASIC override inputs/outputs, lane ASIC status, TX pstate definitions for P0/P0s/P1/P2, TX power-up timers, DCC CR bank address/data, DCC DAC control/range/select/ACK/address, TX clock alignment, and LBERT control.
- CR4 lane0 RX statistics controls: load/data masks, pattern match and mask registers, statistic control enables, sample counters, statistic counters 0-6, calibration comparison clock control, second match-register set, statistic-stop control, valid-loss clearing, pause/clock enable, data-delay, and sample-done indicators.
- CR4 lane0 analog TX controls and status: analog TX clock/data/refgen/VCM/word-clock/MPLL/reset/serial/rate/RX-detect override bits, TX termination code and drive-source override, termination clock self-clear control, TX equalization load/leg-pull/mux/pre/post/direction fields, and status bits for clock-shift ACK, RXDET results, loopback, RX calibration, scope data, TX DCC calibration, and EQ mux readback.

Most fields are 16-bit register slices with paired shift and mask definitions. Some fields span multiple registers by suffix, such as `MPLLA_FRACN_QUOT_31_16`/`15_0`, `MPLLA_SSC_PEAK_31_16`/`15_0`, and TX equalization leg-pull fields split across `_0` through `_5`.

## Control Flow

This header has no runtime control flow. It contributes compile-time constants to the AMDGPU display stack:

1. DPCS 4.2.0 register address metadata comes from the companion `dpcs_4_2_0_offset.h` file.
2. This file supplies matching field shifts and masks for those registers.
3. DCN resource and link-encoder code token-pastes register, shift, and mask names into register tables.
4. Runtime display code uses those tables through AMD register helper macros such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.
5. Hardware sequencing for PHY reset, clock selection, PLL programming, pstate changes, lane power, AUX/ATE forcing, RX adaptation, statistics collection, and analog calibration lives outside this generated header.

The macro names describe field location only. They do not encode access semantics such as read-only status, write-one-to-clear behavior, self-clearing bits, sticky bits, reserved-bit policy, or required ordering between writes.

## State And Persistence Behavior

This chunk stores no software state and persists nothing on its own. It names hardware-visible state in CR3 and CR4 DPCS/PHY registers:

- CR3 PMA/PCS override state includes forced request/reset/data-enable values, override-enable bits, TX/RX loopback state, PMA/RTUNE ACK status, MPHY PWM and termination control, RX phase-map adaptation override, rate/width/pstate forcing, DETRX/VBOOST/IBOOST forcing, LOS/LFPS/adaptation controls, VCO/ref load overrides, and RX-valid forcing.
- CR3 TX/RX control state includes FSM enable/timing bits, TX clock enable/source selection, RXDET permission by power state, DCC/off-cancel/adaptation continuous-status enables, RX LOS masking, and OCLA/UPCS observation gates.
- CR4 supervisor state includes MPLLA/MPLLB clocking, SSC, fractional-N, dividers, multipliers, enable/reset/power state, charge-pump/gain-switch tuning, bandgap and prescaler controls, RTUNE set/stat/calibration state, and power-up/timing thresholds.
- CR4 lane0 state includes ASIC override/in/out buses, TX pstate and power-up timing, DCC CR bank access, DAC tuning and ACK state, TX clock alignment, LBERT control, RX statistic match/counter/sample state, and analog TX override/equalization/termination/status readbacks.

Persistence is hardware-defined. Configuration fields generally remain until link reprogramming, modeset, suspend/resume, power-gating, GPU reset, ASIC reset, or explicit driver reinitialization changes them. Status and handshake fields may be transient, latched, clear-on-write, self-clearing, sampled only under an active clock domain, or invalid while PHY power is gated. The header itself does not distinguish these cases.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.0 register database and its companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h` provides matching `ix...` register offsets for the shift/mask names in this file.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` includes the DPCS 4.2.0 offset and shift/mask headers when initializing DCN 3.1 display resources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h` defines DPCS/DCN31 register-list and mask/shift-list macros that consume these generated names.
- Low-level display link, PHY, PLL, lane-training, hotplug/AUX/DDC, diagnostics, and hardware-sequencing code consumes the initialized tables indirectly.

The fields in this chunk sit below the higher-level display pipeline. They provide locations for operations such as forcing or observing lane handshakes, programming MPLL and SSC parameters, controlling PHY power and clocking, running RTUNE and DCC calibration, collecting RX statistics, applying TX equalization/termination settings, and reading analog TX/RX status.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong mask or shift can compile cleanly while causing the driver to update the wrong field or corrupt adjacent reserved bits.
- The chunk starts mid-register: the first visible lines are late shift definitions for `DPCSSYS_CR3_RAWLANEX_DIG_PMA_XF_TX_OVRD_OUT`; earlier shifts and the register comment are in the preceding chunk. Whole-register analysis must reconcile both chunks.
- CR3 and CR4 raw-lane/register-bank layouts are highly repetitive. Copy/generator errors can affect only one lane, PLL, or transmitter path, producing port-specific failures that are hard to reproduce.
- PLL, SSC, divider, multiplier, charge-pump, gain-switch, bandgap, power-up timer, RTUNE, DCC, and analog equalization fields are timing- and silicon-sensitive. Incorrect field definitions can cause link-training failures, unstable clocks, blank displays, excessive bit errors, bad resume behavior, or calibration timeouts.
- Override-enable and override-value pairs must be handled carefully. Setting a value bit without the corresponding enable bit, or enabling an override with a stale value, can force unexpected PHY state.
- Status, ACK, IRQ-like, statistic-done, and calibration-result fields may be read-only, latched, or dependent on active power/clock domains. Treating them like ordinary writable configuration fields can hide real hardware state or clear diagnostics.
- RX statistic and LBERT fields are diagnostic/test-oriented. Incorrect masks can make hardware validation appear to pass or fail incorrectly even when link operation is otherwise unchanged.
- Reserved fields are numerous. Generic register writes must preserve reserved bits unless hardware documentation explicitly requires programming them.
- Manual edits to this generated header risk divergence from AMD's authoritative register source, the offset header, firmware assumptions, and silicon documentation.

## Test Signals

Useful validation should combine generated-header checks and hardware behavior:

- Build AMDGPU display support with DCN 3.1 enabled. Missing or renamed macros should fail where DPCS 4.2.0 register, shift, and mask tables are assembled.
- Mechanically verify that complete fields in this range have paired `__SHIFT` and `_MASK` definitions, allowing for the known starting boundary where `DPCSSYS_CR3_RAWLANEX_DIG_PMA_XF_TX_OVRD_OUT` begins before line 83444.
- Cross-check the register names in this chunk against `dpcs_4_2_0_offset.h` and AMD's source register database.
- Diff CR3/CR4 replicated lane and PLL field layouts against neighboring generated DPCS/DCN headers where the hardware specification expects matching fields.
- Exercise DisplayPort and HDMI link bring-up on ports mapped to the affected DPCS/UNIPHY instances. Watch for stable link training, correct PLL lock behavior, expected lane request/ACK transitions, and no recurring RX/TX calibration failures.
- Run modeset, stream disable/enable, hotplug, suspend/resume, GPU reset, and power-gating tests to catch stale pstate, clock, reset, MPLL, and analog override state.
- Use register dumps during failures to confirm that PMA/PCS overrides, MPLLA/MPLLB settings, RTUNE/DCC status, TX pstate timers, RX statistics, and analog TX status fields decode as expected.
- On validation hardware, run RX statistic/LBERT/ATE paths when available to verify that diagnostic counters, pattern matches, sample-done bits, and forced override paths use the intended field positions.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DPCSSYS_CR3_RAWLANEX_DIG_PMA_XF_TX_OVRD_OUT`, including the register marker and the first shift definitions. This chunk owns the remaining masks for that register, the rest of the visible CR3 raw-lane PMA/PCS/TX/RX/ATE block, and the CR4 supervisor plus lane0 control/status section through the complete `DPCSSYS_CR4_LANE0_DIG_ANA_STATUS_0` register. The next chunk begins at `DPCSSYS_CR4_LANE0_DIG_ANA_TX_DCC_DAC_OVRD_OUT`, so whole-file reconciliation should connect this document with adjacent chunks before making final claims about complete CR3/CR4 lane coverage.
