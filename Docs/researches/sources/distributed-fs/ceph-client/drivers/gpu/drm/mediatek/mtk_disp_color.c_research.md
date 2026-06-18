## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_color.c

### Purpose

`mtk_disp_color.c` implements the MediaTek DISP_COLOR block used in DDP pipelines for basic color engine startup and frame-size programming.

### Important APIs, types, and functions

`struct mtk_disp_color` stores CRTC pointer, clock, MMIO, CMDQ metadata, and platform data. Public functions are `mtk_color_clk_enable()`, `mtk_color_clk_disable()`, `mtk_color_config()`, and `mtk_color_start()`. Match data supplies SoC-specific start/width/height register offsets for MT2701, MT8167, and MT8173.

### Control flow

Probe allocates state, obtains clock and MMIO, optionally obtains CMDQ metadata, stores match data, and adds a component. Config writes width and height registers through DDP write helpers. Start enables bypass-all and sequence selection in `DISP_COLOR_CFG_MAIN`, then writes one to the SoC-specific start register.

### State and persistence behavior

Software state persists the SoC register offset table. Hardware state includes width/height, bypass/sequence config, and start bit until the component is reset or powered down.

### Dependencies

It depends on component framework, clocks, OF match data, platform MMIO, CMDQ helpers, and DDP write helpers.

### Integration points

`mtk_ddp_comp.c` exposes these functions through the `ddp_color` function table. `mtk_crtc.c` configures and starts COLOR when it appears in a SoC DDP path.

### Risks

Register offsets vary by SoC; incorrect match data writes the wrong block. The driver starts COLOR in bypass mode, so advanced color processing is not configured here. There is no stop callback in the DDP table for COLOR.

### Test signals

Signals include component probe for each compatible, correct width/height readback, display scanout through paths containing COLOR, clock balance, and no visual corruption when bypass mode is used.
