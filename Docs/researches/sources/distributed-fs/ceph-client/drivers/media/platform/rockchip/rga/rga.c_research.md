# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rga/rga.c

Purpose: implements the Rockchip RGA platform driver and V4L2 mem2mem device. It handles probe/remove, runtime PM, V4L2 file operations/ioctls, format and selection management, controls, interrupt completion, and mem2mem job dispatch.

Important APIs/functions: `device_run()` selects the next source/destination buffers and calls `rga_hw_start()`. `rga_isr()` acknowledges interrupts, completes buffers, copies metadata, advances sequences, and finishes the mem2mem job. `queue_init()` initializes output/capture VB2 queues. `rga_setup_ctrls()` installs HFLIP, VFLIP, ROTATE, and BG_COLOR controls. IOCTL helpers enumerate formats, get/try/set formats, and get/set crop/compose selections. `rga_probe()` parses DT resources, initializes V4L2/mem2mem/video devices, reads hardware version, allocates the command buffer, and registers `/dev/video*`.

Control flow/state: each open file gets an `rga_ctx` with default input/output frames and an m2m context. Format set is rejected while the corresponding queue is busy, stores frame geometry/stride/size/colorspace, and resets crop. Selection set validates positive in-bounds crop/compose rectangles with min dimensions. Runtime PM enables clocks on streaming start and during version read. `rga->curr` tracks the running context until IRQ completion clears it.

Dependencies/integration: depends on platform resources, reset controls named `core`/`axi`/`ahb`, clocks `sclk`/`aclk`/`hclk`, 32-bit DMA mask, V4L2 mem2mem, VB2 DMA-SG queue ops from `rga-buf.c`, and hardware programming in `rga-hw.c`.

Risks and test signals: interrupt handling assumes one current job and a done bit `0x04`. Probe error unwinding must release V4L2, mem2mem, video, PM, and DMA resources correctly. Format/crop validation is simple and may not enforce every hardware alignment constraint. Test probe/remove deferral/errors, runtime suspend/resume clocks, IRQ completion, streamon/off, format changes while busy, all supported formats, crop/compose bounds, controls under load, and 32-bit DMA restrictions.
