# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/frame/interface/ia_css_frame.h

Purpose: declares host-side frame-info and frame-buffer helpers for CSS image buffers.

Important APIs: frame-info setters (`ia_css_frame_info_set_width`, `set_format`, `init`, `is_same_resolution`, `check_info`), plane initialization (`ia_css_frame_init_planes`), allocation/free helpers (`ia_css_frame_free_multiple`, `ia_css_frame_allocate_with_buffer_size`), type comparison, DMA port derivation (`ia_css_dma_configure_from_info`), and padded-width calculation.

Control flow/state: the header defines no state; callers pass `ia_css_frame`/`ia_css_frame_info` structs from public CSS types. Functions mutate those structs and may allocate backing memory in the implementation.

Dependencies/integration: depends on `ia_css_types.h`, frame format/public definitions, and `dma.h`. It is consumed by pipeline stage allocation, debug dumping, and DMA setup.

Risks: many functions assume valid pointers or valid format enums in implementation. Width padding must match ISP/HMM memory layout or DMA stride bugs follow.

Test signals: frame-info init across RAW/YUV/NV/RGB formats, invalid zero resolution, DMA config stride/elements for packed RAW and NV12_16, and cleanup of multiple partially allocated frames.
