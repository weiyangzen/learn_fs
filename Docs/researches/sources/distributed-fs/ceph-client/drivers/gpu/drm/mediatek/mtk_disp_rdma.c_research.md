## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_rdma.c

### Purpose

`mtk_disp_rdma.c` implements the classic DISP_RDMA read-DMA component. It fetches a single framebuffer layer from memory into the display pipeline, handles vblank/frame-end interrupts, programs FIFO thresholds, exposes supported formats, and provides clock/start/stop/config hooks.

### Important APIs, types, and functions

`struct mtk_disp_rdma_data` stores FIFO size and supported DRM formats. `struct mtk_disp_rdma` stores clock, MMIO, CMDQ register metadata, platform data, vblank callback, and optional DT FIFO override.

External hooks include `mtk_rdma_register_vblank_cb()`, `mtk_rdma_enable_vblank()`, `mtk_rdma_get_formats()`, `mtk_rdma_clk_enable()`, `mtk_rdma_start()`, `mtk_rdma_config()`, `mtk_rdma_layer_nr()`, and `mtk_rdma_layer_config()`. Internal helpers include `rdma_update_bits()` and `rdma_fmt_convert()`.

### Control flow

Probe allocates private state, obtains IRQ, clock, MMIO, optional CMDQ register, optional `mediatek,rdma-fifo-size`, clears interrupts, registers IRQ, sets platform data, enables runtime PM, and adds the component. The IRQ handler clears frame-completion status and dispatches the registered vblank callback.

`mtk_rdma_config()` programs output width and height, selects the DT FIFO override or platform FIFO size, and configures underflow enable, pseudo FIFO size, and output-valid threshold at 70 percent of FIFO capacity. `mtk_rdma_layer_config()` converts DRM format to memory mode, enables BT.601 YUV-to-RGB matrix for UYVY/YUYV, writes memory start address and pitch, programs GMC, and enables memory mode.

### State and persistence behavior

Software state is limited to callback pointers and FIFO override. Hardware state persists in RDMA registers: interrupt enables/status, global engine/memory mode, output dimensions, matrix selection, memory format, source address/pitch, GMC settings, and FIFO thresholds. Register updates during atomic paths can use CMDQ.

### Dependencies

The file depends on DRM fourcc metadata, Linux clock/component/IRQ/PM/platform/CMDQ APIs, and MediaTek DDP/CRTC/display/DRM headers. It consumes `mtk_plane_state` pending address, pitch, format, and dimensions prepared by the plane layer.

### Integration points

RDMA is used both as a standalone path component in many SoC arrays and as a one-layer memory source. CRTC code uses vblank callbacks, clock/start/stop/config hooks, and DMA-device lookup. For newer pseudo-OVL paths, separate MDP RDMA code is used instead of this DISP_RDMA.

### Risks

Only one layer is supported, and the code does not inspect `pending->enable` in `mtk_rdma_layer_config()`, so callers must avoid configuring disabled layers incorrectly. Pitch is masked to 16 bits, limiting wide or high-bpp buffers unless hardware supports more elsewhere. YUV matrix selection is hard-coded to BT.601. FIFO sizing mistakes can trigger underflow on DSI/DPI outputs that cannot backpressure the pipeline.

### Test signals

Test signals include frame-end vblank interrupts, memory-mode scanout in all advertised RGB and packed YUV formats, YUV matrix behavior, FIFO underflow interrupt absence under stress, DT FIFO override, mode changes across platform FIFO sizes, and suspend/resume with runtime PM.
