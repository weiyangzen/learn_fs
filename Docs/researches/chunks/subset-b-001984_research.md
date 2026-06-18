# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 134366-136747

## Scope

This chunk is a generated AMDGPU Display Core DCN 3.2.0 register-field shift/mask slice for the C20 PHY CR2 namespace. It contains preprocessor constants only: `_SHIFT` macros give field lsb positions, `_MASK` macros give bit masks, and `//<REGISTER>` comments group the definitions by hardware register. There are no C functions, structs, enums, branches, loops, memory allocations, locks, syscalls, or direct MMIO accesses in this range.

The slice contains 2176 `#define` lines covering 207 register groups. It is mostly balanced shift/mask material, but it starts and ends on chunk boundaries that split register groups:

- The first in-scope line is in the middle of `C20_PHY_CR2_LANE2_DIG_ANA_XF_RX_AFE_OVRD_IN_2`; earlier shifts and at least the first mask for this register are outside this chunk, while the remaining masks are inside.
- The last in-scope register is `C20_PHY_CR2_LANE3_DIG_RX_STAT_STAT_CTL1`; its complete shift and mask set is present here, and the next register, `C20_PHY_CR2_LANE3_DIG_RX_STAT_SMPL_CNT1`, begins after this chunk.

## Purpose And Hardware Surface

This header is part of the generated register ABI used by AMD display driver code to pack and decode fields in DCN 3.2.0 C20 PHY registers. Companion generated headers provide register addresses; this file provides field positions and masks used by AMDGPU register helper macros for MMIO programming and register dumps.

The hardware surface in this chunk covers the transition from lane 2 RX analog control to the bulk of lane 3 digital/analog TX and RX control:

- `C20_PHY_CR2_LANE2_DIG_ANA_XF_RX_*` completes lane 2 RX AFE override masks and defines lane 2 RX analog configuration register fields `RX_ANA_CREG00` through `RX_ANA_CREG11`, plus `RX_ANA_CREG0_OVRD` and `RX_ANA_CREG1_OVRD`.
- `C20_PHY_CR2_LANE3_DIG_ASIC_*` defines lane 3 ASIC-facing override/input/output fields for lane, TX, and RX paths. These include request/reset/rate/power-state signals, TX coefficient controls, RX adaptation controls, EQ override fields, signal detect, VCO, and lane mode/status handshakes.
- `C20_PHY_CR2_LANE3_DIG_TX_*` defines lane 3 TX power-state control, power-up timing, TX control/status, TX DCC offset controls, TX statistic/load counters, TX clock alignment, TX loopback BERT controls, TX FIFO control, and TX analog transfer/status/configuration registers.
- `C20_PHY_CR2_LANE3_DIG_ANA_XF_TX_*` maps lane 3 TX analog override/status/configuration fields, including serializer/reset/power/driver selection, termination-code overrides, DCC enable/config/calibration controls, EQ override and status, and TX analog `CREG00` through `CREG05` override banks.
- `C20_PHY_CR2_LANE3_DIG_RX_*` defines lane 3 RX power-state control, VCO calibration, loopback BERT error reporting, CDR control/status, DPLL frequency and frequency bounds, adaptation configuration/status, DFE/slicer/DCC offset controls, fast flags, SSM search controls, and RX statistic controls.

## Important Definitions

The generated naming pattern is consistent across the chunk:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for writing or extracting a field value.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted mask for that field.
- Register comments are the only grouping metadata; there are no typed declarations.

Important macro families in this range:

