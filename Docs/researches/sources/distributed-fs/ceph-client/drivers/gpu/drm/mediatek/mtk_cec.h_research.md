## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_cec.h

### Purpose

`mtk_cec.h` declares the small HPD-facing API exposed by the MediaTek HDMI v1 CEC block.

### Important APIs, types, and functions

It forward-declares `struct device` and declares `mtk_cec_set_hpd_event()` plus `mtk_cec_hpd_high()`. The callback signature passes a boolean HPD level and the HDMI device pointer supplied during registration.

### Control flow

There is no runtime flow in the header. HDMI code registers a callback, and the CEC driver calls it from the hotplug IRQ thread when HPD changes.

### State and persistence behavior

The header owns no state. Registered callback state is stored in `struct mtk_cec` in `mtk_cec.c`.

### Dependencies

It depends only on Linux types and a device forward declaration, keeping the HDMI/CEC boundary light.

### Integration points

The declarations are implemented by `mtk_cec.c` and consumed by HDMI v1 code built under `CONFIG_DRM_MEDIATEK_HDMI`.

### Risks

The API exposes HPD only, despite the CEC filename, so callers must not expect full CEC transmit/receive functionality. Callback lifetime must be managed by the caller.

### Test signals

Build coverage with HDMI v1 enabled and runtime callback registration during HDMI probe are the main signals.
