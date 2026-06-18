# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/frame/src/frame.c

Purpose: implements CSS frame layout, HMM allocation, padding, and DMA-port derivation.

Important functions: `ia_css_frame_allocate_from_info`, `ia_css_frame_allocate`, `ia_css_frame_free`, `ia_css_frame_init_planes`, `ia_css_frame_pad_width`, frame-info setters, `ia_css_frame_allocate_with_buffer_size`, `ia_css_frame_is_same_type`, `ia_css_dma_configure_from_info`, host-to-SP conversion helpers, and `ia_css_frame_init_from_info`.

Control flow: allocation creates a zeroed frame, initializes plane offsets/strides based on format, then allocates `data_bytes` through `hmm_alloc`. Plane initialization dispatches by frame format to single-plane, raw-packed, NV, YUV, RGB, six-plane, or binary helpers. DMA config converts frame info into stride/elements/width after checking padded width.

State/persistence: frame structs own an HMM buffer address in `frame->data` and transient plane metadata. Defaults set invalid queue/buffer IDs until higher layers bind frames to queues.

Dependencies/integration: depends on kernel allocation (`kvmalloc`/`kvfree`), HMM memory, frame formats, ISP vector/DDR constants, AtomISP logging, and pipeline stage creation.

Risks: format handling is hand-maintained and mismatched padding can underallocate or mis-stride hardware buffers. Odd heights are rounded for single-plane allocation but not uniformly for all formats. `ia_css_frame_is_same_type` dereferences frame pointers before null checks on frame objects.

Test signals: allocation/free for every supported format, invalid MIPI format rejection, raw bit-depth stride math, NV12_TILEY rounding, DMA config invalid padded width, and fault injection of HMM allocation failures.
