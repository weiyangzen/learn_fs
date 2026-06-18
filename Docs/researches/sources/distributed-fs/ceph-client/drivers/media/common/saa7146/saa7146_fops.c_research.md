# sources/distributed-fs/ceph-client/drivers/media/common/saa7146/saa7146_fops.c

Purpose: common V4L2/VB2 file-operation and device-registration layer for SAA7146 video/VBI extensions, plus shared DMA queue/resource management.

Important APIs/functions: `saa7146_vv_init()` registers `v4l2_device`, creates brightness/contrast/saturation/flip controls, initializes video/VBI use-ops, and default formats. `saa7146_vv_release()` tears down VV state. `saa7146_register_device()` sets file/ioctl ops, device caps, VB2 queue properties, and registers `video_device`; `saa7146_unregister_device()` unregisters it. Buffer helpers queue, finish, advance, and timeout buffers.

Control flow: VB2 queues call into video or VBI qops; queued buffers are either activated immediately or linked. IRQ callbacks finish current buffer and activate next. Timeout marks current buffer error and advances. `fops_write()` delegates only VBI writes supported by an extension.

State/persistence: `struct saa7146_vv` holds resource bits, formats, queues, timers, sequence number, current standard/source/sync, and wait queues. State is runtime only.

Dependencies/integration: depends on SAA7146 core, V4L2 device/control/file ops, VB2 DMA-SG memory ops, extension-provided capabilities/standards/callbacks.

Risks/test signals: resource locking has a redundant first check that effectively treats already-set bits as success, so concurrent resource semantics deserve scrutiny. Test queue lifecycle, timeout handling, video vs VBI capability masks, VB2 queue init failure, and extension VBI write locking.
