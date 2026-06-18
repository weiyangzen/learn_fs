# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rga/rga-buf.c

Purpose: implements videobuf2 queue operations and per-buffer RGA MMU descriptor preparation for the Rockchip RGA V4L2 mem2mem driver.

Important APIs/functions: exports `rga_qops`. `rga_queue_setup()` validates plane counts/sizes. `rga_buf_init()` allocates a coherent descriptor table sized to the frame size in pages. `rga_buf_prepare()` validates fields, sets payloads, fills descriptors from each scatter-gather DMA page, computes per-plane offsets, and stores Y/U/V offsets in `struct rga_vb_buffer`. `rga_buf_queue()` queues buffers into the V4L2 mem2mem context. Streaming start/stop handle runtime PM and return pending buffers on failure/stop.

Control flow/state: each VB2 buffer owns a coherent `rga_dma_desc` array and DMA address consumed by hardware command programming. For multi-planar and single-memory multi-component formats, offsets are derived either from descriptor table position or from frame geometry. Output buffers must be progressive (`V4L2_FIELD_NONE`).

Dependencies/integration: depends on `videobuf2-dma-sg`, V4L2 mem2mem queue helpers, runtime PM, SG DMA iterators, `rga_get_frame()`, and `rga-hw.c` command programming that consumes descriptor DMA addresses and offsets.

Risks and test signals: `fill_descriptors()` checks `n_desc > max_desc`, so boundary behavior at exactly max descriptors deserves attention. Plane offset calculations assume format geometry and `uv_factor` match V4L2 format layout. Test MMAP/DMABUF queues, SG buffers crossing many pages, NV12/NV12M/YUV planar formats, invalid field values, stream start PM failure, and stop returning queued buffers with error.
