# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 131243-133878

## Scope

This chunk is a late segment of the generated AMD DPCS 4.2.3 shift/mask header. It covers line 131243 through line 133878 and defines 2,041 `__SHIFT` macros across 596 visible register groups. Unlike earlier portions of this header that include both shifts and masks, this range contains shift definitions only. It begins at the tail of `C20_PHY_CR1_RAWLANEAON2_DIG_RX_CAL_BANK_SEL`, then covers the end of RawLaneAON2 RX fields, a broad RawLaneAON3 TX/RX firmware and calibration surface, and a large lane-generic `C20_PHY_CR1_LANEX_DIG_*` surface. It ends inside `C20_PHY_CR1_LANEX_DIG_ANA_XF_RX_STAT_OUT_1`, after `RX_ANA_CDR_VCO_EN__SHIFT`.

The content is declarative. There are no C functions, structs, enums, branches, loops, allocations, locks, or direct register accesses. The exported interface is a generated preprocessor namespace that gives bit positions for DPCS C20 PHY CR1 fields.

## Purpose

`dpcs_4_2_3_sh_mask.h` provides symbolic bitfield metadata for AMDGPU display code targeting the DPCS 4.2.3 register layout. Consumers pair these `__SHIFT` constants with companion `_MASK` constants elsewhere in the same header and register offsets from `dpcs_4_2_3_offset.h` to compose, update, and decode indexed or memory-mapped display PHY registers without hard-coding raw bit numbers.

This chunk focuses on C20 PHY CR1 always-on raw-lane and lane-generic definitions:

- `C20_PHY_CR1_RAWLANEAON2_DIG_RX_*`: tail RX DCC, IQ, adaptation, DFE tap, TX-equalization feedback, override, signal-detect, PMA, input, and output fields for RawLaneAON2.
- `C20_PHY_CR1_RAWLANEAON3_DIG_TX_*`: firmware states, SRAM recovery, algorithm control, fast flags, high-power protection, lane transceiver mode, MPLLA/MPLLB DCC calibration banks, calibration-done fields, DCC code readbacks, and TX inputs for RawLaneAON3.
- `C20_PHY_CR1_RAWLANEAON3_DIG_RX_*`: startup calibration/adaptation algorithm controls, continuous adaptation controls, fast flags, VDAC/IDAC offsets, DCC and IQ calibration banks, adaptation banks, DFE offsets, TX equalization thresholds, CDR and signal-detect controls, override surfaces, and RX I/O readbacks for RawLaneAON3.
- `C20_PHY_CR1_LANEX_DIG_*`: lane-generic ASIC override/input/output fields, TX/RX power-control state tables and timers, DCC controls, TX/RX statistic and match counters, LBERT, clock alignment, CDR/DPLL, adaptation control/status, IQ correction, and digital-to-analog transfer controls/status for TX and RX.

## Exported API Surface

There are no callable APIs or local data types. The public surface is a set of generated macros of the form `<REGISTER>__<FIELD>__SHIFT`.

Important macro families in this range include:

