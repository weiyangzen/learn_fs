# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 9691-12098

## Scope And Purpose

This chunk is part of AMDGPU's generated DPCS 4.2.3 shift/mask header. It contains C preprocessor constants for display PHY/DPCS hardware register bitfields, not executable code. The range provides `__SHIFT` and `_MASK` definitions used by driver code to pack values into CR0 lane registers or decode status readbacks.

The chunk starts inside the CR0 lane 2 ASIC RX override block, completes most of lane 2's digital and analog TX/RX field definitions, then begins the same generated layout for CR0 lane 3 through early RX statistics control. In this range there are 2,408 lines, 236 register-comment headings, 1,174 shift macros, and 1,017 mask macros. The dominant namespace is `DPCSSYS_CR0_LANE2_*`; the final 41 register headings are `DPCSSYS_CR0_LANE3_*`.

## Register Groups Covered

- `DPCSSYS_CR0_LANE2_DIG_ASIC_*`: RX override inputs for request/data enable/pstate/rate/width, CDR reference and VCO load values, CDR tracking/SSC/alignment, low-power/invert/adaptation/termination/reset controls, RX equalization override values, RX override outputs, lane loopback controls, TX/RX ASIC input and output observation, TX override continuation, and OCLA control.
- `DPCSSYS_CR0_LANE2_DIG_TX_PWRCTL_*`: TX power-state words for P0, P0S, P1, and P2, TX power-up timing words, TX DCC CR-bank and DAC address/data/control/select/ack fields, TX clock alignment, and TX LBERT controls.
- `DPCSSYS_CR0_LANE2_DIG_RX_PWRCTL_*`: RX power-state words for P0, P0S, P1, and P2 plus RX power-up timing fields for VCM, signal detect, DFE enable, and related waits.
- `DPCSSYS_CR0_LANE2_DIG_RX_VCOCAL_*`, `RX_CDR_*`, and `RX_DPLL_*`: RX VCO calibration control/status/timing fields, CDR control/status fields, DPLL frequency, and DPLL frequency bounds.
- `DPCSSYS_CR0_LANE2_DIG_RX_ADPTCTL_*`: RX adaptation configuration words, adaptation reset controls, ATT/VGA/CTLE/DFE tap status, DFE even/odd data and error VDAC offsets, slicer controls, error slicer level, DAC control select fields, and adaptation CR-bank address/data.
- `DPCSSYS_CR0_LANE2_DIG_RX_STAT_*`: RX statistic load/data-mask/match/control/count registers, calibration compare clock control, additional match-control words, statistic stop control, and sample-count fields.
- `DPCSSYS_CR0_LANE2_DIG_MPHY_*`, `DIG_ANA_*`, and `LANE2_ANA_*`: MPHY low-speed RX PWM/termination/stable-count fields, digital-to-analog override outputs for TX/RX controls, TX equalization and DCC DAC overrides, RX VCO/calibration/DAC/AFE/CTLE/scope/slicer/phase controls, analog status words, signal-detect overrides, analog TX override/power/alternate-test-bus/termination/miscellaneous fields, analog RX clock/CDR/slicer/power/squelch/calibration/test-bus fields, and reserved analog words.
- `DPCSSYS_CR0_LANE3_*` start: lane 3 ASIC lane/TX override input/output fields, TX ASIC input/output observation, TX power-state and timing fields, TX DCC bank/DAC fields, TX clock alignment, TX LBERT, and the beginning of RX statistics controls through `RX_STAT_STAT_CTL1`. The next chunk continues lane 3 RX statistic counters.

## Important APIs, Types, And Functions

There are no functions, structs, enums, or runtime APIs in this chunk. The public interface is the generated macro namespace:

- `DPCSSYS_CR0_LANE<n>_<BLOCK>_<REGISTER>__<FIELD>__SHIFT` gives the low bit of a field.
- `DPCSSYS_CR0_LANE<n>_<BLOCK>_<REGISTER>__<FIELD>_MASK` gives the encoded field mask.
- `RESERVED_*` field names document occupied or reserved register bits and should generally be preserved by read-modify-write users.

These macros are meant to be paired with the matching DPCS 4.2.3 register-address header and AMDGPU display register access helpers. Consumers normally use the address macro for a register, use the shift/mask macros from this file to construct or decode field values, then perform MMIO or indirect DPCS register access through display/PHY code.

## Control Flow

This header has no runtime control flow. The implied hardware sequencing comes from the field families:

- Override inputs use a value bit or field paired with an enable bit, such as `*_OVRD_EN`, `EN_*`, or related request/ack bits. Software must program both the value and enable side intentionally when taking TX/RX, equalization, CDR, VCO, termination, reset, or analog control away from normal hardware sequencing.
- Power-state words describe what hardware should assert in each TX/RX state. Fields include analog reference generator, VCM hold, clocks, resets, serial enable, data enable, RX detection, VBOOST, DFE, VCO, CDR, equalization, and calibration enable bits.
- Timing registers provide hardware wait counts for TX and RX bring-up, such as reference-generator enable, clock enable, VCM hold, VBOOST disable, RX detect, reset, serial enable, signal-detect, and DFE timing.
- Calibration and adaptation fields expose knobs and status for VCO calibration, CDR behavior, DPLL bounds, ATT/VGA/CTLE/DFE adaptation, slicer offsets, DAC selection, DCC DAC access, and CR-bank address/data access.
- Statistic and LBERT fields are diagnostic/control surfaces. They configure pattern matching, statistic counters, sample windows, valid-loss handling, compare clocks, loopback bit-error testing, and injected TX test errors.

