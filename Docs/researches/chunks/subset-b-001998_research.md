# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 168380-170767

## Scope

This chunk is a generated AMDGPU Display Core DCN 3.2.0 register-field shift/mask slice for the C20 PHY `CR3` lane-3 namespace. It contains C preprocessor constants only: `_SHIFT` macros define bit positions, `_MASK` macros define field masks, and `//<REGISTER>` comments group field definitions by hardware register. There are no C functions, structs, enums, branches, loops, locks, memory allocations, persistence APIs, syscalls, or direct MMIO accesses in this range.

The mapped work item is `subset-b-001998`, chunk 70 for this oversized header, covering lines 168380-170767. The chunk contains 2170 `#define` lines, balanced as 1085 `_SHIFT` definitions and 1085 `_MASK` definitions, plus 218 in-range register comments. It starts and ends on chunk boundaries that split register definitions:

- The first in-scope lines are the tail of `C20_PHY_CR3_LANE3_DIG_TX_FIFO_CTL`; the register comment and earlier `TX_FIFO_RD_PTR_START` and `TX_FIFO_BYPASS` shift lines are in the preceding chunk.
- The final in-scope register comment is `C20_PHY_CR3_LANE3_DIG_ANA_XF_RX_ANA_CREG08`, but this chunk includes only its first two shift fields, `RX_ANA_RX_SIGDET_HF_BIAS_SEL` and `RX_ANA_BIAS_CURR_MODE_REG`; the remaining shifts and all masks for that register continue in the next chunk.

## Purpose And Hardware Surface

The parent header supplies bit-layout constants for AMDGPU Display Core code that programs DCN 3.2.0 display PHY registers. Companion generated headers provide register offsets; this `*_sh_mask.h` file provides field positions and masks consumed by AMD display register helpers to compose MMIO writes and decode register reads.

This chunk covers the lane-3 CR3 digital and analog TX/RX control surface, beginning at TX FIFO control tail fields and then moving through TX analog-transfer overrides, RX ASIC-facing controls, RX power/control/calibration/adaptation/statistics, IQ calibration, and RX analog-transfer controls:

- `C20_PHY_CR3_LANE3_DIG_TX_FIFO_CTL` tail fields expose FIFO read-pointer start, FIFO bypass, and reserved mask coverage across the chunk boundary.
- `C20_PHY_CR3_LANE3_DIG_ANA_XF_TX_*` defines 35 TX analog transfer register groups: clock/reset/serializer/data/driver override outputs, termination-code override controls, TX DCC enable/configuration/calibration controls, EQ override/status, TX analog status input/output, and TX analog `CREG00` through `CREG05` banks plus coarse CREG override gates.
- `C20_PHY_CR3_LANE3_DIG_ASIC_RX_*` defines 30 ASIC-facing RX register groups: override inputs, ASIC inputs, ASIC outputs, CDR/VCO and EQ input words, signal-detect overrides, DFE/CTLE/VGA/ATT override values, tap-offset override banks, IQ/bias/AFE controls, and handshake/status bits.
- `C20_PHY_CR3_LANE3_DIG_RX_PWRCTL_*` defines 8 RX power-control groups for P0/P0S/P1/P2 state composition, power-up timing, RX control, and RX status.
- `C20_PHY_CR3_LANE3_DIG_RX_VCOCAL_*`, `RX_CDR_*`, and `RX_DPLL_*` define VCO calibration control/timing/status, clock-data-recovery gains/lock/status, and DPLL frequency/bounds fields.
- `C20_PHY_CR3_LANE3_DIG_RX_ADPTCTL_*` defines 48 adaptation-control groups for ATT/VGA/CTLE/DFE configuration and status, reset controls, slicer and VDAC offset controls, RX DCC offset override values, fast flags, and slicer/search state-machine configuration/status.
- `C20_PHY_CR3_LANE3_DIG_RX_STAT_*` defines 31 RX statistic and pattern-match groups for load values, masks, match patterns, statistic selection, sample counters, statistic counters, shadow counters, stop controls, and calibration-comparison clock control.
- `C20_PHY_CR3_LANE3_DIG_RX_IQC_CTL_*` defines 3 IQ calibration/control groups for reset/adjustment, IQC configuration, and IQC status.
- `C20_PHY_CR3_LANE3_DIG_ANA_XF_RX_*` defines 44 RX analog-transfer groups in this chunk: control and power override outputs, signal-detect calibration, VCO override outputs, RX calibration controls, VDAC/DAC/DCC controls, AFE overrides, scope/slicer/IQ/IQC controls, termination-code controls, RX analog status, AFE override input, and RX analog `CREG00` through the start of `CREG08`.

## Important Definitions

