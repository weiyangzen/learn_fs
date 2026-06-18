## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_gamma.c

### Purpose

`mtk_disp_gamma.c` implements the MediaTek DISP_GAMMA DDP component. It owns gamma LUT programming, optional dithering setup, enable/disable sequencing, clock control, platform capability data, and component registration for gamma blocks on MT8173, MT8183, and MT8195-class display pipelines.

### Important APIs, types, and functions

The main state is `struct mtk_disp_gamma`, which stores the MMIO base, component clock, CMDQ client register, and `struct mtk_disp_gamma_data`. Platform data describes whether dithering exists, whether odd LUT entries are differential, LUT bank size, total LUT size, and LUT bit depth.

External DDP-facing functions are `mtk_gamma_clk_enable()`, `mtk_gamma_clk_disable()`, `mtk_gamma_get_lut_size()`, `mtk_gamma_set()`, `mtk_gamma_config()`, `mtk_gamma_start()`, and `mtk_gamma_stop()`. Probe/remove are `mtk_disp_gamma_probe()` and `mtk_disp_gamma_remove()`, exported through `mtk_disp_gamma_driver`.

### Control flow

Probe allocates private state, obtains the unnamed gamma clock, maps register resource 0, optionally obtains the CMDQ client register, attaches match data, stores drvdata, and registers as a component. Bind and unbind are empty because the operational hooks are called through the DDP component abstraction.

Mode setup calls `mtk_gamma_config()`, which programs `DISP_GAMMA_SIZE` through `mtk_ddp_write()` and, on dither-capable platforms, delegates common dither fields to `mtk_dither_set_common()`. `mtk_gamma_set()` is called with the CRTC state gamma blob: it selects LUT data mode and bank, converts DRM 16-bit LUT entries down to 10 or 12 hardware bits, optionally encodes differential odd entries, writes LUT RAM, sets rising/descending LUT type on non-dither hardware, enables the LUT, and disables relay mode. Start/stop write `DISP_GAMMA_EN`.

### State and persistence behavior

Software state is devm-managed and persists for the platform device lifetime. Hardware state persists in MMIO registers: size, dither configuration, relay mode, LUT enable/type, bank selector, and LUT RAM contents. LUT writes are direct `writel()` operations, not CMDQ queued, so gamma table updates are immediate relative to CPU execution. Size and dither changes may be synchronized by CMDQ when a packet is supplied.

### Dependencies

The file depends on Linux clock, component, platform, OF, bitfield, and CMDQ APIs, DRM color LUT helpers, and MediaTek local headers `mtk_crtc.h`, `mtk_ddp_comp.h`, `mtk_disp_drv.h`, and `mtk_drm_drv.h`. Dithering is provided by shared MediaTek display helpers, and register writes use both raw MMIO and `mtk_ddp_write()`.

### Integration points

The gamma component appears in SoC display paths in `mtk_drm_drv.c` and is initialized through `mtk_ddp_comp_init()`. CRTC gamma property sizing is driven by `mtk_gamma_get_lut_size()`. Atomic modeset and plane/color-management code call the config, start, stop, clock, and LUT hooks through DDP component function tables.

### Risks

The 12-bit layout writes red/green to `DISP_GAMMA_LUT` and blue to `DISP_GAMMA_LUT1`; using the wrong layout or bank size corrupts colors. Differential LUT mode subtracts previous entries without monotonic validation, so unexpected descending or non-monotonic LUTs can underflow before extraction. `mtk_gamma_lut_is_descending()` is called with `lut_size - 1`, which intentionally ignores the last entry in the current code path and should be treated carefully if LUT sizing changes. Direct LUT writes bypass CMDQ ordering, so callers must ensure the block is clocked and safe to update.

### Test signals

Useful signals include successful probe for each compatible, gamma LUT size exposure, KMS color-management tests with linear and non-linear LUTs, suspend/resume retaining or restoring expected color output, visual checks for 10-bit and 12-bit LUT platforms, dither enable behavior on MT8173, and register traces confirming banked MT8195 LUT programming.
