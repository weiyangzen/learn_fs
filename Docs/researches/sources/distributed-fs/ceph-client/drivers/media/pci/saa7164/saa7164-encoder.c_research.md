<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-encoder.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-encoder.c

Purpose: V4L2 MPEG encoder node support for SAA7164 analog encoder ports. It exposes read-only MPEG capture, tuner/input/frequency controls, MPEG/AV controls, and dynamic DMA/user-buffer allocation for MPEG-TS or MPEG-PS reads.

Important APIs, types, and functions: `saa7164_encoder_register()` creates the V4L2 video device and control handler. `saa7164_s_std()`, `saa7164_s_input()`, and `saa7164_s_frequency()` update cached port state and firmware/tuner settings. `saa7164_s_ctrl()` maps V4L2 controls to firmware API calls or cached encoder params. `fops_read()` and `fops_poll()` lazily start streaming. `saa7164_encoder_start_streaming()` allocates DMA/read buffers, configures encoder, programs buffer descriptors, and transitions firmware to run.

Control flow: registration seeds NTSC defaults and hardware controls. First reader/poller initializes DIF/audio, starts DMA, then waits for user buffers filled by core deferred IRQ work. Reads copy whole or partial user buffers to userspace and recycle them to the free list. Last close decrements the reader count and stops/free buffers.

State and persistence: persistent runtime state is in `saa7164_port`: standard, dimensions, input, frequency, controls, encoder params, reader count, DMA queue, used/free read queues, and wait queue. No disk persistence is used.

Dependencies and integration points: V4L2 file/ioctl/control framework, DVB frontend tuner analog ops, SAA7164 firmware API for DIF, mux, user controls, audio, encoder, buffer helpers, and core IRQ work.

Risks: read and poll both start capture, so user applications can allocate substantial buffers without an explicit stream-on operation. Buffer allocation result is not checked before subsequent configuration. Multi-reader behavior depends on atomic per-file and per-port counters, while only one hardware stream exists. Frequency setting assumes matching TS port has a frontend with analog tuner ops.

Test signals: V4L2 capability/ioctl checks, MPEG TS/PS reads, nonblocking `-EAGAIN`, blocking wakeups, control changes reflected in firmware, last-close cleanup, CRC guard warnings absent, and analog tuner frequency changes on both encoder ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-encoder.c -->
