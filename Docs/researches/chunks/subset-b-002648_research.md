# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_offset.h lines 7471-7503

## Purpose

This chunk closes the generated GC 9.2.1 register-offset header with the tail of the DIDT TCP register block, the shared DIDT stall telemetry counters, late `CTRL1`/EDC threshold offsets, and the final include-guard `#endif`.

The constants are indirect-register offsets (`ixDIDT_*`) for Dynamic Inductive Droop Throttling logic in AMD's graphics core. The TCP entries cover stall-pattern programming, throttle timing, weights, EDC control, EDC stall patterns, and EDC stall delays:

- `ixDIDT_TCP_STALL_PATTERN_5_6` through `ixDIDT_TCP_STALL_PATTERN_7` at `0x006a`-`0x006b`.
- `ixDIDT_TCP_MPD_SCALE_FACTOR` and `ixDIDT_TCP_THROTTLE_CNTL0/1/STATUS` at `0x006c`-`0x006f`.
- `ixDIDT_TCP_WEIGHT0_3`, `ixDIDT_TCP_WEIGHT4_7`, and `ixDIDT_TCP_WEIGHT8_11` at `0x0070`-`0x0072`.
- `ixDIDT_TCP_EDC_CTRL`, `ixDIDT_TCP_THROTTLE_CTRL`, EDC stall-pattern registers, and EDC stall-delay registers at `0x0073`-`0x007b`.
- shared stall-event counters for SQ, DB, TD, TCP, and DBR at `0x00a0`-`0x00a4`.
- `CTRL1` and EDC threshold offsets for SQ, DB, TD, and TCP at `0x00b0`-`0x00b7`.

## Important APIs, Types, And Data

The chunk contains only preprocessor constants. It defines no functions, structs, enums, storage, or callable APIs. Its API surface is the symbolic offset namespace consumed by AMDGPU and PowerPlay register helpers:

- `ixDIDT_TCP_*` names select TCP-domain DIDT indirect registers.
- `ixDIDT_{SQ,DB,TD,TCP,DBR}_STALL_EVENT_COUNTER` names 32-bit hardware counters for stall-event telemetry.
- `ixDIDT_{SQ,DB,TD,TCP}_CTRL1` names min/max power limit registers.
- `ixDIDT_{SQ,DB,TD,TCP}_EDC_THRESHOLD` names full-width EDC threshold registers.

The sibling `gc_9_2_1_sh_mask.h` file supplies the field contracts for these offsets. Important fields include two 15-bit stall-pattern fields in `DIDT_TCP_STALL_PATTERN_5_6`, one 15-bit field in `DIDT_TCP_STALL_PATTERN_7`, 4-bit MPD scale fields in `DIDT_TCP_MPD_SCALE_FACTOR`, enable/release-delay fields in `DIDT_TCP_THROTTLE_CNTL0/1`, an FSM-state field in `DIDT_TCP_THROTTLE_CNTL_STATUS`, byte-wide DIDT weights in the three weight registers, EDC enable/reset/force-stall/policy bits in `DIDT_TCP_EDC_CTRL`, `PCC_STALL_EN` in `DIDT_TCP_THROTTLE_CTRL`, and full-width masks for the stall counters and EDC thresholds.

## Control Flow

There is no executable control flow in this header fragment. At compile time, the C preprocessor binds symbolic register names to literal indirect offsets. Runtime flow is supplied by callers that pass these macros to DIDT indexed-register accessors or table-driven configuration code.

The closest local integration pattern is `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_powertune.c`. That file uses arrays of `struct vega10_didt_config_reg` entries to program DIDT registers by offset, mask, shift, and value. In that path:

- `SEDiDtCtrl1Config_Vega10` writes `ixDIDT_TCP_CTRL1` with `MIN_POWER` and `MAX_POWER` fields.
- `SEDiDtWeightConfig_Vega10` writes `ixDIDT_TCP_WEIGHT0_3`, `ixDIDT_TCP_WEIGHT4_7`, and `ixDIDT_TCP_WEIGHT8_11`.
- `SEDiDtStallPatternConfig_Vega10`, `SEEDCStallPatternConfig_Vega10`, `SEEDCStallDelayConfig_Vega10`, and `SEEDCThresholdConfig_Vega10` program the TCP stall pattern, EDC stall pattern, EDC stall delay, and threshold offsets from this chunk.
- EDC enable/disable code reads and writes `ixDIDT_TCP_EDC_CTRL` through `cgs_read_ind_register(..., CGS_IND_REG__DIDT, ...)` and `cgs_write_ind_register(..., CGS_IND_REG__DIDT, ...)`.

