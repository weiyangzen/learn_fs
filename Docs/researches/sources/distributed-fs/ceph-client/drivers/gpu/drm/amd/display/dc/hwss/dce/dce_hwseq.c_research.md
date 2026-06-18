# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce/dce_hwseq.c

Purpose: implements shared DCE hardware sequencer helpers for front-end clock control, pipe update locking, blender mode programming, light sleep or SRAM power-up handling, CRTC clock-source selection, and LUT-use decisions.

Important APIs and functions: `dce_enable_fe_clock()` toggles `DCFE_CLOCK_ENABLE`. `dce_pipe_control_lock()` coordinates vertical update locks for DCP graphics, scaler, blender, and update lock mode, avoiding locking an already blanked pipe and applying a CRTC hblank write workaround when unlocking. `dce60_pipe_control_lock()` is a no-op for SI/DCE6 because that register is absent. `dce_set_blender_mode()` programs feedthrough, blend mode, alpha mode, and multiplied mode. `dce_clock_gating_power_up()` either calls placeholder light-sleep enable helpers or disables SRAM shutdown and enables underlay clock. `dce_crtc_switch_to_clk_src()` selects DP DTO, combo PHY PLL, or legacy PLL pixel-rate sources. `dce_use_lut()` returns true only for ARGB8888/ABGR8888.

Control flow: all functions are direct hardware register updates through `reg_helper`. `dce_pipe_control_lock()` first checks blank state through the timing generator, reads current lock register, modifies relevant fields, conditionally writes blender-specific fields if masks exist, and performs a workaround on unlock. Clock-source switching branches on `clock_source->id` and logs an error for unknown ids.

State and persistence: persistent state is hardware clock, update lock, blender, memory power, underlay clock, and pixel-rate source registers. No heap or file state is used. The helpers may leave update locks set until a matching unlock call, so sequencing discipline is critical.

Dependencies and integration points: includes `dce_hwseq.h`, `reg_helper.h`, private HW sequencer definitions, and core types. It integrates with DCE generation constructors, timing generators, blender programming, clock source programming, and surface format paths.

Risks and test signals: update locks can deadlock visual updates if not released; clock-source selection errors can blank displays; placeholder light-sleep helpers indicate incomplete power optimization. Mask checks handle generation differences, but missing masks can silently skip fields. Signals include DCE modeset, pipe lock/unlock stress, blanked-pipe update tests, multi-plane blending, DP and PLL clock-source switching, SI builds, and format LUT validation.
