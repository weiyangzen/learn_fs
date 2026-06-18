# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_hdmi.h

Purpose: Defines shared HDMI types and register helpers used by the HDMI controller and PHY implementation.

Important APIs/types: `struct hdmi_phy_ops` provides `start` and `stop` hooks for PHY-specific code. `struct hdmi_audio_params` stores enabled state, sample width/rate, and CEA audio infoframe. `struct sti_hdmi` is the central HDMI runtime object: device, DRM device, mode, registers, clocks, IRQ/status, PHY ops, HPD wait state, reset, DDC adapter, colorspace, audio codec platform device, connector, CEC notifier, and bridge. `hdmi_read()`/`hdmi_write()` are exported for PHY code.

Control/state: Defines HPD/DLL lock register bits and default colorspace. The HDMI controller owns persistent bridge/connector/audio/CEC state while the PHY module manipulates serializer/PLL registers through the same mapped register space.

Dependencies/integration: Includes Linux HDMI, platform device, CEC notifier, and DRM bridge/mode/property headers.

Risks/test signals: Changes to `struct sti_hdmi` affect both controller and PHY compilation. PHY ops must be valid for the OF-compatible device. Build and HDMI bridge enable tests verify the contract.
