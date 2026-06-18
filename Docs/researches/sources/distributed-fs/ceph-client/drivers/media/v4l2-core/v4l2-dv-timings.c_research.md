# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-dv-timings.c

## Purpose
`v4l2-dv-timings.c` provides helpers for digital video timings, EDID-derived information, HDMI colorimetry, CEC physical-address handling, and optional debugfs InfoFrame exposure. It contains a large table of standard CEA and DMT timing presets and algorithms for validating, matching, deriving, printing, and detecting timing modes.

## Important APIs, Types, and Functions
Key exported data is `v4l2_dv_timings_presets`. Timing helpers include `v4l2_valid_dv_timings`, `v4l2_enum_dv_timings_cap`, `v4l2_find_dv_timings_cap`, `v4l2_find_dv_timings_cea861_vic`, `v4l2_match_dv_timings`, `v4l2_print_dv_timings`, `v4l2_dv_timings_aspect_ratio`, `v4l2_calc_timeperframe`, `v4l2_detect_cvt`, and `v4l2_detect_gtf`. EDID and HDMI helpers include `v4l2_calc_aspect_ratio`, `v4l2_hdmi_rx_colorimetry`, `v4l2_num_edid_blocks`, `v4l2_get_edid_phys_addr`, `v4l2_set_edid_phys_addr`, `v4l2_phys_addr_for_input`, and `v4l2_phys_addr_validate`. Under `CONFIG_DEBUG_FS`, `v4l2_debugfs_if_alloc` and `v4l2_debugfs_if_free` create InfoFrame debugfs files.

## Control Flow
Validation starts with `v4l2_valid_dv_timings`: it accepts only `V4L2_DV_BT_656_1120`, enforces capability bounds for width, height, pixel clock, standard flags, interlaced/progressive support, and sanity bounds for porch/sync fields, then calls an optional driver callback. Enumeration and preset lookup iterate `v4l2_dv_timings_presets`, using validation and matching to return the requested index or convert a measured timing to a known preset while preserving reduced-FPS flags where appropriate.

Timing matching compares type, active dimensions, interlace, polarity, pixel clock within a caller-supplied delta, blanking fields, optional reduced-FPS flags, and interlaced bottom-field fields. Printing derives total frame width/height, frame rate, porch/sync values, pixel clock, flags, standards, aspect, CEA VIC, and HDMI VIC. Aspect and frame-period helpers reduce rational values using `rational_best_approximation`.

`v4l2_detect_cvt` implements CVT and reduced-blanking V1/V2 detection from measured frame height, horizontal frequency, vsync, active width, polarity, and interlace. It derives vertical blanking, active dimensions, horizontal blanking, pixel clock, porch/sync fields, flags, then validates the candidate against capabilities. `v4l2_detect_gtf` performs the same role for default or secondary GTF, using the supplied or default aspect ratio. HDMI colorimetry maps AVI/vendor InfoFrame fields to V4L2 colorspace, YCbCr encoding, quantization, and transfer function. EDID helpers compute block counts, manipulate CEC source physical addresses, update checksums, and validate parent/port hierarchy.

## State and Persistence Behavior
Most functions are pure computations over caller-provided structs. State mutation is limited to output structs, EDID byte arrays, and debugfs allocation. `v4l2_set_edid_phys_addr` mutates EDID in memory and recomputes the affected block checksum. Debugfs helpers allocate a `v4l2_debugfs_if` object and files under an existing dentry; cleanup removes that subtree.

## Dependencies and Integration Points
The file depends on V4L2 DV timing definitions, HDMI InfoFrame structs, CEC EDID helpers, rational arithmetic, 64-bit division helpers, debugfs, and kernel logging. It is used by receiver/transmitter drivers, ioctl handlers for DV timings, HDMI capture drivers, CEC/EDID handling, and debug tooling that exposes InfoFrames.

## Risks
Arithmetic overflow and rounding are central risks, especially pixel clock and blanking calculations that combine dimensions and horizontal frequencies. Capability validation must reject malformed timings without excluding legitimate custom modes. EDID handling relies on exact byte offsets and checksum updates; incorrect source physical address handling can break CEC routing. HDMI colorimetry support explicitly does not cover all newer HDR/DCI-P3 cases. Debugfs allocation is optional and must tolerate missing roots or callbacks.

## Test Signals
Test with preset enumeration across representative caps, custom timing validation boundaries, CVT/GTF generated modelines, reduced-blanking V1/V2 detection, interlaced half-line modes, EDID block count edge cases including EEODB, CEC physical-address parent/port derivation, EDID checksum changes after physical-address writes, and HDMI InfoFrame colorimetry cases for RGB, YCbCr, limited/full range, BT.601, BT.709, xvYCC, opRGB, and BT.2020.
