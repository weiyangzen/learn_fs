# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vbi-cap.c

Purpose: implements Vivid raw and sliced VBI capture support. It generates or loops closed-caption/WSS/teletext data, exposes VBI format/capability ioctls, and provides vb2 queue operations for VBI capture streams.

Important APIs and functions: exported APIs are `vivid_raw_vbi_cap_process`, `vivid_sliced_vbi_cap_process`, `vidioc_g_fmt_vbi_cap`, `vidioc_s_fmt_vbi_cap`, `vivid_fill_service_lines`, `vidioc_g_fmt_sliced_vbi_cap`, `vidioc_try_fmt_sliced_vbi_cap`, `vidioc_s_fmt_sliced_vbi_cap`, `vidioc_g_sliced_vbi_cap`, and `vivid_vbi_cap_qops`. Internal helpers include `vivid_sliced_vbi_cap_fill` and `vivid_g_fmt_vbi_cap`.

Control flow: queued VBI buffers join `vbi_cap_active`; start streaming joins the shared capture kthread. Capture processing sets sequence, generates sliced VBI data for 525/625-line standards, optionally substitutes looped WSS/CC data from VBI output, fills raw buffers with blanking level, then renders raw waveforms or copies sliced records when signal mode is valid. Format ioctls derive sizes and service lines from current SDTV standard and configured service set.

State and persistence: state is volatile in `struct vivid_dev`: VBI active list, service set, interlaced flag, generated `vbi_gen` data, output-looped WSS/CC fields, current input standard/signal mode, and sequence counters. Selected sliced capture service set persists until changed.

Dependencies and integration points: depends on V4L2 VBI structures, videobuf2, shared capture kthread, VBI generator, Vivid video common helpers, and Vivid output-loop state from `vivid-vbi-out.c`.

Risks: `vidioc_s_fmt_vbi_cap` and `vidioc_s_fmt_sliced_vbi_cap` check `fmt->type != ... && vb2_is_busy(...)`, which only rejects busy queues when the type is not the expected type; this may be intentional Vivid test behavior but looks suspicious compared with usual busy checks. Raw and sliced sizes depend on current standard, so standard changes while buffers are queued must be controlled. Loopback substitutions rely on output state freshness.

Test signals: raw and sliced VBI capture for 525/625 standards, service set negotiation, VBI output-to-capture loopback for CC/WSS, invalid/no-signal capture behavior, queue size validation, interlaced flag control, and `v4l2-compliance` VBI tests are useful.
