# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn30/dcn30_hubbub.c

Purpose: Implements DCN3 hubbub behavior. It builds on DCN21 watermark programming, updates VM aperture initialization, extends DCC swizzle/control support, and adds force/readback utilities for watermark and pstate handling.

Important APIs and functions: `hubbub3_init_dchub_sys_ctx` programs system FB/AGP aperture and VMID0. `hubbub3_program_watermarks` delegates urgent/stutter/pstate programming to DCN21 helpers, sets SAT/outstanding thresholds, and conditionally updates self-refresh. `hubbub3_dcc_support_swizzle` supports standard, render, and display swizzle modes including non-X render variants. `hubbub3_get_dcc_compression_cap` fills newer DCC control bitfields. `hubbub3_force_wm_propagate_to_pipes`, `force_pstate_change_control`, `init_watermarks`, and `read_reg_state` provide operational/debug controls.

Control flow: constructor installs a DCN30 function table using DCN2 update/VM/readback helpers, DCN3 DCC helpers, DCN21 watermark readback, and DCN3 force utilities. Watermark programming mirrors DCN21 but only toggles self-refresh when lowering is safe or stutter is disabled.

State and persistence: uses `dcn20_hubbub` cached watermarks and VMID state; detile buffer is 184 KiB for DCN3. Hardware state includes VM apertures, DCC control decisions, watermarks, pstate force bits, DET/compbuf registers, and copied initial watermark sets.

Dependencies and integration: depends on `dcn30_hubbub.h`, DCN20 VMID setup, DCN21 watermark helpers, and register helper macros. Integrated by DCN30 resource pools.

Risks and test signals: DCC capability output changed to set control flags, so consumers must handle both legacy max block fields and new flags. Conditional self-refresh update can leave previous force state if callers do not prepare bandwidth correctly. Tests should cover DCC swizzle matrix, watermark initialization copy from set A to B-D, pstate force toggles, DET/compbuf readback, and system aperture/VMID0 programming.
