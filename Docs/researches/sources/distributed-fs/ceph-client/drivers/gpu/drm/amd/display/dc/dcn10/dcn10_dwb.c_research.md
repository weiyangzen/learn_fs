# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_dwb.c

## Purpose
Implements the DCN1 display writeback controller base behavior: capability reporting, simple enable/disable, and object construction.

## Important APIs, Types, And Functions
`dwb1_get_caps()` fills `struct dwb_caps` for DCN1.0, reporting two pipes, DWB support, WBSCL support, and no OGAM/OCSC. `dwb1_enable()` disables first, disables writeback clock/memory gating, then sets `WB_ENABLE`. `dwb1_disable()` disables capture and WB, soft-resets the block, and re-enables power gating. `dcn10_dwbc_funcs` publishes these functions. `dcn10_dwbc_construct()` stores context, instance, function table, register map, shifts, and masks.

## Control Flow
Enable calls the vtable `disable()` first to reset the block, programs `WB_EC_CONFIG` gating-disable fields, and enables WB. Disable turns off `CNV_FRAME_CAPTURE_EN`, clears `WB_ENABLE`, pulses `WB_SOFT_RESET`, then restores gating fields. Construction is straight-line assignment.

## State And Persistence
Persistent state is hardware register state for the writeback and converter blocks, plus the function pointer and register-map pointers held in `struct dcn10_dwbc`. No dynamic allocation is performed.

## Dependencies And Integration Points
Depends on `reg_helper`, `resource`, the common `dwb` interface, and `dcn10_dwb.h` register definitions. It integrates through the `dwbc_funcs` interface used by display writeback resource code.

## Risks
Enable ignores detailed `dc_dwb_params`; DCN1 writeback configuration is minimal here. Calling enable while external users expect existing CNV state will reset it via `disable()`. Power-gating field behavior is hardware-specific and can affect hangs or idle power if wrong.

## Test Signals
Check `get_caps` values, successful enable/disable register readback, absence of WB soft-reset hangs, and writeback capture smoke tests on DCN1 hardware where this object is wired in.
