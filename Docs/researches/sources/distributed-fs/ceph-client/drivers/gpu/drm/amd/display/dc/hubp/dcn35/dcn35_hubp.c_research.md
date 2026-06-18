# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn35/dcn35_hubp.c

Purpose: implements DCN 3.5 HUBP specialization. It adds fine-grain clock gating control and a DCN 3.5 pixel-format programming path while reusing most DCN 3.x HUBP behavior.

Important APIs and functions: `hubp35_set_fgcg()` toggles `HUBP_FGCG_REP_DIS` with inverted enable semantics. `hubp35_init()` runs `hubp3_init()` and applies the Display Core debug fine-grain clock-gating setting for DCHUB. `hubp35_program_pixel_format()` maps AMD `surface_pixel_format` values to hardware `SURFACE_PIXEL_FORMAT` encodings and programs color channel crossbar fields. `hubp35_program_surface_config()` sequences DCC, tiling, size, rotation, and pixel format. `hubp35_construct()` installs the DCN 3.5 function table and casts DCN 3.5 shift/mask structs to the base DCN 2.0 pointers.

Control flow: after construction, Display Core calls through `dcn35_hubp_funcs`. Surface configuration first controls DCC with `hubp3_dcc_control_sienna_cichlid()`, then tiling, size, rotation, and format. Format programming adjusts crossbar source selection for ABGR-like formats, handles graphics, video, RGBE, and special float/fix formats, and breaks to debugger on unsupported formats.

State and persistence: writes persist in HUBP clock and surface config registers. The function table and register pointers persist in the HUBP object. Pixel format and crossbar writes determine the interpretation of fetched memory; incorrect values persist until a later plane update.

Dependencies and integration points: depends on `dcn35_hubp.h`, `reg_helper`, and inherited DCN 2.x/3.x helpers. It integrates with display debug flags (`enable_fine_grain_clock_gating.bits.dchub`), plane programming, DCC, tiling, and cursor/dmdata inherited from older generations.

Risks and test signals: pixel format mappings are high risk because a wrong numeric encoding or crossbar selection creates color corruption for specific formats. FGC Gating can expose race conditions if clocks gate while registers are still needed. Signals include format sweep tests, RGBE/alpha plane tests, video plane validation, DCC+rotation combinations, clock-gating enabled/disabled boots, and register readback after plane programming.
