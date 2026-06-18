# Research: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-dma.h

Purpose: declares the Xilinx video DMA endpoint and pipeline data structures shared between the composite device and DMA implementation.

Important types: `struct xvip_pipeline` embeds `media_pipeline` plus mutex-protected use and stream counters, number of DMA engines, and the output DMA pointer. `struct xvip_dma` owns list linkage, `video_device`, media pad, parent composite device, embedded pipeline, DT port, format/fmtinfo, vb2 queue, sequence counter, queued buffer list and spinlock, DMAEngine channel, alignment, and interleaved transfer template/chunk. The `to_xvip_dma` and `to_xvip_pipeline` helpers convert from V4L2 objects.

Control flow and state are implemented by `xvip_dma_init()` and `xvip_dma_cleanup()` declared here. Dependencies include DMAEngine, V4L2/vb2, media entities, mutexes, spinlocks, and composite/format forward declarations.

Risks: structure fields are shared across stream, queue, and graph code, so lock ownership matters: `lock` protects format/queue state, `queued_lock` protects queued buffers, and pipeline lock protects counters. Test signals are build compatibility for users of these structures and runtime stream lifecycle coverage in `xilinx-dma.c`.
