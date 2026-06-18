# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_modes.c

## Purpose
This file implements DRM display-mode creation, destruction, timing generation, conversion, comparison, validation, list maintenance, command-line mode parsing, userspace modeinfo conversion, and HDMI YCbCr 4:2:0 capability helpers. It is the core shared modeline utility library for KMS drivers and connector probing.

## Important APIs, Types, and Functions
Allocation and list APIs include `drm_mode_create()`, `drm_mode_destroy()`, `drm_mode_duplicate()`, `drm_mode_copy()`, `drm_mode_init()`, `drm_mode_probed_add()`, `drm_connector_list_update()`, `drm_mode_sort()`, `drm_mode_prune_invalid()`, and `drm_set_preferred_mode()`.

Timing generation includes `drm_analog_tv_mode()` with `fill_analog_mode()`, `drm_cvt_mode()`, `drm_gtf_mode_complex()`, and `drm_gtf_mode()`. Conversion helpers include `drm_display_mode_from_videomode()`, `drm_display_mode_to_videomode()`, `drm_bus_flags_from_videomode()`, `of_get_drm_display_mode()`, `of_get_drm_panel_display_mode()`, `drm_mode_convert_to_umode()`, and `drm_mode_convert_umode()`.

Timing/query helpers include `drm_mode_set_name()`, `drm_mode_vrefresh()`, `drm_mode_get_hv_timing()`, and `drm_mode_set_crtcinfo()`. Matching and validation include `drm_mode_match()`, `drm_mode_equal()`, no-clock variants, `drm_mode_validate_driver()`, `drm_mode_validate_size()`, `drm_mode_validate_ycbcr420()`, and `drm_get_mode_status_name()`. Command-line parsing is exposed through `drm_mode_parse_command_line_for_connector()` and `drm_mode_create_from_cmdline_mode()`. HDMI 4:2:0 helpers are `drm_mode_is_420_only()`, `drm_mode_is_420_also()`, and `drm_mode_is_420()`.

## Control Flow
Mode generation allocates a cleared `drm_display_mode`, computes timing fields, sets flags/name, and returns the object or frees it on error. Analog TV generation chooses NTSC-like or PAL-like timing parameter tables, validates horizontal and vertical durations, and has a BT.601 exception for 13.5 MHz modes up to 720 active pixels. CVT and GTF paths implement integer versions of the VESA algorithms, including reduced blanking, margins, interlace, and sync polarity decisions.

Mode list update moves probed modes into the connector's active mode list under the mode_config mutex, merges duplicates, replaces stale modes, and prefers preferred-mode timings when duplicates differ slightly. Sorting ranks preferred modes first, then resolution, refresh rate, and clock. Pruning deletes non-OK modes and logs user-defined or verbose rejection details.

Command-line parsing splits a connector mode option into mode/name, bpp, refresh, extras, and comma options. It supports numeric modes with `M`/`R`, named analog modes such as NTSC/PAL, force flags, interlace, margins, rotation/reflection, TV margins, panel orientation, and TV mode. Conversion from parsed command-line mode chooses named analog, CVT, or GTF generation, marks the result user-defined, fixes 1366x768 where needed, and computes CRTC info.

## State and Persistence Behavior
The file mostly manipulates caller-owned `struct drm_display_mode` objects and connector mode lists. Modes persist until destroyed or moved between lists. Mode `status`, `type`, `flags`, aspect ratio, CRTC-adjusted fields, and name are cached in the mode object. Command-line parse output is stored in a caller-provided `struct drm_cmdline_mode`. No global mutable runtime state is kept beyond static timing and named-mode tables.

## Dependencies and Integration Points
Dependencies include Linux list sorting, OF/videomode helpers when enabled, framebuffer timing macros, DRM EDID/CEA mode matching, connector display info, mode_config driver `mode_valid` hooks, and uapi `drm_mode_modeinfo`. It integrates with connector probing, EDID processing, Device Tree panel timings, boot command-line connector forcing, HDMI sink capability parsing, and userspace mode ioctls.

## Risks
Timing math uses integer arithmetic and multiple unit conversions; overflow and rounding are handled in some paths but remain a risk when extending formulas. `drm_mode_vrefresh()` returns 0 on overflow or invalid totals, which can affect sorting. Command-line parsing is strict and order-sensitive; accepting new options can break syntax if delimiters are mishandled. Aspect ratio is stored differently in kernel modes and userspace flags, so conversion must clear and rebuild those bits. Connector list update assumes the mode_config mutex is held. 4:2:0 helpers depend on CEA VIC matching; non-CEA modes will not map to the HDMI bitmaps.

## Test Signals
Signals include generated CVT/GTF/analog modes matching known modelines, invalid analog timings returning NULL, videomode and OF timing round trips, correct mode names and vrefresh for interlace/doublescan/vscan/stereo cases, duplicate probed modes merging as expected, invalid modes pruned with correct status strings, command-line parser coverage for numeric, named, forced, rotated, and TV-margin options, userspace modeinfo conversion rejecting bad aspect flags and invalid driver modes, and YCbCr 4:2:0 filters matching EDID capability bitmaps.
