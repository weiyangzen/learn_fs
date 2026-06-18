# sources/distributed-fs/ceph-client/include/media/v4l2-dv-timings.h

Purpose: declares helper APIs for digital-video timing calculation, validation, enumeration, matching, CVT/GTF detection, EDID physical-address handling, HDMI colorimetry, and optional debugfs HDMI InfoFrame export.

Important APIs/types: `v4l2_calc_timeperframe()` derives frame period from pixel clock and blanking totals. `v4l2_dv_timings_presets[]` is the preset timing database. `v4l2_check_dv_timings_fnc` lets drivers add hardware-specific validation. `v4l2_valid_dv_timings()`, `v4l2_enum_dv_timings_cap()`, `v4l2_find_dv_timings_cap()`, `v4l2_find_dv_timings_cea861_vic()`, and `v4l2_match_dv_timings()` validate and normalize modes. `v4l2_detect_cvt()` and `v4l2_detect_gtf()` infer standard timings from measured sync values. `struct v4l2_hdmi_colorimetry` and `v4l2_hdmi_rx_colorimetry()` translate HDMI infoframes into V4L2 colorspace fields.

Control flow: HDMI/receiver drivers measure a mode or parse EDID, call validation/enumeration against `v4l2_dv_timings_cap`, optionally pass a driver callback, and expose results through DV-timings ioctls. Detection helpers map raw sync/frequency observations to CVT/GTF timing structures. EDID helpers count blocks and read/write/validate CEC physical addresses.

State and persistence: helpers are mostly stateless. Persistent data is caller-owned `v4l2_dv_timings`, EDID buffers, and optional `struct v4l2_debugfs_if` allocated by `v4l2_debugfs_if_alloc()` when debugfs is enabled. `can_reduce_fps()` is an inline predicate based on BT timing standards, vsync, and reduced-FPS flags.

Dependencies and integration: includes debugfs and videodev2; integrates with `v4l2-ioctl.h` DV timing callbacks, HDMI infoframe structures, CEC physical addressing, and debugfs. The debugfs allocation/free APIs become NULL/no-op stubs without `CONFIG_DEBUG_FS`.

Risks: invalid or partially filled timing structs produce wrong frame periods; too-wide `pclock_delta` can match the wrong mode; relying on reduced-FPS matching inconsistently can accept incompatible timings; EDID mutation must respect buffer size and checksum expectations in implementation; and debugfs readers must bound output to `V4L2_DEBUGFS_IF_MAX_LEN`.

Test signals: enumerate supported presets across caps, match measured timings with pclock tolerance, CVT/GTF detection for interlaced and reduced-blanking modes, CEA-861 VIC lookup, aspect-ratio calculation from EDID bytes and timings, EDID physical-address validation for parent/port extraction, and debugfs allocation under enabled/disabled config.
