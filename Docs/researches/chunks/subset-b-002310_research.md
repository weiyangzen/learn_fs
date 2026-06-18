# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 52422-54799

## Scope

This chunk is a generated AMD DPCS 4.2.0 shift/mask header segment for the `DPCSSYS_CR2` register block. It covers 2,378 lines and defines 1,057 `__SHIFT` macros plus 1,095 `_MASK` macros. The unequal count is expected for this sliced range: it begins in the middle of common RTUNE definitions, so some masks or shifts for adjacent fields live outside the chunk boundary.

The content is declarative only. It contains no functions, structs, enums, runtime variables, loops, branches, or persistence logic. Its public surface is the set of C preprocessor constants that describe bit positions and masks for 16-bit DPCS internal registers.

## Purpose

The header gives AMDGPU display code symbolic access to DPCS 4.2.0 hardware register fields. Consumer code combines these constants with addresses from `dpcs_4_2_0_offset.h` and register helper macros to perform read-modify-write operations without hard-coding bit numbers.

This chunk specifically covers:

- The tail of common always-on RTUNE values for common RX/TX termination calibration.
- Common SRAM bring-up, power-gating, reset, supply, reference-range, VREF, and resonance override/status controls.
- Full lane 0 and lane 1 register-field maps for PCS crossbar (`PCS_XF`), lane FSM, IRQ control, PMA crossbar (`PMA_XF`), TX control, RX control, and ATE/test override windows.
- The beginning of lane 2 TX PCS/override field definitions through `DPCSSYS_CR2_RAWLANE2_DIG_PCS_XF_TX_PCS_IN`.

## Exported API Surface

There are no callable APIs or local types. The exported interface is the generated macro namespace, where each register field has a `__SHIFT` constant and a `_MASK` constant.

Important macro families in this range:

- `DPCSSYS_CR2_RAWCMN_DIG_AON_CMN_RTUNE_*`: common RTUNE readback/value fields for RX, TXDN, and TXUP termination calibration slots 6 and 7.
- `DPCSSYS_CR2_RAWCMN_DIG_AON_CMN_SRAM_BL_CFG`: SRAM boot/load controls such as power-gate boot-load enable, ROM selection, bypass, and start.
- `DPCSSYS_CR2_RAWCMN_DIG_AON_CMN_PG_OVRD_*`, `SUP_OVRD_IN`, `RES_OVRD_IN`, and `RES_ASIC_IN_OUT`: common-domain power, reset, reference clock, MPLL force/ack, and request/ack override plumbing.
- `DPCSSYS_CR2_RAWCMN_DIG_AON_CMN_VREF_STATS`, `REF_RANGE_OVRD`, and `MISC_CONF_IN_1`: VREF calibration status, reference range override, and MPLL powerdown timing.
- `DPCSSYS_CR2_RAWLANE{0,1}_DIG_PCS_XF_*`: lane-local PCS TX/RX request, reset, rate, width, pstate, low-power detect, MPLL selection, data enable, loopback, adaptation, equalization, phase calibration, termination, and ATE override fields.
- `DPCSSYS_CR2_RAWLANE{0,1}_DIG_FSM_*`: lane FSM override/status, fast calibration/adaptation state monitor fields, common calibration status, flags, CR lock, TX DCC status, OCLA monitor controls, TX EQ update flag, and RX IQ phase offset.
- `DPCSSYS_CR2_RAWLANE{0,1}_DIG_IRQ_CTL_*`: per-lane IRQ status, clear, mask, and reset-return request fields for RX reset/request/rate/pstate/adaptation, phase-2 calibration, loopback, DCC on-demand, TX reset, and TX request events.
- `DPCSSYS_CR2_RAWLANE{0,1}_DIG_PMA_XF_*`: PMA-facing lane, supply, TX, RX, MPHY, RTUNE, and adaptation override/status fields.
- `DPCSSYS_CR2_RAWLANE{0,1}_DIG_TX_CTL_*` and `RX_CTL_*`: lane-local TX/RX controller knobs and status, including TX FSM control, TX clock control, DCC continuous status, RX FSM control, RX LOS mask control, RX data-enable override, OFFCAN/adaptation continuous status, and UPCS/OCLA observability.
- `DPCSSYS_CR2_RAWLANE2_DIG_PCS_XF_TX_*`: start of the lane 2 PCS TX override/input surface, continuing the same repeated lane pattern in later lines.

