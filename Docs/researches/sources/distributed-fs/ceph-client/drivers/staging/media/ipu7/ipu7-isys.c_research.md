# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys.c

## Purpose
Implements the IPU7 ISYS auxiliary driver: probe/remove, media/V4L2 device registration, CSI2 and capture-node topology creation, async sensor binding, runtime/system PM, hardware IRQ setup/cleanup, firmware message-buffer pool management, CSI2 error handling, and top-level interrupt dispatch.

## Important APIs, Types, and Functions
Key internal subsystems are async notifier callbacks (`isys_notifier_bound()`, `isys_notifier_complete()`), device registration helpers (`isys_register_devices()`, `isys_register_video_devices()`, `isys_csi2_register_subdevices()`, `isys_csi2_create_media_links()`), PM hooks, firmware message-buffer pool functions (`alloc_fw_msg_bufs()`, `ipu7_get_fw_msg_buf()`, `ipu7_put_fw_msg_buf()`, `ipu7_cleanup_fw_msg_bufs()`), and ISR functions (`isys_isr()`, `isys_isr_one()`, `ipu7_isys_csi2_isr()`). Exported-to-local headers include `ipu7_isys_setup_hw()` and `isys_isr_one()`.

## Control Flow
Probe waits for IPU bus readiness, allocates `struct ipu7_isys`, powers the aux device, initializes MMU hardware, allocates CSI2 receivers and firmware message buffers, initializes firmware, registers media/video/CSI2 entities, initializes firmware logging, then releases runtime PM. Async binding parses firmware graph endpoints, links external sensor source pads to CSI2 sink pads, stores lane count and PHY mode, and registers subdev nodes. Stream startup from queue code later opens firmware and calls `ipu7_isys_setup_hw()`, which enables UC-to-SW and CSI legacy interrupts. The ISR checks power, reads CSI and firmware IRQ status, clears sources, dispatches per-port CSI handlers, drains firmware responses through `isys_isr_one()`, completes stream command completions, routes pin-ready events to queues, records SOF/EOF, logs errors, and loops until no handled status remains.

## State and Persistence Behavior
The parent state owns media/V4L2 devices, CSI2 array, stream array/refcounts, runtime power flag, IRQ masks, PM QoS request, firmware log, firmware message-buffer free/in-fw lists, async notifier, and subsystem config DMA pointer. Locks: `power_lock` protects power in ISR/PM, `streams_lock` protects stream refs, `listlock` protects firmware message pools, `mutex` protects firmware open refcount, and `stream_mutex` serializes stream start/stop around hardware/firmware transitions.

## Dependencies and Integration Points
Integrates with auxiliary bus, PCI media device registration, IPU bridge sensor discovery, V4L2 async notifier, CSI2/video/queue modules, firmware ISYS command/response code, IPU DMA allocator, MMU init/cleanup, PM runtime/QoS, buttress TSC sync, and platform/CSI register maps.

## Risks and Test Signals
Risks include partial probe unwind leaks, async binding ignoring the return from `isys_complete_ext_device_registration()` in the bound callback, ISR refcount churn while handling responses, firmware message buffers not returned on all command-failure paths, and suspend refusal based only on `stream_opened`. Test probe/remove cycles, missing graph endpoints, unsupported bus types, partial video/CSI registration failures, runtime suspend/resume during idle and active streaming, IRQ drain under multiple firmware responses, CSI receiver errors, and stream-opened suspend blocking.
