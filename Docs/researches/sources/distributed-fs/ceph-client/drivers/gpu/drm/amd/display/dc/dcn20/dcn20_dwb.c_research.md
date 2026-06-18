# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/dcn20_dwb.c

## Purpose
Implements DCN2.0 display writeback controller behavior, including converter configuration, enable/disable, update, scaler programming dispatch, stereo/new-content controls, and warmup control.

## Important APIs, Types, And Functions
`dwb2_get_caps()` reports one DCN2 writeback pipe with DWB support but no OGAM/OCSC and `support_wbscl = false` despite scaler programming paths. `dwb2_config_dwb_cnv()` programs source size, optional crop window, capture rate, and output BPC. `dwb2_enable()` validates no luma scaling, enables WB, programs CNV/scaler, enables frame capture, and disables warmup. `dwb2_update()` handles locked/unlocked CNV updates. Exported helpers include `dwb2_disable()`, `dwb2_is_enabled()`, `dwb2_set_stereo()`, `dwb2_set_new_content()`, and `dwb2_set_scaler()`.

## Control Flow
Enable/update both reject source dimensions that differ from destination dimensions, allowing only chroma/subsampling behavior. Update checks `CNV_UPDATE_LOCK`; if not already locked it locks, programs CNV and scaler, then unlocks. Scaler programming sets WBSCL mode/depth, destination size, rounding, clamp, outside-pixel strategy, selects cropped or full source size, calls horizontal and vertical scaler helpers, then toggles coefficient RAM if the hardware exposes the select mask.

## State And Persistence
Persistent state is DWB/CNV/WBSCL hardware registers, including frame capture enable, crop windows, scaler coefficient RAM, stereo/new-content bits, and warmup mode. The `dcn20_dwbc` object stores register descriptor pointers and function table.

## Dependencies And Integration Points
Depends on `dcn20_dwb.h`, common `dwb` params, `resource`, `reg_helper`, and the scalar functions in `dcn20_dwb_scl.c`. Integrated through `dwbc_funcs` used by capture/writeback flows.

## Risks
The dimension check forbids luma scaling, so callers must understand DCN2 limitations. `support_wbscl = false` can conflict with the presence of scaler code if capability consumers interpret it strictly. Update lock ownership is subtle: if caller pre-locks, this function leaves unlock responsibility to caller. Coefficient RAM toggle only occurs if mask is nonzero.

## Test Signals
Enable, update, disable, and `is_enabled` register readback; crop/no-crop capture tests; stereo bit programming; update while pre-locked vs unlocked; and invalid luma-scaling rejection are important test signals.
