<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-vbi.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-vbi.c

Purpose: V4L2 raw VBI capture support for SAA7164 VBI ports. It mirrors encoder read-buffer behavior while delegating analog input, standard, tuner, and frequency operations to the paired encoder port.

Important APIs, types, and functions: `saa7164_vbi_register()` creates a VBI video device and links `port->enc_port`. `saa7164_vbi_start_streaming()` allocates DMA/user buffers, configures hardware buffers, negotiates VBI format, and transitions firmware to run. `fops_read()` and `fops_poll()` lazily start capture and consume read buffers. `saa7164_vbi_fmt()` reports fixed NTSC raw VBI geometry.

Control flow: registration only creates the node. First read/poll initializes VBI parameters from the encoder port, starts DMA, waits for buffers copied by core deferred IRQ work, then copies data to userspace. Last close stops firmware, recycles/free buffers, and releases filehandle state.

State and persistence: VBI state is in the VBI `saa7164_port`: VBI params, DMA queue, used/free read queues, reader count, wait queue, and paired encoder pointer. It uses encoder-port state for standard/input/frequency.

Dependencies and integration points: V4L2 VBI file/ioctl framework, SAA7164 firmware VBI format API, buffer helpers, core IRQ work, and encoder helper functions for shared analog controls.

Risks: VBI geometry is NTSC-specific despite shared norms. Start path does not check allocation failure before configuring buffers. Failed `video_register_device()` may leak the allocated video device according to an in-code TODO. Poll can block for data, which is unusual for poll paths.

Test signals: VBI node creation, `VIDIOC_G_FMT_VBI_CAP`, paired encoder input/frequency changes, blocking and nonblocking VBI reads, start/stop on first/last reader, format negotiation failures, and clean unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-vbi.c -->
