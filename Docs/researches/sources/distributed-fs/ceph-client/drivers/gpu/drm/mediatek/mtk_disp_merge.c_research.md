## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_merge.c

### Purpose

`mtk_disp_merge.c` implements the DISP_MERGE component used to buffer or merge display streams, including left/right merge programming for wide layers and FIFO mode for OVL adaptor pipelines. It also provides mode validation based on merge clock and prefetch bandwidth constraints.

### Important APIs, types, and functions

`struct mtk_disp_merge` stores MMIO, main and optional async clocks, CMDQ register metadata, FIFO/mute feature flags, and an optional reset control. Public hooks include `mtk_merge_start()`, `mtk_merge_stop()`, `mtk_merge_start_cmdq()`, `mtk_merge_stop_cmdq()`, `mtk_merge_config()`, `mtk_merge_advance_config()`, `mtk_merge_clk_enable()`, `mtk_merge_clk_disable()`, and `mtk_merge_mode_valid()`.

Key register groups are `DISP_REG_MERGE_CTRL`, size registers `CFG_0/1/4/24/25/26/27`, merge mode register `CFG_12`, swap register `CFG_10`, FIFO threshold registers `CFG_36/37/40/41`, and `DISP_REG_MERGE_MUTE_0`.

### Control flow

Probe maps registers, obtains clocks, optionally obtains the async clock and reset control, obtains CMDQ metadata, reads `mediatek,merge-fifo-en` and `mediatek,merge-mute`, stores drvdata, and registers the component. Start clears mute if supported and enables the merge block. Stop optionally mutes, disables the block, and performs a reset when invoked synchronously without CMDQ and an async clock is present.

`mtk_merge_config()` is a simple one-input wrapper. `mtk_merge_advance_config()` validates nonzero height and left width, optionally sets FIFO thresholds, selects buffer mode, two-input FIFO mode, or left/right merge mode depending on `fifo_en` and `r_w`, programs input/output/SRAM dimensions, clears swap mode, and writes the merge mode.

### State and persistence behavior

Private state is platform-device lifetime state. Hardware state persists across the block until rewritten or reset: merge mode, input and output dimensions, SRAM dimensions, FIFO thresholding, mute, swap, and enable. Clock enable state is reference-managed externally by DDP component sequencing, while stop may reset async-clock variants only for direct CPU stop calls.

### Dependencies

The driver uses clock, reset, component, OF, platform, CMDQ, and DRM mode APIs. It depends on `mtk_ddp_write()` and `mtk_ddp_write_mask()` for optional CMDQ-backed register programming and is consumed by `mtk_disp_ovl_adaptor.c` and CRTC path management.

### Integration points

In normal DDP paths, merge is a component in SoC path arrays. In the OVL adaptor path, per-layer MDP RDMA outputs feed MERGE blocks before ETHDR, with `mtk_merge_advance_config()` receiving left/right widths. `mtk_merge_mode_valid()` is called through component function tables to reject modes that exceed merge clock or prefetch bandwidth assumptions.

### Risks

The async-clock error unwind in `mtk_merge_clk_enable()` correctly disables the main clock, but the rollback loop in OVL adaptor clock enable calls must pass the matching component pointer or clocks can be unbalanced there. Width and height validation only rejects zero left width and height; extreme dimensions rely on register mask limits and upstream mode checks. The mode-valid prefetch formula uses a fixed threshold derived from 4K60 assumptions, so new SoCs or clocks may need updated limits. Reset is skipped for CMDQ stops, which may matter if a CMDQ stop is expected to fully clear state.

### Test signals

Test with single-input buffer mode, dual-input left/right merge mode, FIFO-enabled OVL adaptor layers, mute-capable compatibles, async reset paths, mode validation for high-pixel-clock and low-VBP modes, and CMDQ versus direct start/stop paths. Display bringup on MT8195 merge paths is the primary integration signal.