## Register Areas Covered

The common AON section exposes cross-lane support state: RTUNE calibration values, SRAM boot/load sequencing, PMA/PCS power stable overrides, power-gate reset/mode overrides, monitor input and analog isolation overrides, MPLLA/MPLLB force and acknowledgement overrides, reference clock enable override, VREF calibration done state, request/ack override routing, reference range override, and MPLL powerdown timing.

The lane 0 and lane 1 PCS crossbar sections are structurally parallel. TX fields cover reset, request, power state, low-power detect, data width/rate, MPLLB selection, MPLL enable, master MPLL state, DETRX request, VBOOST, IBOOST, beacon enable, serial loopback, TX data enable, TX async enable/data, acknowledgement, DETRX result, EN_CTL, and TX DWORD clock sync override. RX fields cover rate/width/pstate/LPD override, AFE/DFE adaptation enables, parallel loopback, RX data enable, LOS/LFPS and threshold overrides, adaptation/off-cancellation continuous mode, VCO/reference load overrides, RX PCS inputs, valid/ack outputs, adaptation acknowledgement, figure-of-merit, directed TX pre/main/post EQ values, lane number, RX EQ delta IQ, termination controls, RX EQ override controls, and phase-2 calibration request/ack.

The FSM sections encode diagnostics and state-machine observability rather than direct high-level software logic. They expose FSM override control, memory address and status monitors, fast RX startup/adaptation/calibration state bits, continuous calibration/adaptation state bits, common MPLL/RCAL status, RX VCO/ref/IQ calibration progression, generic flags, CR lock state, TX DCC flags/status, OCLA capture controls, TX EQ update flag, and RX IQ phase offset.

The IRQ sections define a consistent event model for each lane. Individual event registers and matching clear registers exist for RX reset, RX request, RX rate, RX pstate, RX adaptation request/disable, RX phase-2 calibration request/disable, lane loopback enable, TX reset, TX request, and lane transceiver mode. `IRQ_MASK` and `IRQ_MASK_2` fields gate those events, including DCC on-demand and TX reset/request mask bits.

The PMA and TX/RX controller sections bridge the digital PCS lane controls into analog/PHY-side status and override points. They include lane pstate/ack controls, supply power stable/enable fields, TX ack/data enable/DCC done flags, RX data/valid/adaptation done flags, RTUNE control, MPHY reference clock/DCC/reset/PLL calibration/sleep/termination fields, RX adaptation output override, TX FSM and clock controls, RX LOS and data-enable override controls, and OCLA/UPCS observability.

## Control Flow And State Behavior

This file has no software control flow. Runtime behavior is determined by the driver code that writes fields selected by these masks and by hardware state machines in the DPCS block.

The field names imply several hardware sequences:

- Common-domain bring-up: SRAM boot/load, PMA/PCS power stable indications, power-gate reset/mode, reference clock enable, MPLL force/ack, VREF calibration done, reference range, and MPLL powerdown timing are inputs to link initialization and low-power transitions.
- Per-lane TX/RX activation: TX/RX reset and request bits pair with acknowledgement/status fields; rate, width, pstate, LPD, MPLL select, MPLL enable, and data-enable fields describe the configured link state for each lane.
- Calibration and adaptation: RTUNE, RX AFE/DFE adaptation, OFFCAN continuous mode, VCO/ref load overrides, phase-2 calibration, TX DCC, IQ phase offset, FOM, and directed TX EQ fields expose calibration commands and readbacks.
- Interrupt lifecycle: event bits, clear bits, and mask bits describe a status-clear-mask pattern that consumers must handle with the correct register access semantics.
- Test and debug access: ATE override, OCLA, UPCS_OCLA, FSM memory/status monitor, and MPHY override windows allow manufacturing, validation, or deep debug code to force or observe low-level PHY behavior.

