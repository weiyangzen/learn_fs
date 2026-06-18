# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 200000-202389

## Scope

This chunk is a generated DCN 3.2.0 register-field shift/mask slice for the AMD display C20 PHY `CR4` lane namespace. It contains C preprocessor constants only: each definition is a `_SHIFT` or `_MASK` macro for a named hardware register field, grouped by `//<REGISTER>` comments. There are no functions, structs, enums, branches, loops, locks, memory allocations, direct MMIO operations, or persistence code in this range.

The line range starts in the middle of `C20_PHY_CR4_LANE2_DIG_RX_ADPTCTL_CTLE_STATUS`: the `CTLE_BOOST_ADPT_CODE`, `CTLE_POLE_ADPT_CODE`, and `ASM1_DONE` shift lines are immediately before this chunk, while their masks and the reserved-field shift/mask are inside it. The range ends in the middle of `C20_PHY_CR4_LANE3_DIG_ASIC_RX_OVRD_MISC`: only `RX_MISC_OVRD_VAL__SHIFT` and `RX_MISC_OVRD_EN__SHIFT` are in this chunk, with the reserved shift and all masks following after line 202389. Final file-level documentation must merge adjacent chunks before treating those boundary registers as complete.

## Purpose And Hardware Surface

This header supplies bit-layout constants used by AMDGPU Display Core register helpers to compose writes and decode reads for DCN 3.2.0 hardware registers. Companion generated headers provide register offsets; this `*_sh_mask.h` file provides the bit positions and masks used with those offsets.

The hardware surface in this chunk covers the tail of C20 PHY CR4 lane 2 RX adaptation and analog-RX controls, then the beginning and most of C20 PHY CR4 lane 3 ASIC/TX/RX controls:

- `C20_PHY_CR4_LANE2_DIG_RX_ADPTCTL_*` defines RX adaptation readbacks and controls for CTLE and DFE tap status, DFE VDAC offsets, slicer controls, error/bypass VDAC offsets, adaptation reset, CTLE/DFE saturation settings, RX DCC IDAC offsets, fast settle flags, SSM scan controls, and final SSM code readbacks.
- `C20_PHY_CR4_LANE2_DIG_RX_STAT_*` defines lane-2 RX statistic/match/sample/counter controls: data masks, match controls, statistic control words, sample counters, status counters, calibration compare clock controls, stop controls, and extended load values.
- `C20_PHY_CR4_LANE2_DIG_RX_IQC_CTL_*` and `C20_PHY_CR4_LANE2_DIG_ANA_XF_RX_*` define IQ calibration reset/config/status, analog RX override outputs, power overrides, signal-detect calibration, VCO overrides, RX calibration control, VDAC range, DAC controls, AFE overrides, scope/slicer/IQ controls, loopback, update enables, sampler selection, termination overrides, analog status in/out, and analog control registers `ANA_CREG00` through `ANA_CREG11`.
- `C20_PHY_CR4_LANE3_DIG_ASIC_*` starts lane-3 ASIC override and ASIC input/output mappings for lane-level, TX, and RX control surfaces, including reset/invert/data-enable/request/low-power/pstate/rate/width/divider and CDR/signal-detect/equalization fields.
- `C20_PHY_CR4_LANE3_DIG_TX_PWRCTL_*`, `TX_DCC_CTL_*`, `TX_STAT_*`, `TX_CLK_ALIGN_*`, `TX_LBERT_*`, and `TX_FIFO_CTL` define lane-3 TX power-state presets, power-up timing, TX control/status, TX DCC offset/status, TX statistic counters, clock alignment, loopback-BERT pattern/control fields, TX level calculation status, and FIFO controls.
- `C20_PHY_CR4_LANE3_DIG_ANA_XF_TX_*` defines lane-3 analog TX override outputs, termination overrides, TX analog DCC controls, calibration override/compare/control enables, calibration range/data, TX equalization override/status readbacks, TX analog status in/out, and analog control registers `ANA_CREG00` through `ANA_CREG05`.
- `C20_PHY_CR4_LANE3_DIG_ASIC_RX_*` defines lane-3 RX override input/output, raw ASIC input, VCO/CDR input, equalization input, signal-detect override, and RX status output fields. The last register in scope, `RX_OVRD_MISC`, is incomplete in this chunk.