- RawLaneAON2 RX DCC/IQ/adaptation fields: `DIG_RX_DCC_*`, `DIG_RX_IQ_*`, `DIG_RX_ADPT_*`, `DIG_RX_DFE_*`, `DIG_RX_CDR_*`, `DIG_RX_SIGDET_*`, `DIG_RX_OVRD_*`, `DIG_RX_PMA_OVRD_OUT_0`, `DIG_RX_IN_0`, and `DIG_RX_OUT_0`.
- RawLaneAON3 TX firmware and calibration fields: `DIG_TX_FW_STATES_*`, `DIG_TX_MEM_BREAKPOINT_2`, `DIG_TX_SRAM_REC_*`, `DIG_TX_STARTUP_ALGO_CTL_0`, `DIG_TX_CONT_ALGO_CTL_0`, `DIG_TX_FAST_FLAGS_0`, `DIG_TX_MPLLA_*`, `DIG_TX_MPLLB_*`, `DIG_TX_CAL_DONE`, `DIG_TX_DCC_*`, `DIG_TX_CAL_BANK_SEL`, and `DIG_TX_IN_0`.
- RawLaneAON3 RX calibration/adaptation fields: `DIG_RX_STARTUP_CAL_ALGO_CTL_*`, `DIG_RX_STARTUP_ADAPT_ALGO_CTL_0`, `DIG_RX_CONT_ALGO_CTL`, `DIG_RX_FAST_FLAGS`, `DIG_RX_*_VDAC_OFST`, `DIG_RX_*_IDAC_OFST`, `DIG_RX_DCC_*_BANK_*`, `DIG_RX_CAL_DONE_BANK_*`, `DIG_RX_ADPT_*_BANK_*`, `DIG_RX_TX_*_THRESHOLD`, `DIG_RX_ADPT_CTL_0` through `DIG_RX_ADPT_CTL_28`, and the RawLaneAON3 RX override and PMA readback fields.
- Lane-generic ASIC bridge fields: `C20_PHY_CR1_LANEX_DIG_ASIC_LANE_*`, `DIG_ASIC_TX_*`, and `DIG_ASIC_RX_*`, including override inputs, ASIC input mirrors, ASIC outputs, signal-detect/VCO/equalization override groups, and misc override controls.
- Lane-generic TX/RX control and diagnostics: `DIG_TX_PWRCTL_*`, `DIG_TX_DCC_CTL_*`, `DIG_TX_STAT_*`, `DIG_TX_CLK_ALIGN_*`, `DIG_TX_LBERT_*`, `DIG_TX_FIFO_CTL`, `DIG_RX_PWRCTL_*`, `DIG_RX_VCOCAL_*`, `DIG_RX_LBERT_*`, `DIG_RX_CDR_*`, `DIG_RX_DPLL_*`, `DIG_RX_ADPTCTL_*`, `DIG_RX_STAT_*`, and `DIG_RX_IQC_CTL_*`.
- Digital-to-analog transfer fields: `DIG_ANA_XF_TX_*` and `DIG_ANA_XF_RX_*` for override outputs, termination code control, DCC calibration, analog config/status, TX equalization status, RX signal-detect calibration, RX VCO/AFE/slicer/IQ controls, loopback, sample selection, and analog status readback.

The chunk emits reserved fields as named shifts, such as `RESERVED_15_*`. Those definitions matter for generated masks and read-modify-write helpers that need to preserve or avoid undocumented bit ranges.

## Register Areas Covered

The RawLaneAON2 tail is RX-centric. It exposes duty-cycle correction code fields for data, bypass, and phase paths; IQ calibration and done readbacks; two adaptation result banks for attenuator, VGA, CTLE, DFE taps, DFE tap offsets, IQ, reference error, and adaptation done; TX equalization threshold feedback used by RX adaptation logic; generic adaptation control words; CDR detector/recovery controls; signal-detect filtering; and override/input/output mirrors.

The RawLaneAON3 TX section adds firmware-observable state and calibration control. It includes firmware state bits, memory breakpoint and SRAM recovery controls, CCA counters, startup and continuous DCC algorithm skip bits, fast-mode flags, high-power protection and transceiver-mode override inputs, four DCC banks each for MPLLA and MPLLB, per-bank and aggregate calibration-done readbacks, selected DCC code readbacks, calibration bank select, and TX input status.

The RawLaneAON3 RX section is larger and mirrors many RawLaneAON2 concepts while adding full startup and continuous algorithm controls. It defines startup calibration/adaptation skip bits for VGEN, signal-detect, AFE trim, VDAC offsets, IQ, DCC, rate-aware recalibration, and DFE tap handling. It also exposes VDAC/IDAC setup offsets for reference, slicer, AFE, CTLE, VGA, DFE phase/data/bypass/error paths; four DCC/IQ/calibration banks; active DCC code readbacks; two adaptation result banks; broad adaptation control words; CDR and signal-detect fields; and RawLaneAON3 override/status mirrors.

