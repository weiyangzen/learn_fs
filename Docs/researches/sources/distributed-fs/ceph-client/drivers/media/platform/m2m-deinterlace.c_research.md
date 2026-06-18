# sources/distributed-fs/ceph-client/drivers/media/platform/m2m-deinterlace.c

## Purpose
This file implements a V4L2 memory-to-memory deinterlacing driver backed by a DMAengine channel with interleaved-transfer support. It converts sequential-field input buffers into either interlaced output or progressive line-doubled output for YUV420 and YUYV formats.

## Important APIs, Types, And Functions
`struct deinterlace_fmt` declares supported fourccs and queue direction flags. `struct deinterlace_q_data` stores width, height, sizeimage, format, and field for a queue. `struct deinterlace_dev` owns the V4L2/video device, DMA channel, mutex, busy flag, and m2m device. `struct deinterlace_ctx` owns one file handle, m2m context, colorspace, DMA cookie, abort flag, and `dma_interleaved_template`.

The central functions are `deinterlace_job_ready()`, `deinterlace_device_run()`, `deinterlace_issue_dma()`, `dma_callback()`, format ioctls `vidioc_*`, vb2 callbacks `deinterlace_queue_setup()`, `deinterlace_buf_prepare()`, `deinterlace_buf_queue()`, queue creation `queue_init()`, file operations `deinterlace_open()` / `deinterlace_release()`, and platform probe/remove.

## Control Flow
Probe allocates the device, requests any DMA channel advertising `DMA_INTERLEAVE`, registers a V4L2 device, registers a video node, initializes the V4L2 mem2mem device, and stores driver data. Open allocates a context, initializes its V4L2 file handle and mem2mem queues, allocates one interleaved DMA template, and defaults colorspace. Userspace configures matching output/capture formats and compatible field conversion. `vidioc_streamon()` rejects mismatched fourccs and unsupported field-direction combinations before delegating to V4L2 m2m.

When both source and destination buffers are ready and the device is not busy, `deinterlace_device_run()` marks the device busy and submits a sequence of interleaved DMA operations. For YUV420 it submits separate Y, U, and V odd/even or line-doubling operations; for YUYV it submits odd/even or odd/doubled operations. Only the final operation in the sequence carries the callback. `dma_callback()` clears busy, removes source and destination buffers, copies timestamp/timecode metadata, marks both done, and finishes the m2m job.

## State And Persistence
Queue format state is held in a global static `q_data[2]`, not per context. Per-open state includes colorspace, abort flag, and DMA template. The driver has no persistent storage. Runtime state is the global DMA channel, `busy` atomic, and queued mem2mem buffers.

## Dependencies And Integration Points
The driver depends on V4L2 mem2mem, vb2 DMA-contig, DMAengine interleaved DMA, and the platform bus. It registers as a platform driver named `m2m-deinterlace` and exposes `V4L2_CAP_VIDEO_M2M | V4L2_CAP_STREAMING`. It does not use hardware-specific registers; the DMAengine provider supplies the actual copy engine.

## Risks
The global `q_data` means multiple opens can overwrite each other's negotiated formats, which is a serious multi-instance correctness risk. `queue_init()` appears to assign the destination default field into `q_data[V4L2_M2M_SRC].field`, leaving destination field initialization suspicious. If `deinterlace_issue_dma()` fails to acquire addresses, prepare, or submit a DMA descriptor, it returns without completing buffers or finishing the job, which can hang userspace. The code assumes the DMA template with one `data_chunk` is enough for all operations and reuses it across sequential submissions. Abort handling calls job finish but does not explicitly terminate in-flight DMA.

## Test Signals
Compile with DMAengine and V4L2 mem2mem enabled. Runtime tests should use two simultaneous file handles to expose global-format leakage, validate all four field conversion modes, stream YUV420 and YUYV with MMAP/DMABUF, inject DMA prep/submit failures, and run streamoff/close while a job is busy. V4L2 compliance should verify queue setup, field validation, and timestamp propagation.
