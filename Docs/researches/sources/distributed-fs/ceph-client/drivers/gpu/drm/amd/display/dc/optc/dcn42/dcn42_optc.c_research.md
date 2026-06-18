# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn42/dcn42_optc.c

## Purpose
Implements DCN 4.2 OPTC behavior by composing DCN401/DCN35 logic with DCN42-specific CRC register layout, PWA frame-sync controls, RSMU underflow handling, double-buffer initialization, and custom lock double-buffer programming.

## Important APIs, Types, and Functions
Public functions are `dcn42_timing_generator_init()`, `optc42_enable_pwa()`, `optc42_disable_pwa()`, `optc42_tg_init()`, `optc42_clear_optc_underflow()`, `optc42_is_optc_underflow_occurred()`, `optc42_disable_crtc()`, and `optc42_lock_doublebuffer_enable()`. The static `optc42_get_crc()` reads DCN42's split red/green/blue CRC registers. The vtable delegates most base operations to DCN401 and DCN35 helpers.

## Control Flow and State
CRC readback first checks `OTG_CRC_EN`, then reads engine 0 or 1 results from separate R/G/B registers. PWA enable checks the debug option `enable_otg_frame_sync_pwa`, then programs enable, vcount mode, and line offset; disable clears the enable bit. Underflow clear writes both `OPTC_INPUT_GLOBAL_CONTROL.OPTC_UNDERFLOW_CLEAR` and `OPTC_RSMU_UNDERFLOW.OPTC_RSMU_UNDERFLOW_CLEAR`; status reports either normal or RSMU underflow. Disable delegates to `optc401_disable_crtc()` then clears DCN42 underflow. TG init enables DRR timing double-buffer mode 2 and clears underflow. The custom lock-doublebuffer routine computes blanking positions, programs lock window/update position/vupdate keepout, enables global update lock, and emits a trace event.

## Dependencies and Integration Points
Includes DCN35 and DCN401 headers for reused functions plus `dc_trace.h` for lock/unlock tracing. The vtable uses DCN401 for enable, ODM, DRR, global sync, output mux, vupdate keepout, and update-lock wait; DCN35 for long-vtotal, CRC configuration, wait OTG disable, and FGC clock gating.

## Risks and Test Signals
Risks include CRC field-name mismatches for engine 1, PWA debug gating, RSMU underflow not being cleared on all disable paths, and lock-window arithmetic when `h_blank_start` is small. Tests should cover CRC engine 0/1, PWA enable/disable with debug flag, underflow injection/clear, global update lock tracing, ODM/DCN401 inherited paths, and FGC clock-gating toggles.
