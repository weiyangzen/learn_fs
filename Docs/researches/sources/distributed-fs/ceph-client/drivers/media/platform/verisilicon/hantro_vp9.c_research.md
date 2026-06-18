# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_vp9.c

## Purpose
`hantro_vp9.c` initializes and releases the VP9 decoder hardware context for Hantro G2, including tile-edge scratch space, BSD control storage, double-buffered segment maps, probability tables, symbol-count tables, and tile information. It also maps the hardware symbol-count memory into the V4L2 VP9 count table pointer structure used by shared VP9 probability update logic.

## Important APIs, Types, And Functions
Size helpers include `hantro_vp9_tile_filter_size`, `hantro_vp9_bsd_control_size`, `hantro_vp9_segment_map_size`, `hantro_vp9_prob_tab_size`, `hantro_vp9_count_tab_size`, and `hantro_vp9_tile_info_size`. `init_v4l2_vp9_count_tbl` initializes pointer fields in `ctx->vp9_dec.cnts`. `hantro_vp9_dec_init` allocates and zeros the coherent DMA buffers, while `hantro_vp9_dec_exit` frees them. Internal helpers `get_coeffs_arr` and `get_eobs1` select coefficient/eob count arrays for transform sizes.

## Control Flow
Initialization first verifies the hardware variant advertises `V4L2_PIX_FMT_VP9_FRAME`, then derives maximum VP9 frame dimensions from the variant format table rather than the current stream. It allocates tile-edge plus BSD control memory as one block with `bsd_ctrl_offset`, allocates two segment-map areas in one block for alternating use, and allocates a misc block containing probabilities, counters, and tile info with recorded offsets. After zeroing all buffers, it binds V4L2 count pointers into the counter region inside `misc`. Failure paths free earlier allocations in reverse order.

## State And Persistence
Per-context state lives in `ctx->vp9_dec`: coherent DMA buffers, offsets into those buffers, segment map size, and pointer aliases into the count table. Segment maps are double-buffered across frames. Probability and counter memory is transient hardware state for the active context and is released at stream stop through codec exit.

## Dependencies And Integration Points
The file includes `hantro.h`, `hantro_hw.h`, and `hantro_vp9.h`. It depends on G2 VP9 hardware register programming and completion paths, variant format tables, Linux DMA coherent allocation, and the V4L2 mem2mem stateless VP9 controls that consume the initialized `cnts` structure.

## Risks
Buffer sizes are derived from maximum variant dimensions and hard-coded tile limits, so format table changes can alter DMA footprint. The count table pointer setup is sensitive to `struct symbol_counts` layout; a mismatch with hardware output or the V4L2 VP9 library's expected pointer shape would break adaptive probability updates. `tx16x16_count` has a documented shape mismatch with the API, requiring special handling elsewhere.

## Test Signals
VP9 conformance streams with many tiles, segmentation, adaptive probability updates, and maximum-resolution frames are important. Fault-injection around coherent allocation should verify unwind paths. Debugging should inspect tile/BSD offsets, segment-map toggling, and symbol-count propagation after decode completion.