The generated interface follows the standard AMD display register naming pattern:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted bit mask for that same field.
- `//<REGISTER>` comments are the only local grouping metadata; there are no typed declarations or inline helpers.

Important macro families visible in this range include:

- TX analog override outputs: `ANA_XF_TX_OVRD_OUT_0` through `_3` map MPLLA/MPLLB clock enables, TX analog clock/data/serial/reset enables, refgen/VCM/vreg/bleeder controls, data-rate/reference/loopback/RX-detect/VBoost/word-clock controls, and miscellaneous async reset fields. Most fields are paired with an explicit `*_OVRD_EN` bit, so software can either pass through hardware-owned values or force a register-provided value.
- TX termination and DCC controls: `TX_TERM_CODE_OVRD_OUT`, `TX_TERM_CODE_CLK_OVRD_OUT`, `TX_ANA_DCC_EN`, `TX_ANA_DCC_CONFIG`, `TX_ANA_DCC_CAL_*`, and `TX_ANA_DCC_CAL_DATA` provide termination-code values, self-clear disable bits, DCC calibration control selection, DAC range, calibration data, and override enables.
- TX EQ and analog status/configuration: `TX_STAT_EQ_OVRD_*`, `TX_STAT_OUT_*`, `TX_STAT_EQ_OUT_*`, `TX_STAT_IN_0`, and `TX_ANA_CREG00` through `CREG05` cover pre/main/post cursor values, load clocks, link-state and power-state readback, driver selection, ATB/debug controls, vreg settings, power-on controls, DCC enable, and analog miscellaneous configuration.
- RX ASIC override and input fields: `RX_OVRD_IN_0` through `_4`, `RX_OVRD_SIGDET_IN`, `RX_OVRD_VCO_IN`, and `RX_OVRD_EQ_IN_0` through `_11` define forced reset/request/rate/p-state values, adaptation mode and enable bits, DFE bypass, CDR tracking and SSC, RX disable, signal-detect thresholds, VCO config, ATT/VGA/CTLE/DFE/IQ/AFE override values, DFE quadrant tap-1 offsets, and paired override enables.
- RX ASIC pass-through and status fields: `RX_ASIC_IN_0` through `_3`, `RX_CDR_VCO_ASIC_IN`, `RX_EQ_ASIC_IN_0` through `_2`, `RX_ASIC_OUT_0`, and `RX_OVRD_MISC` define non-override ASIC-provided values and readback/handshake bits such as `ACK`, `VALID`, and `ADAPT_STS`.
- RX power-state and timing fields: `RX_PWRCTL_RX_PSTATE_P0`, `P0S`, `P1`, and `P2` define per-state analog bleeder, AFE, clock vreg, div16p5 clock, clock DCC, deserializer, CDR, VCO reset/calibration, continuous calibration, digital clock, DFE, and bypass-slicer enables. `RX_PWRUP_TIME_0` and `_1`, `RX_CTL`, and `RX_STATUS` provide startup delay, reset/rate acknowledgement, and control/status fields.
- RX VCO, CDR, and DPLL fields: `RX_VCOCAL_RX_VCO_CAL_CTRL_*`, `RX_VCOCAL_RX_VCO_CAL_TIME_*`, and `RX_VCOCAL_RX_VCO_STAT_*` cover VCO configuration, continuous calibration, fast mode, code update, timeouts, and calibration readback. `RX_CDR_CDR_CTL_0` through `_4` cover CDR proportional/integral gains, PI mode, lock controls, and timing. `RX_DPLL_FREQ` and `RX_DPLL_FREQ_BOUND_*` expose DPLL frequency values and limits.
- RX adaptation controls and status: `RX_ADPTCTL_ADPT_CFG_0` through `_12`, `RST_ADPT_CFG`, `ADPT_RESET`, `ATT_STATUS`, `VGA_STATUS`, `CTLE_STATUS`, `DFE_TAP1_STATUS` through `DFE_TAP5_STATUS`, `RX_FAST_FLAGS`, and `SSM_*` configure adaptation enable/mode, settling, thresholds, mu values, saturation behavior, reset scopes, fast-settle flags, slicer/search state-machine steps and waits, and done/abort/FSM readback.
- RX offset and slicer fields: `DFE_DATA_*_VDAC_OFST`, `DFE_ERROR_*_VDAC_OFST`, `DFE_BYPASS_*_VDAC_OFST`, `ERROR_SLICER_*_LEVEL`, `RX_SLICER_CTRL_EVEN`, `RX_SLICER_CTRL_ODD`, and `RX_DCC_*_IDAC_OFST` define data/error/bypass/slicer/DCC offsets for even and odd paths, differential and common-mode controls, and explicit override enables for selected DCC offsets.
- RX statistic and IQC fields: `RX_STAT_LD_VAL_1`, `RX_STAT_DATA_MSK`, `RX_STAT_MATCH_CTL*`, `RX_STAT_STAT_CTL*`, `RX_STAT_SMPL_CNT*`, `RX_STAT_STAT_CNT_*`, `RX_STAT_STAT_STOP`, `RX_STAT_*_SHD`, `RX_IQC_CTL_RESET_ADJUST`, `RX_IQC_CTL_CONFIG`, and `RX_IQC_CTL_STAT` define statistic pattern matching, masks, load values, counters, clock/comparison controls, stop behavior, and IQ calibration control/status.
- RX analog-transfer fields: `ANA_XF_RX_CTL_OVRD_OUT`, `PWR_OVRD_OUT_*`, `SIGDET_*_CAL`, `VCO_OVRD_OUT_*`, `RX_CAL_*`, `VDAC_RANGE_SEL`, `DAC_CTRL*`, `RX_SCOPE`, `RX_SLICER_CTRL`, `RX_ANA_IQ`, `RX_ANA_IQC_*`, `RX_ANA_CAL_DAC_CTRL_EN`, `RX_ANA_LOOPBACK_CTRL`, `RX_ANA_AFE_UPDATE_EN`, `RX_ANA_*_SAMP_SEL`, `RX_TERM_CODE_*`, `RX_STAT_OUT_*`, `RX_STAT_IN_0`, `RX_AFE_OVRD_IN_2`, and `RX_ANA_CREG00` through the start of `CREG08` expose low-level analog enable, calibration, measurement, loopback, termination, ATB, vreg, AFE, DFE, signal-detect, and sampler controls.

