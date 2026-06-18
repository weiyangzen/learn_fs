# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 99809-102362

## Scope

This chunk is a late segment of the generated AMD DPCS 4.2.3 shift/mask header. It covers line 99809 through line 102362 and defines 2,124 `__SHIFT` macros across 430 visible register groups, plus one `_MASK` macro that belongs to the previous chunk's `C20_PHY_CR0_RAWCMN_DIG_AON_SUP_IN_0` register. The range starts at the tail of `C20_PHY_CR0_RAWCMN_DIG_AON_SUP_IN_0`, continues through CR0 RAWCMN always-on supervisor/SRAM/calibration controls, covers most of CR0 lane 0 digital TX/RX and analog-transfer fields, then enters the corresponding CR0 lane 1 TX/RX surface and ends inside `C20_PHY_CR0_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0S`.

The content is declarative only. There are no C functions, structs, enums, runtime branches, loops, allocations, or local state mutations. The exported interface is a large set of C preprocessor constants naming bit positions for DPCS C20 PHY CR0 hardware registers.

## Purpose

`dpcs_4_2_3_sh_mask.h` gives AMDGPU display code symbolic bitfield locations for DPCS 4.2.3 hardware registers. Consumers pair these `__SHIFT` constants with the companion `_MASK` constants in the same generated header, matching register offsets from `dpcs_4_2_3_offset.h`, and the AMD display register helper macros to build read-modify-write values without embedding raw bit numbers in driver logic.

This chunk focuses on the C20 PHY CR0 common and lane-local register space:

- RAWCMN always-on supervisor output overrides, common MPLL/RTUNE calibration status, RTUNE result values for lanes 0-7, SRAM boot/load status, firmware and RAW version words, supervisor clock/firmware stop controls, APB timeout controls, power/clock status readback, metadata, and SRAM recovery address controls.
- Lane 0 ASIC-facing TX/RX override inputs and readbacks, lane mode controls, TX/RX ASIC input mirrors, power-state bitmaps, power-up timers, status words, clock alignment, LBERT controls, FIFO controls, DCC calibration, RX VCO/CDR/adaptation/IQC/statistic controls, and analog-transfer override/status/configuration fields.
- Lane 1 starts the same lane-local pattern: lane/TX override and ASIC input/output fields, TX power-state/timer/status and TX analog-transfer fields, RX override/equalization/ASIC input/output fields, and the beginning of RX power-state programming.

## Exported API Surface

There are no callable APIs or local types. The public surface is the generated macro namespace:

- `C20_PHY_CR0_RAWCMN_DIG_AON_*`: common always-on fields for supervisor handshakes, MPLLA/MPLLB recalibration bank selection, common MPLL/RTUNE calibration status, per-lane RTUNE RX/TX result words, SRAM load and boot bypass controls, firmware/RAW version registers, APB timeout configuration, common power/clock status, metadata location, and SRAM recovery addressing.
- `C20_PHY_CR0_LANE0_DIG_ASIC_*`: lane 0 digital ASIC-facing lane, TX, and RX controls. These include override value/enable pairs for reset, invert, data enable, request, low-power detect, pstate, rate, width, VCO/load values, PLL enables, spread-spectrum, clock dividers, loopback, swing/pre-emphasis, termination, VREF, receiver signal-detect, CDR, VCO, equalization, and miscellaneous fields.
- `C20_PHY_CR0_LANE0_DIG_TX_*`: lane 0 TX power-control, timing, DCC, statistic, clock-align, LBERT, level-calculation, FIFO, and digital-to-analog transfer fields. The P0/P0S/P1/P2 groups describe which analog and digital TX sub-blocks are enabled for each power state.
- `C20_PHY_CR0_LANE0_DIG_RX_*`: lane 0 RX power-control, VCO calibration, LBERT, CDR, DPLL, adaptation, slicer/state-machine, RX DCC, statistic/match/count, IQC, and digital-to-analog transfer fields. The RX groups describe both configuration and readback paths for receiver adaptation and diagnostics.
- `C20_PHY_CR0_LANE0_DIG_ANA_XF_*`: lane 0 bridge fields that transfer digital controls/status to or from analog TX/RX blocks, including override outputs, termination-code overrides, DCC calibration controls, equalization override/status, analog CREG words, signal-detect calibration, VCO override/status, DAC controls, AFE controls, scope/slicer/IQ/IQC controls, loopback, and analog sample selectors.
- `C20_PHY_CR0_LANE1_DIG_*`: lane 1 repeats the lane 0 TX/RX structure through TX analog-transfer fields and RX ASIC override/equalization fields. This slice reaches the beginning of lane 1 RX power-control P0S definitions and continues in the next chunk.

Most complete groups follow the generated convention `<REGISTER>__<FIELD>__SHIFT`; the corresponding `<REGISTER>__<FIELD>_MASK` definitions are mostly outside this chunk because this range is in the shift-definition portion of the header. Reserved fields are emitted as named constants too, which lets generator checks and low-level code reason about full 16-bit register layouts.