## Important Definitions

The generated interface follows the AMD display register convention:

- `<REGISTER>__<FIELD>__SHIFT` gives a field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in register value position.
- `//<REGISTER>` comments mark the register whose field definitions follow.

Important macro families in this chunk include:

- RX adaptation status and trims for lane 2: `C20_PHY_CR4_LANE2_DIG_RX_ADPTCTL_CTLE_STATUS`, `DFE_TAP1_STATUS` through `DFE_TAP5_STATUS`, `DFE_DATA_*_VDAC_OFST`, `DFE_ERROR_*_VDAC_OFST`, `DFE_BYPASS_*_VDAC_OFST`, `ERROR_SLICER_*_LEVEL`, and `RX_SLICER_CTRL_*`. These decode CTLE/DFE adaptation results, ASM completion bits, slicer levels, and even/odd high/low VDAC trim values.
- RX adaptation control and DCC fields for lane 2: `ADPT_RESET`, `ADPT_CFG_10`, `ADPT_CFG_11`, `ADPT_CFG_12`, `RX_DCC_PHASE_*_IDAC_OFST`, `RX_DCC_DATA_*_IDAC_OFST`, `RX_DCC_BYPASS_*_IDAC_OFST`, and `RX_FAST_FLAGS`. These drive adaptation reset, CTLE/DFE saturation limits, DCC offset override values/enables, and fast AFE/DFE or SSM DAC settle behavior.
- SSM and RX statistics for lane 2: `SSM_SSM_CFG_0` through `SSM_SSM_CFG_4`, `SSM_FINAL_CODE`, `RX_STAT_LD_VAL_1`, `RX_STAT_DATA_MSK`, `RX_STAT_MATCH_CTL0` through `MATCH_CTL6`, `RX_STAT_STAT_CTL0` through `STAT_CTL2`, `RX_STAT_SMPL_CNT*`, `RX_STAT_STAT_CNT_*`, `CAL_COMP_CLK_CTL`, `STAT_STOP`, `STAT_CNT_N_SHD`, and extended load-value registers. These support hardware scan/statistic collection and counter readback.
- IQ and analog RX control for lane 2: `RX_IQC_CTL_RESET_ADJUST`, `RX_IQC_CTL_CONFIG`, `RX_IQC_CTL_STAT`, and the `DIG_ANA_XF_RX_*` family. Fields include analog override values/enables for reset, VCO, DFE, DCC, AFE, slicer, IQ, loopback, termination, power, signal-detect, calibration, and analog control-register pages.
- Lane-3 ASIC TX override and raw input/output fields: `C20_PHY_CR4_LANE3_DIG_ASIC_LANE_OVRD_IN`, `TX_OVRD_IN_0` through `TX_OVRD_IN_5`, `TX_OVRD_OUT`, `LANE_ASIC_IN`, `TX_ASIC_IN_0` through `TX_ASIC_IN_3`, `TX_ASIC_OUT`, and `TX_OVRD_MISC`. These expose lane-level and TX override enables/values for clock-ready, reset, invert, data enable, request, low-power, pstate, rate, width, PLL enable, de-emphasis, boost, VREG, termination, pattern generator, and PRBS controls.
- Lane-3 TX power, calibration, debug, and analog controls: `TX_PWRCTL_TX_PSTATE_P0`, `P0S`, `P1`, `P2`, `TX_PWRUP_TIME_*`, `TX_CTL`, `TX_STATUS`, `TX_DCC_CTL_*`, `TX_STAT_*`, `TX_CLK_ALIGN_*`, `TX_LBERT_*`, `TX_LVL_CALC_STAT`, `TX_FIFO_CTL`, and `DIG_ANA_XF_TX_*`. These fields define TX state presets, timing counters, DCC IDAC offset overrides, statistics, clock alignment, loopback-BERT patterns, FIFO status/control, analog TX override outputs, DCC calibration controls, status equalization readbacks, and TX analog control registers.
- Lane-3 ASIC RX override and raw input/output fields: `RX_OVRD_IN_0` through `RX_OVRD_IN_4`, `RX_OVRD_SIGDET_IN`, `RX_OVRD_VCO_IN`, `RX_OVRD_EQ_IN_0` through `RX_OVRD_EQ_IN_4`, `RX_OVRD_OUT_0`, `RX_ASIC_IN_0` through `RX_ASIC_IN_3`, `RX_CDR_VCO_ASIC_IN`, `RX_EQ_ASIC_IN_0` through `RX_EQ_ASIC_IN_2`, `RX_ASIC_OUT_0`, and the beginning of `RX_OVRD_MISC`. These fields cover RX reset/invert/data-enable/request/low-power/pstate/rate/width, DFE bypass, CDR tracking/SSC, signal detect, VCO config, equalizer ATT/VGA/CTLE/AFE/DFE settings, override acknowledge/valid/status, and RX misc override values.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior emerges when DCN 3.2 display code uses these macros with generated register offsets and helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, or lower-level MMIO wrappers.

