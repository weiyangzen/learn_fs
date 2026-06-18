## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_disp_aal.c

### Purpose

`mtk_disp_aal.c` implements the MediaTek DISP_AAL display block, including clock control, size programming, optional gamma LUT programming, start/stop, and component registration.

### Important APIs, types, and functions

`struct mtk_disp_aal` stores clock, MMIO, CMDQ register metadata, and match data. Public component functions are `mtk_aal_clk_enable()`, `mtk_aal_clk_disable()`, `mtk_aal_config()`, `mtk_aal_gamma_get_lut_size()`, `mtk_aal_gamma_set()`, `mtk_aal_start()`, and `mtk_aal_stop()`. Match data currently marks MT8173 as having gamma support.

### Control flow

Probe allocates state, obtains clock and MMIO, optionally obtains CMDQ client register metadata, stores platform data, and adds a component. Config writes input and output size through CMDQ or MMIO. Gamma setup exits if unsupported or no LUT is present, converts DRM LUT entries to 10-bit RGB fields, writes 512 LUT registers directly, then enables gamma LUT and disables relay mode. Start writes `AAL_EN`; stop clears it.

### State and persistence behavior

Software state is the device-private clock/MMIO/CMDQ/data pointer. Hardware state includes size registers, output size, gamma LUT table, config relay/gamma bits, and enable bit.

### Dependencies

It depends on component framework, clocks, OF match data, platform MMIO, CMDQ helpers, DRM color LUT helpers, and DDP write helpers.

### Integration points

`mtk_ddp_comp.c` references these functions in the `ddp_aal` function table. `mtk_crtc.c` invokes config/start/stop and gamma operations through DDP wrappers.

### Risks

Gamma LUT writes bypass CMDQ and direct-write 512 registers, so synchronization with atomic updates relies on call context. Only SoCs with `has_gamma` expose LUT size. Incorrect LUT bit extraction or relay/gamma bits affects color output.

### Test signals

Signals include component probe, clock enable/disable, size programming, gamma LUT property tests on MT8173, relay mode disabled after gamma set, and modesets with AAL in the DDP path.
