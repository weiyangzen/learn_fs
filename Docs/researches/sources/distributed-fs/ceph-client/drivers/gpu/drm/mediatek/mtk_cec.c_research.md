## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_cec.c

### Purpose

`mtk_cec.c` implements the MediaTek HDMI v1 CEC/HPD support block used to detect hotplug state and notify the HDMI driver.

### Important APIs, types, and functions

`struct mtk_cec` stores MMIO, clock, IRQ, cached HPD state, callback, HDMI device pointer, and a spinlock. Exported namespace functions are `mtk_cec_set_hpd_event()` and `mtk_cec_hpd_high()`. Internal helpers set/clear/mask bits, initialize/enable/disable hotplug IRQs, clear IRQ status, deliver callbacks, and service the threaded IRQ.

### Control flow

Probe allocates state, maps MMIO, gets clock and IRQ, registers a shared low-triggered threaded IRQ, enables the CEC clock, initializes 32 kHz hotplug IRQ routing, and enables HDMI power/hotplug interrupts. The IRQ thread clears all hotplug-related status, samples `RX_EVENT`, compares with cached `cec->hpd`, and invokes the registered callback if state changed. Remove disables HPD IRQs and the clock.

### State and persistence behavior

Runtime state includes cached HPD level and callback fields protected by `cec->lock`. Hardware state includes CEC clock gate, hotplug IRQ enable bits, status/clear bits, and RX event bits. Callback registration persists until replaced by HDMI code.

### Dependencies

It depends on platform/OF probing, clocks, threaded IRQs, MMIO access, and the MediaTek HDMI v1 exported namespace contract.

### Integration points

The file registers `mediatek-cec` for `mediatek,mt8173-cec`. HDMI v1 code calls the exported functions to register HPD callbacks and query current HPD state. Symbols are exported under namespace `DRM_MTK_HDMI_V1`.

### Risks

The driver is HPD-oriented and does not implement a full CEC messaging stack. IRQ handling is shared and low-triggered, so clear sequencing is important to avoid interrupt storms. Callback pointers are protected while copied but the callback runs after lock release, so lifetime is owned by the HDMI driver.

### Test signals

Signals include HDMI cable plug/unplug events, `mtk_cec_hpd_high()` matching hardware state, callback invocation exactly on state changes, IRQ clear behavior under repeated toggles, clock enable/disable balance, and module unload safety.
