# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-vbi-out.c

Purpose: implements Vivid raw and sliced VBI output support. It exposes VBI output queue operations and format ioctls, and parses sliced VBI output buffers so capture loopback can reuse WSS and closed-caption data.

Important APIs and functions: exported symbols are `vivid_vbi_out_qops`, `vidioc_g_fmt_vbi_out`, `vidioc_s_fmt_vbi_out`, `vidioc_g_fmt_sliced_vbi_out`, `vidioc_try_fmt_sliced_vbi_out`, `vidioc_s_fmt_sliced_vbi_out`, and `vivid_sliced_vbi_out_process`. Internal vb2 callbacks handle queue setup, prepare, queue, start/stop streaming, and request completion.

Control flow: queue setup/prepare validate raw or sliced VBI output buffer sizes based on output standard. Starting joins the shared output kthread through `vivid_start_generating_vid_out`; stopping leaves the output thread and clears cached WSS/CC flags. Format setters select raw vs sliced queue type and service set when the queue is idle. `vivid_sliced_vbi_out_process` scans completed sliced records, caches field-0/field-1 CC bytes for 525-line output and WSS bytes for 625-line output.

State and persistence: state is volatile in `struct vivid_dev`: VBI output active list, service set, stream mode, cached CC/WSS data and valid flags, output standard, and sequence counters. Cached CC/WSS state persists until another sliced output buffer or stream stop clears it.

Dependencies and integration points: depends on V4L2 VBI structures, videobuf2, shared output kthread, Vivid core, and `vivid_fill_service_lines` from VBI capture support. Capture loopback reads the cached WSS/CC fields.

Risks: raw VBI output payload itself is not parsed in this file; only sliced output affects loopback. Queue type is mutated on the video_device queue when format changes, so userspace must not change formats while busy. The raw output format uses `dev->vbi_cap_interlaced` for flags, tying output raw format to a capture-side control.

Test signals: raw/sliced VBI output format switching, queue size checks, streamoff clearing cached data, output-to-capture CC/WSS loopback, service set negotiation for 525/625 standards, request completion, and v4l2-compliance VBI output tests validate this file.
