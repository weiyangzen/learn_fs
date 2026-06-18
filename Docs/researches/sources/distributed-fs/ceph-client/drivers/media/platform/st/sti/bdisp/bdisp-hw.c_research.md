# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/bdisp-hw.c

Purpose: implements the low-level programming path for the STi BDisp 2D blitter. It converts V4L2 mem2mem context state into BDisp linked-list nodes, allocates coherent node/filter memory, resets the engine, acknowledges hardware interrupts, and submits a request to AQ1.

Important APIs and functions: exported entry points are `bdisp_hw_reset`, `bdisp_hw_get_and_clear_irq`, `bdisp_hw_alloc_nodes`, `bdisp_hw_free_nodes`, `bdisp_hw_alloc_filters`, `bdisp_hw_free_filters`, and `bdisp_hw_update`. Internal helpers choose resize filter tables (`bdisp_hw_get_hf_addr`, `bdisp_hw_get_vf_addr`), compute 6.10 scaling increments, derive operation flags in `bdisp_hw_get_op_cfg`, map V4L2 fourcc values to BDisp color encodings, and build one or more `struct bdisp_node` descriptors.

Control flow: probe-time code allocates global horizontal and vertical filter tables from static coefficient arrays. Per-file contexts allocate up to `MAX_NB_NODE` contiguous DMA descriptors. On each job, `bdisp_hw_update` calls `bdisp_hw_build_all_nodes`, saves a debug copy, enables AQ1 last-node interrupts, writes the first node address, then writes the last node address to start processing. Node construction handles source/destination plane count, RGB/YUV conversion matrices, scaling or 4:2:0 chroma resampling, interlaced source half-height handling, flips, target plane selection, and source splitting into up to two vertical strides for widths over 2048 pixels.

State and persistence: persistent driver state is limited to DMA-backed node/filter buffers and the debug copy in `bdisp_dev->dbg`; hardware state lives in MMIO registers and is reset for every run. Filter address arrays are file-static globals shared by all BDisp instances.

Dependencies and integration points: depends on `bdisp.h`, `bdisp-reg.h`, `bdisp-filter.h`, DMA coherent/write-combine allocation, Linux MMIO accessors, V4L2 pixel formats, and the V4L2 mem2mem context maintained by `bdisp-v4l2.c`.

Risks: scaling accepts a wide range but rejects extreme ratios via increment underflow/overflow. The static global filter arrays assume one allocation lifetime and can be risky if multiple devices probe independently. Node math has many chroma/interlace/stride coordinate transformations, so off-by-one and odd-alignment bugs are plausible. `bdisp_hw_save_request` uses `GFP_ATOMIC` devm allocation for debug copies during submission.

Test signals: useful tests are mem2mem conversions among RGB565/RGB24/XBGR/ABGR/NV12/YUV420, scaling up/down, 2048+ width split jobs, hflip/vflip combinations, interlaced output input handling, interrupt timeout paths, and DMA/IOMMU validation that filter and node physical addresses are visible to the blitter.