Lane identity is part of the contract. Lane 2 and lane 3 fields often have identical masks, but code should use the macro with the same lane prefix as the register address being accessed.

## State And Persistence Behavior

The file itself stores no runtime state. It contributes compile-time constants. Runtime state lives in the DPCS CR0 hardware registers affected by driver consumers:

- TX state includes power-state programming, power-up timing, DCC bank/DAC selection, clock alignment, LBERT mode, TX ASIC inputs/outputs, TX override enables, TX equalization cursors, termination codes, DCC DAC overrides, and analog TX power/test-bus/miscellaneous controls.
- RX state includes ASIC RX request/data/pstate/rate/width controls, reset/invert/low-power/termination/adaptation settings, equalization values, CDR/VCO/DPLL calibration state, RX power-state/timing fields, AFE/CTLE/DFE/slicer offsets, signal-detect controls, MPHY low-speed controls, and analog RX clock/CDR/squelch/calibration/test-bus controls.
- Status and observation state includes TX/RX acknowledgements, detect-RX result, adaptation status, VCO calibration status, CDR lock/status, DPLL frequency, DFE tap readbacks, analog status words, statistic counters, sample-count done flags, and valid-loss controls.

Persistence is determined by hardware reset, power gating, mode-set sequencing, link retraining, suspend/resume, and driver writes. Override enables or power-state words can persist until explicitly rewritten or reset, so debug or bring-up code must restore normal hardware-controlled behavior after using these fields.

## Dependencies And Integration Points

- The matching DPCS 4.2.3 address header is required; this `_sh_mask` file only describes bit positions and masks.
- AMDGPU display/PHY code provides the register access layer, field packing helpers, locks, polling loops, and timeout handling.
- Display link training and mode-set paths integrate with TX/RX power controls, clock alignment, lane width/rate/pstate controls, RX adaptation, CDR/VCO calibration, signal detect, and TX/RX acknowledgements.
- Diagnostics and validation tools may use LBERT, statistic counters, match controls, CR-bank access, DCC DAC controls, analog test-bus fields, and OCLA control.
- Power management and reset paths depend on the power-state, timing, reset, calibration, and override fields being consistent across suspend/resume and hotplug retraining.
- The file is generated from ASIC register specifications. Manual edits risk desynchronizing the driver from the hardware definition and should be checked against the generator/spec source.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is imported Linux AMDGPU display hardware metadata. It has no direct Ceph filesystem behavior.

## Risks And Edge Cases

- The range starts mid-family: lane 2 `DIG_ASIC_RX_OVRD_IN_0` begins before line 9691, so this chunk only includes the tail of that register's masks plus subsequent RX override registers. Merge-stage documentation should reconcile the previous chunk boundary.
- The range ends mid-family: lane 3 `DIG_RX_STAT_STAT_CTL1` is complete, but lane 3 RX statistic sample/count registers continue after line 12098.
- Reserved masks are present for nearly every 16-bit register. Read-modify-write code should preserve reserved bits unless the hardware spec requires a fixed write value.
- Override fields are high risk. Leaving override enables asserted can pin reset, data enable, TX/RX disable, low-power state, termination, CDR tracking, VCO load, signal detect, equalization, DCC DAC, or analog controls away from normal link-training logic.
- Multi-bit fields require masking before shifting. Unchecked values can corrupt adjacent control bits in pstate/rate/width, timing counters, VCO load values, DPLL bounds, DFE taps, DAC controls, statistic match masks, and analog calibration codes.
- Polling status fields needs external timeout and reset logic. CDR/VCO/adaptation/statistic status can be transient, stale, or dependent on clock/power sequencing that is not represented in this header.
- Lane 2 and lane 3 layouts are repetitive. Copying a lane 2 macro for a lane 3 register, or vice versa, may compile and produce the same numeric mask while making the code harder to audit and easier to break when generated layouts diverge.

## Test Signals

Useful validation is mainly compile-time, generator-level, and hardware-facing:

- Build AMDGPU display translation units that include `dpcs_4_2_3_sh_mask.h` to catch duplicate macro, missing macro, or include-order issues.
- Generator consistency checks should verify that each non-reserved field has matching `__SHIFT` and `_MASK` definitions, masks align with shifts and widths, and repeated lane 2/lane 3 layouts match the ASIC register source where expected.
- Static review should check that callers use the lane-matched macro prefix, mask values before shifting, and preserve reserved bits during read-modify-write operations.
- Hardware regression coverage should include DisplayPort/HDMI mode set, link training and retraining, hotplug, high-rate link operation, suspend/resume, lane reset, TX/RX power transitions, CDR/VCO calibration, and RX adaptation.
- Diagnostic tests should exercise LBERT controls, RX statistic counters and match controls, DCC CR-bank/DAC access, OCLA selection, analog test-bus fields, signal-detect overrides, and TX/RX override acknowledgements.
- Runtime warning signals include blank or unstable displays, link training failures, repeated retrains, stuck calibration/adaptation polling, incorrect signal-detect or RX-detect results, and regressions limited to lanes 2 or 3.