- Lane 2 RX analog `CREG` fields: `C20_PHY_CR2_LANE2_DIG_ANA_XF_RX_ANA_CREG00` through `CREG11` define low-level AFE, DCC, CDR, VCO, IQ, divider, calibration, ATB measurement, vreg, signal-detect, DFE, slicer, bypass, phase, and termination-related settings. The pair `RX_ANA_CREG0_OVRD` and `RX_ANA_CREG1_OVRD` exposes coarse override-enable masks for these analog register banks.
- Lane 3 TX ASIC override/input/output fields: `C20_PHY_CR2_LANE3_DIG_ASIC_TX_OVRD_IN_0` through `_5`, `TX_ASIC_IN_0` through `_3`, `TX_OVRD_OUT`, `TX_ASIC_OUT`, and `TX_OVRD_MISC` describe TX request, reset, rate, power-state, polarity, loopback, pre/main/post-cursor coefficients, finite impulse response modes, lane mode, power-up completion, and off-canonical tracking.
- Lane 3 RX ASIC override/input/output fields: `RX_OVRD_IN_0` through `_4`, `RX_OVRD_SIGDET_IN`, `RX_OVRD_VCO_IN`, `RX_OVRD_EQ_IN_0` through `_11`, `RX_ASIC_IN_0` through `_3`, `RX_CDR_VCO_ASIC_IN`, `RX_EQ_ASIC_IN_0` through `_2`, `RX_ASIC_OUT_0`, and `RX_OVRD_MISC` define RX reset/request/rate/p-state, adaptation enable/mode/ack, DFE/VGA/CTLE/ATT controls, CDR/VCO control, IQ/phase adjust codes, equalizer tap initial/min/max/override values, FOM, and off-canonical state.
- Lane 3 TX power and control fields: `TX_PSTATE_P0`, `P0S`, `P1`, and `P2` encode per-state TX power, driver, serializer, mode, termination, VBoost, and DCC decisions. `TX_PWRUP_TIME_0` through `_5` encode timing delays for clock, serializer, power, driver, mode, DCC, termination, reset, and related startup sequencing. `TX_CTL` and `TX_STATUS` expose control bits such as reset ACK, rate ACK, termination control, transceiver mode, DCC enable, power, and status readback.
- Lane 3 TX calibration and observation fields: `TX_DCC_CTL_TX_DCC_DIFF_IDAC_OFST`, `TX_DCC_CTL_TX_DCC_CM_IDAC_OFST`, `TX_DCC_CTL_STAT`, `TX_STAT_*`, `TX_CLK_ALIGN_*`, `TX_LBERT_*`, and `TX_LVL_CALC_STAT` cover DCC offset override values, DCC status, programmable statistic counters, clock alignment, loopback BERT patterns, and TX level calculation status.
- Lane 3 TX analog transfer fields: `ANA_XF_TX_OVRD_OUT_0` through `_3`, `TX_TERM_CODE_*_OVRD_OUT`, `TX_ANA_DCC_*`, `TX_STAT_EQ_*`, `TX_STAT_OUT_*`, `TX_STAT_IN_0`, and `TX_ANA_CREG00` through `CREG05` define low-level TX analog override/status values for serializer, reset, power, driver selection, termination code, DCC calibration, EQ configuration, and analog control registers.
- Lane 3 RX power and VCO/CDR fields: `RX_PSTATE_P0`, `P0S`, `P1`, `P2`, `RX_PWRUP_TIME_0`, `RX_PWRUP_TIME_1`, `RX_CTL`, `RX_STATUS`, `RX_VCOCAL_RX_VCO_CAL_CTRL_*`, `RX_VCOCAL_RX_VCO_CAL_TIME_*`, `RX_VCOCAL_RX_VCO_STAT_*`, `RX_CDR_CDR_CTL_*`, `RX_CDR_STAT`, `RX_DPLL_FREQ`, and `RX_DPLL_FREQ_BOUND_*` describe RX power-state programming, startup timing, reset/rate acknowledgements, VCO calibration mode/control/timing/status, CDR integral/proportional gains and lock settings, and DPLL frequency limits/readback.
- Lane 3 RX adaptation fields: `RX_ADPTCTL_ADPT_CFG_0` through `_12`, `RST_ADPT_CFG`, `ATT_STATUS`, `VGA_STATUS`, `CTLE_STATUS`, `DFE_TAP1_STATUS` through `DFE_TAP5_STATUS`, `ADPT_RESET`, and `RX_FAST_FLAGS` configure adaptation gating, control, averaging, settling, target values, saturation limits, lock timers, and fast-settle behavior while exposing live equalization state.
- Lane 3 RX DFE, slicer, and DCC offset fields: `DFE_DATA_*_VDAC_OFST`, `DFE_ERROR_*_VDAC_OFST`, `DFE_BYPASS_*_VDAC_OFST`, `RX_SLICER_CTRL_EVEN`, `RX_SLICER_CTRL_ODD`, `ERROR_SLICER_*_LEVEL`, and `RX_DCC_*_IDAC_OFST` provide value plus override-enable fields for even/odd data, error, bypass, phase, data, and common-mode/differential offsets.
- Lane 3 RX SSM and statistics fields: `SSM_SSM_CFG_0` through `_4` configure slicer/search state machine threshold, DAC selection, destination, step counts, wait periods, direction, sticky/LPF bypass behavior, and start control. `SSM_FINAL_CODE` exposes DAC code, done/abort flags, and FSM state. `RX_STAT_LD_VAL_1`, `RX_STAT_DATA_MSK`, `RX_STAT_MATCH_CTL0`, `RX_STAT_MATCH_CTL1`, `RX_STAT_STAT_CTL0`, and `RX_STAT_STAT_CTL1` configure statistic-counter load values, masks, pattern matching, correlation/statistic source selection, valid-data handling, counter enables, and statistic clock control.

