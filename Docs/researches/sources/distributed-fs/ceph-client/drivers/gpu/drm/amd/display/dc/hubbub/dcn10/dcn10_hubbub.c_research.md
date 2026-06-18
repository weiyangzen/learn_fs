# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn10/dcn10_hubbub.c

Purpose: Implements the base DCN1 hubbub, the display hub memory arbiter and address-aperture block. It programs watermarks, self-refresh/pstate controls, DCHUB frame-buffer windows, DCC capability decisions, soft reset, global timer, and state readback.

Important APIs and functions: `hubbub1_program_watermarks` composes urgent, stutter, and pstate watermark programming for sets A-D. `hubbub1_program_urgent_watermarks`, `stutter_watermarks`, and `pstate_watermarks` convert nanoseconds to refclk cycles and track pending lower-watermark updates. `hubbub1_update_dchub` programs local/ZFB/mixed AGP and FB apertures. `hubbub1_get_dcc_compression_cap` derives DCC block capability from format, swizzle, scan direction, and DET request sizing. `hubbub1_verify_allow_pstate_change_high` polls debug status and can force pstate allow as a hang avoidance workaround.

Control flow: callers use `hubbub_funcs` installed by `hubbub1_construct`. Watermark programming only lowers values when `safe_to_lower` is true; otherwise pending lower values are reported for later programming. DCC capability flow validates debug policy, pixel format, swizzle, request size, and DCC disable mode before filling output.

State and persistence: `dcn10_hubbub` stores cached watermarks and `debug_test_index_pstate`. Hardware state persists in arbiter, DCHUB, self-refresh, pstate, DCC-derived programming, and aperture registers. Static locals in pstate verification remember previous forced state and max sample.

Dependencies and integration: depends on `dcn10_hubp.h`, `dcn10_hubbub.h`, `reg_helper.h`, DCHUB/DCC structures, and DC debug flags. Integrated by resource pools as the base hubbub vtable and reused by later generations.

Risks and test signals: lowering-watermark rules can leave stale high values if caller misuses `safe_to_lower`. DCC logic mirrors DML and is sensitive to format/swizzle tables. Tests should cover all watermark sets, DCHUB framebuffer modes, DCC formats/swizzles/scan directions, pstate timeout workaround, and global timer/refdiv updates.
