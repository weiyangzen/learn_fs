<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gspca.c -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gspca.c

Purpose: `gspca.c` is the shared GSPCA USB camera core. It registers V4L2 video devices, owns vb2 queue integration, manages USB isochronous/bulk URBs, dispatches subdriver callbacks, assembles frames, supports optional input buttons, and handles disconnect and power management.

Important APIs, types, and functions: exported entry points are `gspca_dev_probe()`, `gspca_dev_probe2()`, `gspca_disconnect()`, `gspca_frame_add()`, `gspca_suspend()`, and `gspca_resume()`. URB callbacks include `isoc_irq()`, `bulk_irq()`, and optional `int_irq()`. Streaming setup runs through `gspca_init_transfer()`, `build_isoc_ep_tb()`, `create_urbs()`, and `gspca_stream_off()`. V4L2 operations cover format enumeration, try/set format, frame sizes/intervals, stream parameters, JPEG compression, and vb2 buffer lifecycle.

Control flow: subdrivers call `gspca_dev_probe()`, which allocates `gspca_dev`, initializes V4L2/vb2 state, calls subdriver `config/init/init_controls`, sets a default mode, registers the video device, and starts optional interrupt input. On `STREAMON`, vb2 calls `gspca_start_streaming()`, which chooses endpoints/altsettings, creates URBs, calls subdriver `start`, submits URBs, and resubmits them in completion handlers. Subdriver packet scanners call `gspca_frame_add()` to complete buffers.

State and persistence: `gspca_dev` stores mode, queue, buffer list, URBs, current image pointer/length, sequence, USB error, locks, streaming/present flags, endpoint/altsetting, and PM frozen state. State is per device and freed through V4L2 release.

Dependencies and integration points: depends on Linux USB, V4L2, videobuf2-vmalloc, optional input, and subdriver `sd_desc` contracts.

Risks: frame correctness depends on subdrivers emitting a sane FIRST/INTER/LAST sequence. `gspca_frame_add()` protects buffer list selection but image pointer/length are interrupt-context state. Bandwidth negotiation can fail on crowded USB buses. Test signals include v4l2-compliance basics, repeated stream on/off, no buffer leaks on disconnect, suspend/resume with active streams, and absence of frame overflow logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gspca.c -->
