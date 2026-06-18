## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_ddp_comp.h

### Purpose

`mtk_ddp_comp.h` defines the common MediaTek DDP component abstraction used by CRTCs, planes, and display block drivers.

### Important APIs, types, and functions

It defines `enum mtk_ddp_comp_type`, `struct mtk_ddp_comp_funcs`, and `struct mtk_ddp_comp`. The function table covers power, clock, config/start/stop, vblank callbacks, plane/layer capabilities and programming, gamma/CTM, background color, DMA device selection, formats/blend/AFBC, MMSYS connect/disconnect, mutex add/remove, encoder index, and mode validation. Inline wrappers provide default PM/runtime behavior and no-op fallbacks.

### Control flow

Callers operate through wrappers such as `mtk_ddp_comp_power_on()`, `mtk_ddp_comp_config()`, `mtk_ddp_comp_layer_config()`, `mtk_ddp_gamma_set()`, `mtk_ddp_comp_connect()`, and `mtk_ddp_comp_encoder_index_set()`. If a callback is missing, the wrapper usually returns a safe default or falls back to runtime PM.

### State and persistence behavior

`struct mtk_ddp_comp` persists the device pointer, IRQ, component ID, encoder index, and callback table pointer for each component in a DRM private path. The header itself stores no runtime data.

### Dependencies

It depends on Linux IO, runtime PM, CMDQ, MMSYS, mutex, and DRM mode types. It forward-declares DRM and MediaTek plane/CRTC state types to keep component callbacks typed.

### Integration points

This is the main contract between `mtk_crtc.c`, `mtk_ddp_comp.c`, and individual display-block drivers such as OVL, RDMA, AAL, CCORR, COLOR, DSI, DPI, MERGE, and OVL adaptor.

### Risks

Silent no-op defaults are useful for optional blocks but can hide missing callbacks. `mtk_ddp_comp_power_on()` contains an unreachable `return 0` after the fallback return. Function tables must match each component driver’s private data type. Missing layer count or format callbacks can prevent plane creation.

### Test signals

Build coverage, CRTC creation, plane count/format discovery, runtime PM balance, vblank callback delivery, color-management updates, connector route switching, and SoC-specific component path tests validate this interface.
