# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec-vp9.c

Purpose: implements the VP9 stateless backend for the original RKVDEC register model. It prepares VP9 probability tables, segmentation maps, reference metadata, symbol-count adaptation, and register programming for profile-0 VP9 frame decode.

Important APIs and functions: exported `rkvdec_vp9_fmt_ops` with adjust/start/stop/run/done hooks. Key helpers include `init_probs`, `init_intra_only_probs`, `init_inter_probs`, `config_registers`, `validate_dec_params`, `rkvdec_vp9_run_preamble`, `rkvdec_vp9_done`, `rkvdec_init_v4l2_vp9_count_tbl`, and allocation helpers in start/stop. Private types model probability-table layout, hardware symbol-count layout, current/last frame info, and context state.

Control flow: run preamble gets VP9 frame and compressed-header controls, validates profile/resolution, resets/updates V4L2 frame contexts, and applies compressed-header probability updates. `init_probs` translates V4L2 probability tables into hardware-aligned layout. `config_registers` resolves reference buffers by timestamp, updates current/last frame state, computes aligned pitch/height and MV buffer address, configures segmentation/ref scaling/loop-filter carry-over, writes DMA bases and error controls, and copies the register image to MMIO. Completion adapts probabilities from the count buffer and saves frame context when requested.

State and persistence: VP9 context persists across frames to track four frame contexts, current/last frame metadata, two alternating segmentation maps, probability tables, and coherent private/count tables. This is stream-local state, freed on stop.

Dependencies and integration points: depends on V4L2 VP9 stateless helpers, vb2 timestamp lookup, DMA-contig buffers, `rkvdec-regs.h`, mem2mem request flow, and core decoded-buffer metadata.

Risks: only profile 0 is accepted. Probability/count layout is highly hardware-specific and alignment-sensitive. Reference lookup by timestamp falls back to the destination buffer, which avoids invalid DMA but can conceal userspace reference mistakes. Resolution changes require userspace to update capture format exactly to aligned dimensions.

Test signals: VP9 profile-0 conformance, key/intra/inter frames, segmentation map update/no-update cases, frame-context refresh modes, resolution-change negotiation, probability adaptation correctness, and IOMMU/dma-debug monitoring.