## Control Flow And State Behavior

There is no executable control flow in this chunk. Runtime behavior appears when AMDGPU Display Core code combines these masks and shifts with generated register addresses and MMIO helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, or lower-level register access wrappers.

Typical runtime flows using these definitions are:

1. DisplayPort or eDP link bring-up selects lane rate, width, reset/request behavior, RX power state, DFE bypass, signal-detect thresholds, and CDR tracking through ASIC RX input or override fields.
2. Power-management paths program RX P0/P0S/P1/P2 enable sets and startup delays, then read `RX_CTL`, `RX_STATUS`, `RX_ASIC_OUT_0`, and analog status fields for acknowledgement and completion.
3. PHY calibration code programs or decodes TX DCC and termination controls, RX VCO calibration, CDR gains, DPLL frequency bounds, RX DCC offsets, IQC controls, AFE/VDAC trims, signal-detect calibration, and analog `CREG` banks.
4. RX adaptation and equalization code configures ATT, VGA, CTLE, DFE taps, thresholds, mu values, reset scope, fast-settle flags, slicer offsets, SSM search controls, and then polls adaptation status and final-code fields.
5. Diagnostics, validation, and lab tooling use statistic counters, pattern matching, LBERT-adjacent FIFO state from the boundary register, CDR/VCO/DPLL readbacks, analog status outputs, IQC status, and signal-detect readbacks to inspect lane health.

The state represented here is hardware register state, not software-owned persistence:

- Persistent programmed state includes override enables and forced values, RX power-state recipes, startup delays, VCO/CDR/DPLL calibration controls, RX adaptation configuration, DFE/slicer/DCC offsets, SSM configuration, statistic control setup, IQC configuration, and TX/RX analog transfer register settings.
- Volatile readback includes RX ASIC `ACK`/`VALID`/`ADAPT_STS`, RX power and reset/rate status, VCO calibration state, CDR status, DPLL frequency readback, adaptation codes and done flags, SSM final code/done/abort/FSM state, statistic/sample counters, IQC status, analog status outputs, signal-detect status, and ATB/measurement fields.
- Sequencing-sensitive fields include reset/request/rate acknowledgement fields, self-clear disable bits, DCC and VCO calibration starts/enables, adaptation resets, SSM start controls, statistic load/start/stop controls, clock/load pulses, update-enable fields, and any `*_OVRD_EN` bit that can transfer ownership from normal hardware or firmware control to a forced software value.

## Dependencies And Integration Points

This chunk depends on generated-name and numeric consistency across the DCN 3.2.0 register header set. It is normally consumed with the matching register-offset header for DCN 3.2.0 C20 PHY registers and the AMD Display Core register access layer. The compiler can catch missing macro names, but incorrect numeric masks or shifts usually compile successfully and surface only as hardware behavior regressions.

Important integration points include:

- AMDGPU Display Core link encoder and PHY code that programs C20 PHY CR3 lane-3 controls during link bring-up, retraining, hotplug, modeset, and low-power transitions.
- DisplayPort/eDP link-training flows that depend on RX adaptation, CDR/VCO/DPLL behavior, signal detect, lane rate, lane width, DFE/CTLE/VGA/ATT equalization, TX analog state, and RX analog readiness.
- Power-management code that moves lanes across P0/P0S/P1/P2 recipes, adjusts startup delays, disables or re-enables analog subblocks, and waits for status/acknowledgement fields during suspend/resume or display idle entry/exit.
- Firmware-assisted or hardware-managed PHY flows that exchange values through `*_ASIC_*`, `*_OVRD_*`, and analog transfer register families.
- Calibration and signal-integrity code that consumes TX DCC/termination, RX VCO, CDR, DPLL, DCC, IQC, AFE, CTLE, VGA, DFE, slicer, SSM, signal-detect, and statistic fields.
- Register dump, debugfs, validation, and manufacturing diagnostics that decode CR3 lane-3 register captures using these exact names, shifts, and masks.

## Risks And Maintenance Notes

- Numeric drift is the primary risk. These macros are a hardware ABI: one bad shift or mask can corrupt RX lane reset, link-rate changes, power-state selection, VCO/CDR/DPLL calibration, adaptation, statistic decoding, or analog trim programming.
- Dense 16-bit registers make overlap and reserved-bit mistakes easy to miss in review. Most bad values compile cleanly and fail only on specific hardware, cable conditions, link rates, or resume/retrain sequences.
- The repeated register-family structure is easy to mis-generate: TX vs RX analog-transfer fields, ASIC input vs override input vs output, P0/P0S/P1/P2 recipes, even vs odd slicer paths, DFE tap numbers, common-mode vs differential DCC offsets, and `CR2` vs `CR3` lane namespaces have similar names but different hardware locations.
- Override-enable fields are high risk because they can bypass normal firmware or hardware ownership. An incorrect `*_OVRD_EN` mask may force stale values, prevent adaptation, leave analog controls in lab/debug mode, or block normal power sequencing.
- Calibration, reset, start, stop, and self-clear related fields are sequencing-sensitive. Wrong masks can cause stuck VCO/DCC/IQC calibration, false done indications, lost statistics, repeated link training, or failure to exit low power.
- Chunk-boundary completeness matters for merged research. `TX_FIFO_CTL` is partial at the start, and `RX_ANA_CREG08` is partial at the end; final per-file reconciliation should merge adjacent chunk reports before claiming complete register-family coverage.

## Test Signals

Useful validation combines generated-header checks, build coverage, and hardware behavior:

- Build AMDGPU Display Core with DCN 3.2 support enabled and confirm consumers of in-scope `C20_PHY_CR3_LANE3_DIG_*` field macros resolve.
- Run generated-register consistency checks that every complete in-range register has paired `_SHIFT` and `_MASK` definitions, masks fit the expected 16-bit register width, and fields do not overlap except where the hardware specification defines reserved coverage.
- Compare numeric shifts and masks against the authoritative DCN 3.2.0 C20 PHY register specification, focusing on override enables, reset/request/rate/status handshakes, P-state recipes, calibration controls, SSM start/done, statistic controls, DCC offsets, and boundary registers split across chunks.
- Exercise DisplayPort/eDP link training and retraining on DCN 3.2 hardware across supported link rates and lane counts; watch for black screens, flicker, link-training failure, repeated retraining, PHY reset loops, or CDR/VCO/DPLL lock instability.
- Validate suspend/resume, hotplug, modeset, display idle entry/exit, and low-power recovery while checking RX P-state programming, power-up timing, reset/rate acknowledgements, and analog enable/readback fields.
- Stress RX adaptation by reading ATT/VGA/CTLE/DFE status, slicer offsets, IQC status, CDR status, DPLL frequency, VCO calibration status, SSM final code, and signal-detect readbacks after rate changes and high-bandwidth modes.
- Validate analog and calibration behavior through register dumps around TX DCC/termination programming, RX VCO/CDR/DPLL programming, RX DCC/IQC/AFE updates, signal-detect calibration, and statistic-counter collection.

## Chunk-Specific Summary

Lines 168380-170767 define generated DCN 3.2.0 C20 PHY CR3 lane-3 shift and mask constants for TX FIFO tail fields, TX analog-transfer control/status, RX ASIC controls, RX power/VCO/CDR/DPLL control, RX adaptation and statistic engines, IQC, and RX analog-transfer controls through the start of `RX_ANA_CREG08`. The content is register metadata rather than executable logic. Correctness depends on exact bit positions and masks, repeated family consistency, careful handling of override and calibration fields, and hardware validation across link training, power sequencing, adaptation, CDR/VCO/DPLL lock, signal detect, IQC/DCC calibration, statistics, and suspend/resume flows.