The `LANEX` block abstracts fields common to a lane instance. The ASIC bridge groups carry driver/firmware override values and hardware-facing inputs/outputs for TX/RX requests, resets, pstates, rates, data enable, clocking, serial/deserializer enable, VREF, PWM, equalization, CDR/VCO, signal detect, loopback, and lane-master status. The TX/RX power-control groups encode P0/P0S/P1/P2 state bitmaps and power-up timing fields. TX/RX statistic blocks define match masks, sample counters, statistic counters, stop controls, calibration-comparator clocks, and load-value registers.

The later `LANEX` RX blocks cover VCO calibration, LBERT error testing, CDR and DPLL boundaries, adaptation configuration/status, SSM configuration, IQ correction controls, and RX analog transfer fields. The analog transfer groups are especially hardware-facing: they expose override enables for RX/TX analog power, clocks, AFE, CDR, DFE, termination, DCC DAC control, VCO startup/tuning, signal-detect calibration, slicer control, IQ bypass/data adjustment clocks, loopback, sample selectors, and status readbacks.

## Control Flow And State Behavior

This header chunk has no local control flow. Runtime behavior appears only when included by AMD display code that passes these constants into register-field helpers for DPCS/DIO/HPO PHY access.

The field names describe several hardware state machines and persistent hardware states:

- DCC and IQ calibration: bank-select, range, full-rate, half-rate, data, bypass, phase, IQ calibration, and `*_DONE` fields expose calibration sequencing and readback state for RawLaneAON2/3 TX and RX paths.
- TX/RX power sequencing: `PSTATE_P0`, `PSTATE_P0S`, `PSTATE_P1`, `PSTATE_P2`, `PWRUP_TIME_*`, request, reset, data enable, clock enable, serial/deserializer enable, and status fields represent lane power-management state and timing.
- Adaptation and equalization: ATT, VGA, CTLE, DFE tap, slicer, VDAC/IDAC offset, reference-error, fast-flag, and SSM fields describe RX adaptation state and thresholds used during link training or continuous adaptation.
- CDR/DPLL/VCO behavior: CDR control/status, DPLL frequency bounds, VCO calibration control/time/status, VCO override outputs, startup, center, and frequency-tune fields support clock recovery and lane-rate transitions.
- Override workflows: repeated `*_OVRD_IN`, `*_OVRD_OUT`, `*_OVRD_EN`, and `*_ASIC_IN` fields let firmware, driver bring-up code, validation tools, or recovery paths force values that would normally be generated by PHY control state machines.
- Debug and validation: LBERT, SRAM recovery, firmware state, memory breakpoint, statistic counters, match masks, sample counters, ATB-like analog transfer controls, and analog status outputs support lab diagnostics and failure isolation.

No software persistence is implemented here. Hardware register contents persist according to the ASIC reset, lane power, always-on, and clock domains. By naming convention, fields containing `STAT`, `STATUS`, `OUT`, `DONE`, `ERR`, `CNT`, or `ASIC_OUT` are primarily readback-oriented, while fields containing `CTL`, `CFG`, `OVRD_IN`, `OVRD_EN`, `PSTATE`, `TIME`, `SEL`, or calibration values are control/configuration-oriented. The header itself does not encode read/write permissions, sticky behavior, self-clearing behavior, or reset defaults.

## Dependencies And Integration Points

The only syntactic dependency is the C preprocessor. Semantically, this chunk depends on the rest of `dpcs_4_2_3_sh_mask.h` for corresponding masks and on `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h` for matching register addresses.

The direct include site in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which includes both the DPCS 4.2.3 offset and shift/mask headers. That resource code builds DCN316 register/shift/mask tables used by AMD display resource initialization. This chunk exposes many low-level PHY fields beyond the compact high-level table entries in that resource file, but they share the same generated namespace available to DCN316 display, PHY, diagnostics, and hardware-validation code.

Likely integration points include:

- DCN316 resource initialization and DPCS register table generation.
- DCN31-style DIO/HPO link encoder code that programs DPCS lanes during DisplayPort or HDMI link setup.
- PHY firmware or firmware-assisted driver paths that inspect RawLaneAON firmware states, calibration banks, and adaptation results.
- Link training and recovery paths that need RX CDR, DPLL, VCO calibration, signal detect, equalization, DFE, and TX drive settings.
- Suspend/resume, hotplug, lane power-gating, and link-rate transition flows that depend on TX/RX power-control states and timing.
- Lab/debug flows using LBERT, statistic counters, match logic, SRAM recovery, firmware breakpoints, and analog transfer/status fields.

## Risks

- Generated-header drift is the primary risk. A wrong shift value can silently set or read the wrong PHY bit when combined with a correct-looking mask and offset.
- This chunk contains only `__SHIFT` definitions; corresponding masks are outside this exact line range. Chunk-local validation should not report missing masks as a source defect without considering the whole generated file.
- The range starts and ends at chunk boundaries inside register groups: it begins with the tail of `RAWLANEAON2_DIG_RX_CAL_BANK_SEL` and ends before the rest of `LANEX_DIG_ANA_XF_RX_STAT_OUT_1`. Merge-time checks should account for neighboring chunks.
- Override fields are dense and paired. Setting an override value without its enable bit will not have the intended effect, while leaving an enable bit set can hold PHY state across later link training, hotplug recovery, or resume.
- Many fields control analog calibration, CDR/VCO/DPLL behavior, lane power, and equalization. Incorrect programming can appear as intermittent link training failures, marginal signal quality, lane-specific failures, or failures only at certain data rates.
- Readback and control fields are represented by identical macro syntax. Consumers must rely on the hardware register database and access helpers for read-only, write-only, sticky, self-clearing, and reserved-bit behavior.
- Multiple banked fields share nearly identical names across RawLaneAON2, RawLaneAON3, `MPLLA`, `MPLLB`, bank numbers, and full/half-rate paths. Copy/paste mistakes are hard to spot in code review unless tests exercise each rate and bank.
- Reserved bit shifts are exported. Driver code should preserve reserved bits where required and avoid deriving new undocumented register values from these macros alone.

## Test Signals

Useful validation is mainly build-time, generation-time, and hardware-integration oriented:

- Compile or preprocess AMDGPU display code for DCN316 targets that include `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`.
- Regenerate or diff the full DPCS 4.2.3 header against the authoritative AMD register database, checking that every complete field has the expected shift and mask.
- Cross-check register names in this range against `dpcs_4_2_3_offset.h` and against any generated DCN316 DPCS table macros that consume this namespace.
- Exercise DP and HDMI link training, link-rate changes, lane power-state transitions, hotplug, suspend/resume, and recovery after failed link training on DPCS 4.2.3-class hardware.
- Validate RawLaneAON2/3 calibration flows by reading DCC/IQ calibration banks, calibration-done bits, adaptation result banks, DFE tap/offset values, CDR status, signal-detect state, and PMA override readbacks.
- Validate `LANEX` power-control and analog-transfer behavior through register readback around P0/P0S/P1/P2 transitions, VCO calibration, DPLL bounds, RX adaptation, TX/RX statistics, LBERT, and cleanup of all override-enable bits after debug or recovery flows.
- Use static checks for duplicate or inconsistent banked names across `RAWLANEAON2`, `RAWLANEAON3`, `LANEX`, `MPLLA`, `MPLLB`, bank 0-3, full-rate, and half-rate families.

## Chunk Notes For Merge

This document is source-tree aligned and covers only lines 131243-133878 of `dpcs_4_2_3_sh_mask.h`. Earlier chunks should provide the start of `C20_PHY_CR1_RAWLANEAON2_DIG_RX_CAL_BANK_SEL` and the broader C20/CR1 context. Later chunks should continue `C20_PHY_CR1_LANEX_DIG_ANA_XF_RX_STAT_OUT_1` and any remaining C20 PHY CR1 register groups. The final per-file report should treat the complete file as a generated ASIC register bitfield map for AMD display PHY programming, not as handwritten runtime logic.
