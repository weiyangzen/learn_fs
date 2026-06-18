# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-helper.c

## Purpose
`wave5-helper.c` provides shared utility code for Wave5 V4L2 encoder and decoder frontends. It centralizes state string conversion, instance cleanup, release sequencing, vb2 queue initialization, event subscription, output format reporting, format lookup, V4L2 format-to-firmware-standard mapping, queued buffer return, pixel format sizing, and IRQ FIFO allocation.

## Important APIs and Functions
Key functions include `state_to_str`, `wave5_kfifo_alloc`, `wave5_cleanup_instance`, `wave5_vpu_release_device`, `wave5_vpu_queue_init`, `wave5_vpu_subscribe_event`, `wave5_vpu_g_fmt_out`, `wave5_find_vpu_fmt`, `wave5_find_vpu_fmt_by_idx`, `wave5_to_vpu_std`, `wave5_return_bufs`, and `wave5_update_pix_fmt`. These operate on shared `struct vpu_instance` and `struct vpu_device` state from `wave5-vpu.h`.

## Control Flow
Open paths allocate instances and later call these helpers for queue setup and cleanup. Release first destroys the V4L2 mem2mem context, removes the instance from the device list under mutex plus spinlock protection, calls the codec-specific close function if firmware state exists, and then frees queues, controls, DMA buffers, SRAM, IDs, codec info, and the instance.

## State and Persistence
The helper owns no independent persistent storage, but it mutates important instance state: IRQ status kfifo allocation, queue parameters, V4L2 controls, source/destination format structures, SRAM and bitstream DMA buffers, framebuffer backing buffers, and device instance lists.

## Dependencies and Integration
It depends on V4L2 mem2mem, videobuf2 DMA-contig, V4L2 events/controls, IDA allocation, kfifo, and Wave5 VDI framebuffer reset/free helpers. It is shared by decoder and encoder frontends through `wave5-helper.h`.

## Risks and Test Signals
Risks include release ordering around IRQ threads, list synchronization between hard IRQ and threaded IRQ contexts, queue `buf_struct_size` consistency, and returning queued buffers with completed request controls. Test signals are clean open/close loops under active decode, event subscription behavior, buffer cancellation on streamoff/error paths, format enumeration/fallback behavior, and lockdep/KASAN coverage around release races.