## Register Areas Covered

The RAWCMN AON section defines common CR0 resources shared by the C20 PHY. Supervisor output override fields force MPLLA/MPLLB acknowledge and reference or firmware clock requests. Calibration/status groups expose common MPLL and RTUNE initialization/done states, recalibration-bank selection, and per-lane RTUNE values for RX, TXDN, and TX average paths. SRAM fields describe external load completion, bypass and bootload bypass, SRAM init-done, EOF/BOC locations, recovery offsets, and firmware/RAW version identification. Supervisor control/status fields cover CR clock source overrides, firmware stop request/acknowledge, SRAM/ROM clock enables, APB timeout policy, PMA/PCS power stability, isolation, reference-clock acknowledgement, and firmware clock requests.

Lane 0 is the largest part of the chunk. The TX side contains ASIC override controls for core link signals, TX pstate/rate/width, MPLL force enables, CDR/VCO-related values, loopback, TX swing/pre-emphasis, VREG, VREF, termination, and miscellaneous override values. TX power-control groups encode P0/P0S/P1/P2 power-state enables for analog reference, VCM hold, analog and word clocks, data/serial output, digital clocking, RX detect, DCC calibration, and reset behavior. TX timing groups split power-up time values across several registers, while TX DCC/stat/clock-align/LBERT/fifo groups expose calibration and diagnostic controls.

Lane 0 RX coverage includes ASIC override controls for reset, invert, data enable, request, pstate, rate, width, VCO load, DIV16P5 clock, CDR tracking/SSC, signal-detect thresholds, VCO configuration, equalizer attenuation/VGA/CTLE/DFE taps, DFE tap offsets, AFE bias/VCM/CTLE zero and offset, and miscellaneous receiver overrides. RX power-control and power-up groups mirror the TX pstate pattern for analog AFE, clock/VREG, deserializer, CDR, VCO resets/calibration, digital clock, DFE, and bypass slicer controls. Additional RX blocks cover VCO calibration timing/status, LBERT error counting, CDR controls/status, DPLL frequency/bounds, adaptation configuration/status, slicer and DFE state-machine controls, RX DCC offsets, statistic match/count/sample registers, IQC configuration/status, and analog-transfer controls.

Lane 1 repeats much of the same TX/RX programming model. This chunk covers lane 1 TX ASIC override and ASIC input/output mirrors, TX power-state bitmaps, TX power-up timers, TX DCC/stat/clock-align/LBERT/FIFO fields, TX analog-transfer controls/status/CREG words, RX ASIC override/equalization fields, RX ASIC mirrors, RX analog/equalizer override extension fields, and the first RX power-control P0/P0S definitions.

## Control Flow And State Behavior

This header has no software control flow. Runtime behavior appears only when code includes the generated constants and uses them through register helper macros or indexed DPCS/RDPCS transactions.

The field names imply several hardware state machines and handshakes:

- Common PHY bring-up and firmware coordination: supervisor clock source selection, firmware clock request/acknowledge, firmware stop request/acknowledge, APB timeout masking, PMA/PCS power stability, isolation state, SRAM initialization, firmware image/version discovery, and SRAM recovery addressing.
- Calibration sequencing: common MPLL and RTUNE initialization/done bits, PMA MPLL recalibration bank selection, per-lane RTUNE value capture, TX/RX DCC calibration controls and acknowledgements, RX VCO calibration timers/status, CDR controls/status, and adaptation state/status.
- Lane power transitions: TX and RX P0/P0S/P1/P2 pstate bitmaps and power-up timer fields describe which analog/digital sub-blocks are enabled and when resets, clocks, VCO calibration, data enable, serial output, CDR, DFE, and bypass slicers are sequenced.
- Override workflows: repeated `*_OVRD_VAL` plus `*_OVRD_EN` fields let firmware, driver bring-up, diagnostics, or lab tooling force state-machine-visible values for TX/RX requests, pstate, rate, width, equalization, signal detect, VCO/CDR behavior, termination, DCC, and analog bridge signals.
- Diagnostic and validation paths: LBERT controls, statistic match/count/sample registers, clock alignment status, FIFO controls, adaptation status, DFE/slicer offsets, scope controls, and analog CREG/readback fields support PHY characterization and fault isolation.

No software persistence is implemented by this file. Hardware register contents persist according to ASIC reset, power, and clock domains. Names ending in `STATUS`, `STAT`, `OUT`, `ACK`, `DONE`, `ERR`, or `CNT` are readback-oriented by naming convention; names containing `CTL`, `CFG`, `OVRD_IN`, `OVRD_EN`, `ASIC_IN`, pstate, timer, calibration, and CREG are control-oriented. The generated macros do not encode access permissions, volatility, sticky semantics, clear-on-read behavior, or reset defaults.

