# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/dw-hdmi-audio.h

Purpose: provides the platform-data contracts shared between the main DW-HDMI bridge driver and its AHB/I2S/GP audio companion drivers.

Important APIs/types/functions: forward-declares `struct dw_hdmi`. `struct dw_hdmi_audio_data` carries MMIO physical/base addresses, IRQ, parent HDMI pointer, and `get_eld()` callback for AHB and GP audio paths. `struct dw_hdmi_i2s_audio_data` carries parent HDMI pointer plus register read/write callbacks and `get_eld()` for the I2S codec path.

Control flow: no executable code. Parent HDMI code instantiates platform devices with one of these data blocks; audio drivers consume the callbacks/resources during probe and codec/PCM operations.

State and persistence: no owned state. The structures reference parent-owned MMIO and HDMI state; lifetime must outlive child platform devices.

Dependencies and integration: requires Linux integer/address types and the opaque DW-HDMI core. Integrates DRM ELD access, HDMI audio control APIs, and register access indirection for child drivers.

Risks: platform data is copied by some consumers and referenced by others, so parent lifetime and callback validity are critical. Wrong IRQ/base pairing can break AHB DMA audio. Missing `get_eld` would crash consumers because they call it unconditionally.

Test signals: build coverage for all DW-HDMI audio companions and runtime child device creation/removal with valid ELD and register callbacks.