Typical runtime flows using this slice are:

1. RX adaptation and calibration code decodes lane-2 CTLE/DFE tap status, applies DCC/VDAC/IDAC trim overrides, resets adaptation logic, configures SSM scans, and reads statistic counters.
2. Analog RX bring-up or debug paths program lane-2 analog override enables/values, signal-detect calibration, VCO/DAC/AFE/slicer/IQ settings, loopback, sampler selection, termination overrides, and analog control registers.
3. Lane-3 TX bring-up configures ASIC-visible TX inputs or overrides, selects TX power-state presets, sequences power-up timers, monitors TX status, programs DCC offsets, checks clock alignment, drives LBERT/debug patterns, and reads FIFO or level-calculation status.
4. Lane-3 analog TX calibration/debug paths program analog TX override outputs, DCC calibration controls, termination overrides, and analog `CREG` values, then read equalization and analog status outputs.
5. Lane-3 RX bring-up/training configures ASIC-visible RX inputs, CDR/VCO/signal-detect/equalizer overrides, DFE bypass and CDR tracking, then reads RX acknowledge/valid/adaptation status and raw equalization inputs.

The state represented here is hardware register state:

- Persistent programmed state includes override enables and values, adaptation reset/configuration, DCC/VDAC/IDAC offset controls, fast-settle flags, SSM/statistic controls, analog RX/TX control-register values, TX power-state presets, TX power-up timing, LBERT patterns, FIFO controls, lane transceiver inputs, RX/TX pstate/rate/width settings, and CDR/equalization override values.
- Volatile readback includes adaptation result codes, ASM done bits, SSM final codes, statistic counters, IQ calibration status, analog status outputs, TX/RX ASIC out acknowledge/valid/status fields, TX status, DCC status, clock-alignment status, level-calculation status, FIFO status, and signal-detect/equalization readbacks.
- Sequencing-sensitive fields include reset/disable/request overrides, adaptation reset, fast-settle flags, SSM start controls, statistic stop controls, DCC calibration controls, power-state preset and power-up timer fields, clock-alignment controls, LBERT controls, and override-enable bits that can disconnect normal hardware or firmware control paths.

## Dependencies And Integration Points

This chunk depends on exact numeric consistency with the DCN 3.2.0 C20 PHY register specification and with companion generated offset headers. The header is included by DCN 3.2 display and support code in the AMDGPU tree, including DMUB DCN32 code, IRQ/GPIO support, clock/resource management, and related GPU initialization paths.

Important integration points include:

