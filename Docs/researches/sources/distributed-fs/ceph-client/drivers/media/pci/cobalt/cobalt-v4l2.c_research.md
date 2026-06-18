<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-v4l2.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-v4l2.c

Purpose: Implements the Cobalt V4L2 video node API, vb2 queue operations, format/timing/input/output/EDID ioctls, stream start/stop hardware programming, and node registration/unregistration.

Important APIs/functions: vb2 ops include `cobalt_queue_setup()`, `cobalt_buf_init()`, `cobalt_buf_queue()`, `cobalt_start_streaming()`, and `cobalt_stop_streaming()`. Hardware setup helpers `cobalt_enable_input()`, `cobalt_enable_output()`, `cobalt_dma_start_streaming()`, and `cobalt_dma_stop_streaming()` program packer, CVI, measurement, freewheel, clock-loss, syncgen, CPLD clock, and DMA. Ioctls cover capabilities, log-status, DV timings, formats, input/output selection, EDID, events, parameters, pixel aspect, and selection. `cobalt_nodes_register()` creates all stream nodes; `cobalt_nodes_unregister()` tears them down.

Control flow: Node registration initializes stream locks, default 1080p60 timing, default format, vb2 queue, video-device fields, and either video device registration or ALSA init. Buffer init builds DMA descriptors from vb2 SG tables. Queueing appends buffers under `irqlock` and chains descriptors. Stream-on programs input/output hardware, resets sequence, and starts DMA from the first queued buffer. Stream-off stops event counters/DMA, returns all queued buffers as errors, and disables measurement/freewheel/clock-loss for capture.

State/persistence: Per-stream V4L2 state includes width/height/stride/bpp/pixfmt/colorspace/timings/input/sequence, queued buffer list, descriptor info, and stability flags. Hardware state includes CVI, packer, VMR, freewheel, clock-loss, syncgen, and subdevice formats/EDID. No persistent storage.

Dependencies/integration: Depends on V4L2/vb2 DMA-SG, ADV subdevice pad/video/audio APIs, Cobalt IRQ/DMA/CPLD modules, generated register maps, and ALSA node creation for audio streams.

Risks: Format changes are blocked only when vb2 is busy; callers must keep format and descriptor sizes consistent. `cobalt_s_fmt_vid_cap()` calls `cobalt_enable_input()` even outside streaming. Output pixelclock programming can fail silently aside from logging if `cobalt_cpld_set_freq()` returns false. Dummy nodes expose only debug-register ops. Queue start assumes at least one queued buffer due to vb2 minimums. Stream-off abort timeout is fixed at 100 ms.

Test signals: v4l2-compliance, capture/output streaming with MMAP/USERPTR/DMABUF/read/write, format negotiation, DV timing changes while idle/busy, EDID get/set, HDMI source-change events, log-status coverage, dummy node behavior, ALSA node registration, and stop/abort behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-v4l2.c -->