No software state is persisted here. Hardware register contents persist or reset according to ASIC power domains, resets, and firmware/hardware sequencing. Reserved fields are explicitly named in the macros and should be preserved by consumers during read-modify-write operations.

## Dependencies And Integration Points

The syntactic dependency is the C preprocessor. The semantic dependency is the DPCS 4.2.0 register database that generated this file and its companion `dpcs_4_2_0_offset.h` address map.

Within this source tree, `dpcs_4_2_0_sh_mask.h` is included by `drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` together with `dpcs_4_2_0_offset.h`. That ties this generated register contract to the DCN 3.1 resource implementation for Yellow Carp-class display hardware. The matching offset range maps the common registers around `0x203c`-`0x2040`, lane 0 around `0x3000`-`0x30c8`, lane 1 around `0x3100` and later, and lane 2 starting at the next repeated lane window.

Integration points visible from the names include AMD DC link encoder and PHY programming, DisplayPort/HDMI link training, per-lane PMA/PCS control, DPCS interrupt handling, suspend/resume and power-gating flows, firmware or manufacturing ATE paths, and debug/diagnostic paths that inspect FSM, OCLA, calibration, and IRQ state.

## Risks

- Generated-header drift is the main risk. A wrong bit shift or mask can silently change adjacent hardware fields during register updates.
- The lane 0 and lane 1 blocks are highly repetitive. A copy-generation error in only one lane can create asymmetric display-link failures that are hard to reproduce.
- This chunk starts and ends inside larger logical register groups. Merge/reconciliation must avoid assuming the partial RTUNE and lane 2 groups are complete in this chunk alone.
- Many registers mix override enable bits with override value bits. Setting a value bit without its enable bit, or leaving an enable bit asserted after debug/test use, can force hardware away from normal state-machine control.
- IRQ status, clear, and mask fields share very similar names. Consumer code must respect write-one-to-clear or mask polarity semantics from the hardware spec; the mask header alone does not encode those access rules.
- Reserved masks cover large bit ranges. Drivers should preserve reserved bits and avoid treating full-width or reserved fields as safe scratch space.
- Debug/ATE/OCLA/MPHY override fields can interfere with normal link training, power management, and calibration if used outside controlled bring-up or diagnostics.

## Test Signals

Useful validation is mostly build-time, generation-time, and hardware-integration oriented:

- Compile/preprocess AMDGPU DCN 3.1 code that includes `dpcs_4_2_0_sh_mask.h` through `dcn31_resource.c`.
- Static checks that every complete register group has matching `__SHIFT` and `_MASK` definitions; for this sliced chunk, expect 1,057 shifts and 1,095 masks because the line range crosses group boundaries.
- Consistency checks against `dpcs_4_2_0_offset.h` so every register-family prefix in this chunk has a corresponding `ix...` address define.
- Generated-register comparison against adjacent DPCS versions (`dpcs_4_2_2`, `dpcs_4_2_3`, or `dcn_4_1_0` copies) to catch accidental field-width or mask-format changes.
- Runtime display tests on hardware using DPCS 4.2.0: DP and HDMI link training, lane-count/rate changes, hotplug, suspend/resume, low-power entry/exit, RX/TX calibration, DCC/adaptation flows, loopback/debug paths if available, and IRQ clear/mask handling.
- Register readback during bring-up should show expected transitions for power stable, SRAM load, reset/request acknowledgements, VREF calibration done, adaptation acknowledgements, phase-2 calibration request/ack, TX DCC status, FSM flags, and IRQ status/clear behavior.

## Chunk Notes For Merge

This document intentionally covers only lines 52422-54799 of `dpcs_4_2_0_sh_mask.h`. Earlier chunks should cover the preceding common AON RTUNE fields, and later chunks should continue lane 2 and subsequent register blocks. The final merged per-file report should describe the whole file as a generated ASIC bitfield map for DPCS 4.2.0 rather than handwritten driver logic, with `dcn31_resource.c` and the matching offset header as the primary in-tree integration anchors.