## Dependencies And Integration Points

The only syntactic dependency is the C preprocessor. Semantically, this chunk depends on the generated register database staying synchronized across:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h` for the corresponding C20 PHY CR0 register addresses.
- The `_MASK` half of `dpcs_4_2_3_sh_mask.h`, which provides masks matching these shift positions.
- AMD display register helper macros such as `LE_SF`, `SRI`, and `SR`, which turn generated offset/shift/mask constants into register tables.

In this tree, the direct include site for this DPCS 4.2.3 header pair is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`. That resource file includes `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h` and builds DCN316 DPCS register, shift, and mask tables through `DPCS_DCN31_REG_LIST` and `DPCS_DCN31_MASK_SH_LIST`, whose definitions live in `display/dc/dio/dcn31/dcn31_dio_link_encoder.h`.

The low-level C20 PHY fields in this chunk are more detailed than the high-level link-encoder table fields, but they share the same generated DPCS namespace used by DCN316 display resource setup, DIO link encoder programming, RDPCS indexed PHY access, DisplayPort/HDMI link training, lane power management, suspend/resume, hotplug recovery, firmware-assisted PHY flows, and hardware diagnostics.

## Risks

- Generated-header drift is the primary risk. A wrong shift can silently target the wrong bit in a 16-bit PHY register, especially in dense pstate, timer, override, DCC, adaptation, or equalization registers.
- This chunk mixes common CR0 resources with lane-local controls. A bug in RAWCMN supervisor, SRAM, clock, APB, RTUNE, or MPLL calibration fields can affect every lane using the C20 PHY CR0 common block, while lane 0/1 mistakes can appear as lane-specific training or signal-integrity failures.
- Override enable fields are common and dangerous. Setting an override value without its enable bit has no intended effect, while leaving an enable bit asserted after diagnostics can hold TX/RX, calibration, equalization, signal-detect, or power-state logic in a forced state.
- Pstate and power-up timer fields describe sequencing for analog and digital PHY sub-blocks. Partial updates, stale high/low timing halves, or mismatched TX/RX pstate bitmaps can produce intermittent link training, resume, CDR lock, VCO calibration, or DCC calibration failures.
- Status and control fields are represented identically as macros. Consumers need hardware-register knowledge to avoid writing read-only/status bits, clearing sticky diagnostics unexpectedly, or depending on reserved-field behavior.
- Many lane 0 and lane 1 groups are structurally repeated. Copy/paste or generator instance mistakes can swap lane identity or apply a lane 0 value to lane 1, causing asymmetric failures that are hard to diagnose.
- Chunk boundaries cut through register groups: line 99809 is a leftover `C20_PHY_CR0_RAWCMN_DIG_AON_SUP_IN_0` shift from the previous group, and line 102362 stops after only two fields of `C20_PHY_CR0_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0S`. Merge-time validation should account for the adjacent chunks before flagging missing fields.

## Test Signals

Useful validation is mostly generation-time, build-time, and hardware-integration oriented:

- Compile or preprocess AMDGPU display code for DCN316 targets that include `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`.
- Static generator checks that every full-register field has matching `__SHIFT` and `_MASK` definitions in the complete header, with known chunk-boundary exceptions for `C20_PHY_CR0_RAWCMN_DIG_AON_SUP_IN_0` and `C20_PHY_CR0_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0S`.
- Cross-check C20 PHY CR0 register names and bit positions against the DPCS 4.2.3 register database and companion offset header.
- Grep/compile checks for integration with `dcn316_resource.c`, `dcn31_dio_link_encoder.h`, and RDPCS/DPCS register access helper paths.
- Hardware tests on DCN316/DPCS 4.2.3-class ASICs: DP and HDMI link training at multiple rates, lane enable/disable changes, pstate transitions, hotplug, suspend/resume, firmware stop/start interactions, RX detect, signal-detect thresholds, CDR/VCO lock, DCC calibration, RTUNE readiness, and recovery after failed training.
- Diagnostic readback during bring-up should confirm common power/clock status, SRAM init and firmware version reads, MPLL/RTUNE calibration done bits, TX/RX pstate transitions, VCO/CDR status, LBERT/statistic counters, DCC acknowledgements, RX adaptation/DFE status, and cleanup of override-enable bits after diagnostic paths.

## Chunk Notes For Merge

This document is intentionally source-tree aligned and covers only lines 99809-102362 of `dpcs_4_2_3_sh_mask.h`. Earlier chunks should cover the complete `C20_PHY_CR0_RAWCMN_DIG_AON_SUP_IN_0` group and any preceding C20 PHY CR0 RAWCMN fields. Later chunks should continue `C20_PHY_CR0_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0S`, the rest of lane 1 RX power/adaptation/stat/analog-transfer fields, and later C20 PHY or DPCS groups. The final per-file report should treat the whole file as a generated ASIC register bitfield map for AMD display PHY programming rather than handwritten runtime logic.