## Control Flow And State Behavior

There is no executable control flow in this chunk. Runtime behavior comes from driver code that combines these masks and shifts with register offsets and helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, or generated bitfield helpers.

Typical runtime flows using these definitions are:

1. Link setup or retraining code programs lane 3 TX/RX ASIC override and input registers to select lane rate, lane mode, reset/request behavior, polarity, loopback, power state, adaptation mode, and coefficient or equalizer settings.
2. Power sequencing code selects per-state TX/RX power options and startup delays through the `TX_PSTATE_*`, `RX_PSTATE_*`, `TX_PWRUP_TIME_*`, and `RX_PWRUP_TIME_*` fields, then observes status and acknowledgment fields.
3. Analog bring-up and calibration code writes TX/RX analog `CREG` fields, DCC offset fields, termination-code overrides, VCO calibration controls, CDR controls, DPLL bounds, and adaptation configuration before polling status fields.
4. Adaptation code uses RX adaptation controls and status registers to tune ATT, VGA, CTLE, DFE taps, slicer thresholds, IQ/phase codes, VCO/CDR state, and FOM-related values.
5. Debug, validation, and manufacturing flows use TX/RX statistics, LBERT controls, clock alignment status, SSM final codes, DCC calibration status, CDR/VCO status, and raw analog readbacks to diagnose lane behavior.

The state represented by these macros is hardware register state, not driver-owned memory:

- Persistent programmed state includes ASIC override enables, TX/RX request/reset/rate/p-state values, TX driver and EQ settings, RX adaptation mode and equalizer values, TX/RX power-state definitions, startup timing, analog `CREG` values, DCC offset overrides, VCO/CDR calibration controls, DPLL bounds, SSM configuration, and statistic control setup.
- Volatile readback includes TX/RX off-canonical state, power-up completion, TX/RX status, TX DCC status, clock alignment status, LBERT error counters, TX level status, analog TX/RX status, RX VCO calibration state, CDR status, DPLL frequency, adaptation status, SSM final code/done/abort state, and statistic-counter validity/status.
- Side-effecting or sequencing-sensitive fields include reset/rate acknowledgements, DCC calibration enables, VCO calibration controls, adaptation reset, SSM start, statistic load/start and valid-loss clear fields, self-clearing or pulse-style clock/update controls in analog banks, and override-enable bits that can bypass normal firmware or hardware-calibrated behavior.

## Dependencies And Integration Points

This chunk depends on generated-name consistency across the DCN 3.2.0 register header set. It is normally consumed alongside the matching register-address header and the AMD Display Core register access layer. The C compiler can catch missing macro names, but wrong numeric masks or shifts usually compile successfully and only surface as hardware failures.

Key integration points include:

- AMDGPU Display Core DCN 3.2 link encoder and PHY code that programs C20 PHY lane controls during DisplayPort/embedded DisplayPort link bring-up, retraining, hotplug, and modeset transitions.
- Register helper macros and generated register tables that use these field definitions to compose MMIO writes and decode MMIO reads.
- Firmware-assisted PHY flows that hand off lane request/reset/rate, TX coefficient, RX adaptation, FOM, and status signals through `*_ASIC_*` and analog transfer register families.
- Power-management paths that move lanes among P0/P0S/P1/P2 states, adjust startup delays, disable or re-enable analog subblocks, and rely on acknowledgement/status bits during suspend/resume or link idle transitions.
- Calibration and signal-integrity flows that consume TX DCC, RX VCO, CDR, DPLL, DFE, CTLE, VGA, ATT, slicer, SSM, and statistic fields to tune the physical link.
- Debug and diagnostics tooling that decodes register dumps for lane 2 analog RX state and lane 3 TX/RX state using these exact field names and masks.

