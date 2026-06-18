## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_ddp_comp.c

### Purpose

`mtk_ddp_comp.c` is the MediaTek DDP component registry and generic component helper implementation. It maps SoC component IDs to component types and function tables, provides CMDQ-aware register write helpers, implements simple block handlers for dither/DSC/OD/postmask/UFOE, resolves possible CRTCs, and initializes generic component state.

### Important APIs, types, and functions

Public functions include `mtk_ddp_write()`, `mtk_ddp_write_relaxed()`, `mtk_ddp_write_mask()`, `mtk_dither_set_common()`, `mtk_ddp_comp_get_id()`, `mtk_find_possible_crtcs()`, and `mtk_ddp_comp_init()`. Key tables are `ddp_aal`, `ddp_ccorr`, `ddp_color`, `ddp_dither`, `ddp_dpi`, `ddp_dsc`, `ddp_dsi`, `ddp_gamma`, `ddp_merge`, `ddp_od`, `ddp_ovl`, `ddp_postmask`, `ddp_rdma`, `ddp_ufoe`, `ddp_ovl_adaptor`, `mtk_ddp_comp_stem`, and `mtk_ddp_matches`.

### Control flow

Register writes go through CMDQ packet commands when a packet is provided, otherwise direct MMIO. Component initialization validates the component ID, installs ID/function table data, resolves the platform device from DT, defers if missing, and for generic components maps MMIO, obtains a clock, gets CMDQ client registers, and stores private data. Components with dedicated drivers skip generic MMIO setup. `mtk_find_possible_crtcs()` scans all MMSYS private paths and connector routes to return the CRTC bitmask containing a device.

### State and persistence behavior

Persistent state includes `struct mtk_ddp_comp` fields (`dev`, `id`, `encoder_index`, callbacks) and generic `struct mtk_ddp_comp_dev` MMIO/clock/CMDQ metadata. Hardware state for generic helpers includes dither, DSC bypass/enable, OD relay/dither, postmask relay, and UFO bypass registers.

### Dependencies

It depends on OF/platform helpers, clocks, CMDQ, DRM logging, MediaTek MMSYS route data, mutex APIs through function tables, and display block functions declared in `mtk_disp_drv.h`.

### Integration points

`mtk_crtc.c` uses the function tables through inline wrappers in `mtk_ddp_comp.h`. SoC driver data supplies path arrays and connector routes indexed by `DDP_COMPONENT_*` IDs. Dedicated component platform drivers provide their own `dev_get_drvdata()` payloads.

### Risks

Component ID, OF alias, and function-table mappings are central contracts; mistakes route planes or encoders incorrectly. Some component types have NULL function tables and rely on fallback behavior. Generic and dedicated components have different private-data shapes, so a function table must match the owning driver. CMDQ and direct-write paths must remain equivalent.

### Test signals

Signals include DT probe ordering with `-EPROBE_DEFER`, path availability detection, CRTC possible-mask correctness, CMDQ/direct register write parity, dither/DSC/postmask behavior, and modeset coverage for every component ID used by supported SoCs.
