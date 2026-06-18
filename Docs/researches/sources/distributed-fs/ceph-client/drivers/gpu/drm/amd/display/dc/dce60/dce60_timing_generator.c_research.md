## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce60/dce60_timing_generator.c

Purpose: DCE6 timing-generator adapter that inherits most DCE110 behavior while handling DCE6 register offsets, DMIF pixel-duration programming, DCE6 advanced-request differences, and limited CRC support.

Important APIs: `dce60_timing_generator_construct`; static `program_timing`, `program_pix_dur`, `dce60_timing_generator_enable_advanced_request`, `dce60_is_tg_enabled`, and `dce60_configure_crc`. Its `dce60_tg_funcs` table mostly points to DCE110 functions with selected overrides.

Control flow: construction stores caller offsets, derived DCE6 CRTC/DCP offsets, shared timing limits, and the DCE60 vtable. Direct timing programming first writes DMIF pixel duration from `pix_clk_100hz`, then delegates to `dce110_tg_program_timing`. Advanced request updates `CRTC_START_LINE_CONTROL` and `CRTC_CONTROL` because DCE6 stores prefetch enable differently and lacks `CRTC_LEGACY_REQUESTOR_EN`.

State and dependencies: state is inherited `dce110_timing_generator` fields plus derived offsets and DCE6 hardware registers. Dependencies are DCE6 register headers and DCE110 timing APIs. Risks include unused loop index in LPT-like offset macros not relevant here, CRC configure returning true without actual CRC registers, derived offsets not used by shared macros consistently, and pixel-duration only programmed on non-VBIOS path. Test signals are DCE6 direct modesets, advanced request behavior, pixel clock changes, enable-state reporting, and CRC API callers tolerating no hardware CRC.
