## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_timing_generator_v.c

Purpose: DCE11 underlay/video timing-generator implementation using CRTCV registers. It implements a reduced timing-generator vtable for the underlay pipe.

Important APIs: `dce110_timing_generator_v_construct` and static callbacks for enable/disable, blank/unblank, direct blanking programming, advanced request, colors, vblank counter, waits, and unsupported sync operations. It reuses `dce110_tg_validate_timing`, `dce110_timing_generator_program_timing_generator`, and `dce110_is_two_pixels_per_container`.

Control flow: construction assigns `CONTROLLER_ID_UNDERLAY0`, installs the underlay vtable, and initializes DCE11 timing limits. Program timing either delegates to the shared VBIOS timing routine or writes CRTCV timing, sync, polarity, and interlace registers. Unsupported timing sync/global swap/reset callbacks log errors and return.

State and dependencies: state is mostly CRTCV hardware registers and inherited timing-limit fields. Dependencies include DCE11 register headers and the shared DCE110 timing header. Risks include no `get_position` callback, unsupported sync/reset behavior, direct CRTCV register use without instance offsets, potential typo in early-control writing `mmCRTC_CONTROL`, and limited validation inherited from DCE110. Test signals are underlay modeset, blank/unblank, color programming, vblank waits, and graceful handling when higher layers request unsupported synchronization.
