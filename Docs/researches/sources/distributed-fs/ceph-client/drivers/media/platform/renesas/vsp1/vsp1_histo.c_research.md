# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_histo.c

Purpose: shared implementation for VSP1 histogram metadata entities. It combines a V4L2 subdevice for image-side statistics sampling with a V4L2 metadata capture video node and vb2-vmalloc queue for readout buffers.

Important APIs and functions: `vsp1_histogram_init()`, `vsp1_histogram_destroy()`, `vsp1_histogram_buffer_get()`, `vsp1_histogram_buffer_complete()`, vb2 queue ops, histogram pad format/selection handlers, and metadata V4L2 ioctl/file operations.

Control flow: entity-specific HGO/HGT constructors call `vsp1_histogram_init()` with entity type, name, formats, data size, and metadata fourcc. Users queue metadata buffers to `irqqueue`. On frame end, HGO/HGT code calls `vsp1_histogram_buffer_get()`, fills the buffer, then calls `vsp1_histogram_buffer_complete()` to timestamp, sequence, set payload, complete vb2, clear readout, and wake stop waiters. Stop streaming returns queued buffers with error and waits for an in-progress readout.

State and persistence: `struct vsp1_histogram` stores metadata format/size, video node, media pad, vb2 queue, IRQ queue, wait queue, and `readout` flag. Subdev state stores sink crop/compose and a metadata fixed source pad. Locks split normal queue access (`lock`) from IRQ queue/readout (`irqlock`).

Dependencies and integration: depends on V4L2 ioctl/subdev, vb2-vmalloc, media entities, and shared entity helpers. HGO/HGT supply hardware-specific frame-end readers and stream configuration.

Risks and test signals: risks include waiting under IRQ lock, buffer completion during stop, metadata source pad semantics, and crop/compose ratio rounding. Test metadata queue lifecycle, streamoff during readout, selection API, payload sizes, and no-buffer frame ends.
