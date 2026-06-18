# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-touch-cap.c

Purpose: implements the Vivid touch capture node. It exposes touch format/input/stream-parameter ioctls, vb2 queue operations, and synthetic pressure-map generation for repeatable touch gestures.

Important APIs and functions: exported symbols are `vivid_touch_cap_qops`, `vivid_enum_fmt_tch`, `vivid_g_fmt_tch`, `vivid_g_fmt_tch_mplane`, `vivid_g_parm_tch`, `vivid_enum_input_tch`, `vivid_g_input_tch`, `vivid_set_touch`, `vivid_s_input_tch`, and `vivid_fillbuff_tch`. Internal helpers generate noise, pressure blobs, and gesture patterns.

Control flow: `vivid_set_touch` fixes the format to `V4L2_TCH_FMT_DELTA_TD16` with a 21x12 single-plane signed-16 image. Queue setup/prepare validate this size, queue appends buffers to `touch_cap_active`, and start/stop streaming use the touch kthread. `vivid_fillbuff_tch` sets sequence, fills low-level random noise, then cycles through single/double/triple tap, left-to-right motion, zoom in/out, palm press, and multiple-press patterns based on sequence modulo constants.

State and persistence: touch format, timeperframe, sequence counters, and cached random gesture seed live in `struct vivid_dev`. Buffer contents are transient, while selected touch input/format are fixed to a single supported input.

Dependencies and integration points: depends on Vivid core, touch kthread, Vivid video common format conversion, videobuf2, and V4L2 touch pixel formats. Multiplanar get-format uses `fmt_sp2mp` even though the underlying touch format is single-plane.

Risks: random noise and pressure offsets make output nondeterministic at sample values, though gesture timing is deterministic by sequence. Big-endian conversion is conditional at the end; early returns for idle frames before conversion mean noise-only frames may not be byte-swapped on big-endian systems. Only get-format is provided; format is fixed through input setup.

Test signals: format enumeration/get for single- and multi-planar modes, streamparm reporting, input enumeration/set/get, gesture sequence inspection, big-endian sample layout review, stream start/stop cleanup, and `v4l2-compliance` touch node tests validate this module.