## State And Persistence Behavior

The macros themselves are stateless compile-time metadata. The state they address is volatile GPU hardware state:

- TCP DIDT weights, throttle controls, stall patterns, EDC controls, EDC stall delays, and threshold registers hold power-management configuration until reset, reprogramming, or relevant power-gating sequences.
- Stall-event counters are hardware counters. The matching mask definitions describe each counter as a full 32-bit `DIDT_STALL_EVENT_COUNTER` field, so sampling code must handle wraparound.
- EDC threshold registers are full-width threshold values. `vega10_powertune.c` programs TCP, TD, and DB thresholds to `0xffffffff` in one table, indicating these can be used as high/disabled-like thresholds depending on the platform policy.
- `CTRL1` min/max power fields are split into two 16-bit fields and are used by PowerTune to bound DIDT power calculations.

No file-system persistence, firmware blob persistence, or software cache is implemented here. Any durable policy is represented elsewhere in driver tables or firmware/platform data, then written into these hardware registers at runtime.

## Dependencies

This chunk depends on generated ASIC register metadata staying synchronized with the GC 9.2.1 hardware specification. Consumers generally need:

- `gc_9_2_1_offset.h` for the offsets in this chunk.
- `gc_9_2_1_sh_mask.h` for shifts and masks used with `REG_SET_FIELD` and table-based masked writes.
- AMDGPU/CGS indirect register accessors for the DIDT space, such as `CGS_IND_REG__DIDT`, `cgs_read_ind_register`, and `cgs_write_ind_register`.
- PowerPlay/SMU policy code that decides whether TCP ramping or EDC ramping is enabled before programming or toggling these registers.

The offsets are generation-specific. GC 9.4.2 keeps the same TCP tail and late threshold/counter offsets, while GC 10.x moves comparable DIDT offsets to different numeric ranges. Older GC 9.0/9.1 headers also differ in where some EDC threshold offsets appear. Cross-generation code must include the correct ASIC header rather than reusing these literals.

## Integration Points

This header fragment integrates with the generated AMDGPU register include tree under `drivers/gpu/drm/amd/include/asic_reg/gc/`. The effective consumers are power-management and diagnostics paths, especially:

- Vega10/GC 9.x PowerTune DIDT configuration tables that write TCP weights, thresholds, stall patterns, and EDC delays.
- EDC enable/disable logic that toggles `DIDT_TCP_EDC_CTRL` based on `PHM_PlatformCaps_TCPRamping`.
- Potential debug or telemetry code that reads the SQ/DB/TD/TCP/DBR stall-event counters.
- Mask/default validation between `*_offset.h`, `*_sh_mask.h`, and any default/reset-value headers generated for the same ASIC family.

## Risks

- A wrong offset can silently program the wrong indirect DIDT register, causing unstable throttling behavior, incorrect power tuning, or misleading telemetry.
- Cross-generation reuse is unsafe because DIDT layout changes across GC families; even similar macro names can have different numeric offsets.
- Stall-event counters are destructive to interpret if another path clears them or resets DIDT while a telemetry reader is sampling.
- 32-bit counters can wrap under heavy activity, so delta calculations must be wraparound-aware.
- EDC control fields include reset, force-stall, and policy bits; incorrect masked writes can disable EDC, force unwanted stalls, or alter throttle policy.
- Since this is generated-style register metadata, hand edits risk diverging from AMD's hardware register source and can be difficult to catch without hardware access.

## Test Signals

Useful validation signals include:

- Compile coverage for GC 9.2.1 AMDGPU code that includes `gc_9_2_1_offset.h` with `gc_9_2_1_sh_mask.h`.
- Static checks that each macro in lines 7471-7500 has a corresponding mask/shift block in `gc_9_2_1_sh_mask.h`.
- Table validation in `vega10_powertune.c` showing masked writes use the expected offsets for TCP weights, stall patterns, EDC delay/pattern, and thresholds.
- Runtime smoke tests on matching GC 9.2.1 hardware that enable TCP ramping, program the DIDT tables, and confirm indirect DIDT reads/writes do not report invalid-register access.
- Telemetry tests that read stall counters before and after load, then verify counter deltas and clear/reset behavior are plausible.