- AMDGPU Display Core link encoder, PHY, and DisplayPort/HDMI link-training paths that configure CR4 lane RX/TX controls, power states, adaptation, DCC calibration, CDR, signal detect, and equalization.
- DMUB or firmware-assisted display flows that rely on ASIC input/output and override registers to exchange lane state, request/acknowledge status, adaptation status, and training controls.
- PHY calibration and lab/debug tooling that dumps lane-2 RX adaptation/analog state and lane-3 TX/RX analog or ASIC state using these masks.
- Power-management, suspend/resume, hotplug, and link-retraining paths that may reapply TX power-state presets, restore analog override state, re-run DCC/IQ/adaptation sequences, or validate RX/TX status fields.
- Register-generation infrastructure and hardware-spec synchronization. Compile-time consumers catch missing macro names, but incorrect shift or mask values can compile successfully and only fail on specific DCN 3.2 hardware paths.

## Risks And Maintenance Notes

- Numeric drift is the highest risk. These macros are a hardware ABI; an incorrect shift or mask can program the wrong PHY field and cause display link failures, marginal signal integrity, bad calibration, or intermittent resume/retrain failures.
- This chunk is dominated by repeated lane, TX/RX, DCC, analog, override, status, and reserved-field patterns. Copy/paste or generator errors can be hard to see by inspection, especially where lane 2 and lane 3 families are structurally similar but not identical.
- Many registers are 16-bit packed fields with adjacent enables and values. A one-bit error in an override enable, reset, pstate, rate, DFE tap, CDR, signal-detect, or DCC field can silently change PHY sequencing.
- Reserved masks matter. Consumers that write register fields through shared helpers depend on reserved bits staying untouched or decoded correctly; bad reserved masks may write undocumented hardware bits.
- Boundary incompleteness matters for this chunk. `CTLE_STATUS` begins before line 200000 and `RX_OVRD_MISC` continues after line 202389, so adjacent chunk reconciliation is required before deriving complete register coverage.
- Generated headers are usually not hand-maintained. Manual edits should be avoided unless they are part of a synchronized register-header refresh validated against the hardware source data.

## Test Signals

Useful validation should combine static generated-header checks, builds, and hardware behavior:

- Build AMDGPU with DCN 3.2 support and confirm all referenced `C20_PHY_CR4_LANE2` and `C20_PHY_CR4_LANE3` field macros resolve for display, DMUB, IRQ/GPIO, clock, resource, and related users.
- Run generated-register consistency checks that each complete register has matching `_SHIFT` and `_MASK` definitions, fields fit within the expected register width, masks match shifts, and fields do not overlap unexpectedly.
- Compare the line-range macros against the authoritative DCN 3.2.0 C20 PHY register data, focusing on adaptation status, DCC/VDAC/IDAC offsets, SSM/statistic counters, analog `CREG` fields, TX pstate/timing, TX/RX ASIC override fields, CDR/signal-detect, and equalizer fields.
- Exercise link training, retraining, hotplug, low-power transitions, and suspend/resume on CR4-backed links across supported rates and lane counts; watch for black screens, link-training failures, flicker, repeated PHY resets, or unstable equalization.
- Validate lane-2 RX paths by dumping CTLE/DFE adaptation status, DFE VDAC offsets, slicer levels, SSM final code, statistic counters, IQ status, signal-detect calibration, analog RX status, and termination/VCO/AFE override state before and after training.
- Validate lane-3 TX paths by checking TX ASIC in/out fields, pstate presets, power-up timing, DCC status, clock-alignment status, LBERT pattern behavior, FIFO status, analog TX DCC calibration state, and equalization readbacks.
- Validate lane-3 RX paths by checking RX ASIC in/out acknowledge/valid/adaptation status, CDR/VCO config, signal-detect overrides, equalization/DFE override fields, DFE bypass, CDR tracking/SSC settings, and RX output status during bring-up and retraining.

## Chunk-Specific Summary

Lines 200000-202389 define DCN 3.2.0 C20 PHY CR4 lane-2 RX adaptation/statistics/analog-RX register shifts and masks, followed by lane-3 ASIC TX, TX power/calibration/debug, analog TX, and ASIC RX register shifts and masks. The content is generated register ABI rather than executable driver logic. Correctness depends on exact field positions, consistency with companion register offset headers and hardware specifications, careful handling of split boundary registers, and validation through DCN 3.2 link training, calibration, debug readbacks, and power-management test paths.