## Risks And Maintenance Notes

- Numeric drift is the main risk. These constants are hardware ABI: a single bad shift or mask can corrupt link-rate changes, lane reset sequencing, power-state selection, analog calibration, CDR lock, RX adaptation, or statistic decoding.
- Dense 16-bit registers have many adjacent fields and reserved bits. Overlapping or off-by-one masks may compile cleanly while writing reserved bits or mixing neighboring hardware controls.
- The repeated family structure is easy to mis-generate or mis-review: lane 2 vs lane 3, TX vs RX, ASIC vs analog transfer, override input vs ASIC input vs status output, even vs odd slicer/DFE fields, common-mode vs differential DCC fields, and P0/P0S/P1/P2 power-state definitions.
- Override-enable fields are high risk because they can bypass hardware/firmware ownership. Incorrect enable masks may force stale values, prevent normal adaptation, or leave TX/RX analog controls in lab/debug settings.
- Calibration and clear/start fields are sequencing-sensitive. Incorrect masks on DCC, VCO, CDR, SSM, adaptation reset, statistic valid-loss clear, or LBERT/statistic start controls can create stuck calibration, lost status, false done indications, or repeated retraining.
- Boundary completeness matters for generated research. `C20_PHY_CR2_LANE2_DIG_ANA_XF_RX_AFE_OVRD_IN_2` is partial at the start of this chunk, and final file-level reconciliation should combine this document with adjacent chunk research before describing complete file coverage.

## Test Signals

Useful validation signals combine generated-header checks, build coverage, and hardware behavior:

- Build AMDGPU with DCN 3.2 support enabled and ensure references to the in-scope `C20_PHY_CR2_LANE2_DIG_ANA_XF_RX_*` and `C20_PHY_CR2_LANE3_DIG_*` field names resolve.
- Run generated-register consistency checks that every complete in-scope register has matching `_SHIFT` and `_MASK` definitions, masks fit within the expected register width, and fields do not overlap unexpectedly outside documented reserved regions.
- Compare the numeric masks and shifts against the authoritative DCN 3.2.0 C20 PHY register specification, focusing on side-effecting ACK, reset, calibration, SSM start, statistic clear/start, DCC offset, and override-enable fields.
- Exercise DisplayPort/eDP link training and retraining on DCN 3.2 hardware across supported lane counts and link rates; watch for link-training failure, black screen, flicker, repeated retraining, or PHY reset loops.
- Validate power-management transitions by testing hotplug, modeset, suspend/resume, display idle, and low-power entry/exit while checking TX/RX P-state programming, startup timing, and status/acknowledgement fields.
- Stress RX adaptation and equalization by reading ATT/VGA/CTLE/DFE status, FOM-related values, CDR lock/state, DPLL frequency, VCO calibration status, slicer offsets, and SSM final codes after mode changes and high-bandwidth link training.
- Validate TX analog and DCC behavior by inspecting TX DCC offset/status fields, TX analog status outputs, clock-alignment status, TX LBERT pattern generation, and TX statistic counters during calibration and loopback tests.
- Use register dumps before and after link bring-up, retraining, and power-down to confirm that persistent programmed fields and volatile readback fields decode coherently through these masks.

## Chunk-Specific Summary

Lines 134366-136747 define generated DCN 3.2.0 C20 PHY CR2 shift/mask constants for lane 2 RX analog configuration and most of lane 3 TX/RX ASIC, power, analog, calibration, adaptation, SSM, and statistic control. The chunk is register metadata rather than executable logic. Correctness depends on exact bitfield values, complete reconciliation with the preceding partial lane-2 AFE register, and hardware validation across link training, power sequencing, TX/RX calibration, RX adaptation, CDR/VCO/DPLL behavior, LBERT/statistic diagnostics, and suspend/resume.
