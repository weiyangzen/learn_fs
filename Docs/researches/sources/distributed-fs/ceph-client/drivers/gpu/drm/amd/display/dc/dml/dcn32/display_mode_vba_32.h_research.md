# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn32/display_mode_vba_32.h

## Purpose

`display_mode_vba_32.h` declares the public DCN32 DML VBA entry points and DCN32-specific constants used by the implementation. It is the small generation-specific interface that lets the generic DML dispatch layer and DCN32 display code call the DCN32 validator and recalculation routines without exposing the implementation internals.

## Important APIs, Types, And Constants

- `struct display_mode_lib;` is forward-declared so callers can use the public functions without including the full DML library definition through this header alone.
- `void dml32_ModeSupportAndSystemConfigurationFull(struct display_mode_lib *mode_lib);` validates a mode and selects/copies supported state data into `mode_lib->vba`.
- `void dml32_recalculate(struct display_mode_lib *mode_lib);` recalculates selected-state timing, prefetch, watermark, bandwidth, and performance outputs after the generic mode support path has run.
- `__DML_VBA_DEBUG__` is a disabled debug-print switch. Enabling it activates verbose DML trace output in the C implementation.
- `__DML_VBA_ALLOW_DELTA__` is a disabled compatibility switch for DML-C changes that have not propagated to the VBA model.
- `__DML_VBA_MIN_VSTARTUP__` is the minimum vstartup line count used when searching prefetch schedules.
- `__DML_ARB_TO_RET_DELAY__` encodes the ARB-to-DET delay as an ARB-to-SDPIF plus SDPIF-to-DET expression.
- `__DML_MIN_DCFCLK_FACTOR__` is a minimum DCFCLK fudge factor.
- `__DML_MAX_VRATIO_PRE__`, `__DML_MAX_BW_RATIO_PRE__`, and `__DML_VBA_MAX_DST_Y_PRE__` bound prefetch ratio/bandwidth/destination-line behavior.
- `BPP_INVALID` and `BPP_BLENDED_PIPE` are sentinel BPP values.
- `MEM_STROBE_FREQ_MHZ`, `DCFCLK_FREQ_EXTRA_PREFETCH_REQ_MHZ`, and `MEM_STROBE_MAX_DELIVERY_TIME_US` define strobe/DCFCLK thresholds that influence extra prefetch timing in the C implementation.

## Control Flow And Integration

The header includes `../display_mode_enums.h` for enum definitions used by the DCN32 DML implementation and the surrounding display mode library. It does not include `display_mode_lib.h`; instead it forward-declares `struct display_mode_lib`, keeping the interface light.

The two prototypes are consumed by `display_mode_lib.c`, which installs them in the DCN32 DML function table, and by DCN32 display code that needs the DCN32 mode support API. The constants are consumed by `display_mode_vba_32.c` during prefetch/vstartup, DCFCLK, BPP, and strobe-related calculations.

## State And Persistence Behavior

The header itself has no state and performs no persistence. Its functions operate on the caller-owned `struct display_mode_lib` object. The constants become compile-time behavior for all DCN32 calculations in the translation unit that includes this header.

## Dependencies

The direct dependency is `../display_mode_enums.h`. The declared functions require a complete `struct display_mode_lib` definition at the call site or in the C implementation, which is provided by `display_mode_lib.h`. The header guard is `__DML32_DISPLAY_MODE_VBA_H__`.

## Risks And Edge Cases

- The constants are generation-specific and should be treated as DCN32 behavior. Reusing them in another DCN generation without review could produce incorrect clock or prefetch decisions.
- The debug and delta feature switches are compile-time macros. Enabling them changes code paths or build behavior globally for translation units that include this header.
- `__DML_ARB_TO_RET_DELAY__` is defined as `7 + 95` without parentheses. It is safe in simple arithmetic contexts but could surprise if used in a larger macro expression without explicit grouping.
- `BPP_BLENDED_PIPE` uses `0xffffffff`, so call sites should compare it as a sentinel rather than treat it as a normal bits-per-pixel value.

## Test Signals

The header is best validated indirectly:

- compile tests should confirm DCN32 DML builds with the declared prototypes and constants;
- dispatch tests should verify the DCN32 function table calls `dml32_ModeSupportAndSystemConfigurationFull()` and `dml32_recalculate()`;
- mode validation tests should cover configurations around the constants, especially minimum vstartup and max prefetch ratio thresholds;
- macro-change tests should compare golden DML output before and after any adjustment to strobe, DCFCLK, or prefetch constants.
