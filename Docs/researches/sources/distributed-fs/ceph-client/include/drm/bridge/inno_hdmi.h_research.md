# sources/distributed-fs/ceph-client/include/drm/bridge/inno_hdmi.h

Purpose: platform interface for an Innosilicon HDMI bridge, allowing glue code to provide PHY tables and optional enable behavior around a common HDMI bridge.

Important APIs/types/functions: `struct inno_hdmi_plat_ops`, `struct inno_hdmi_phy_config`, `struct inno_hdmi_plat_data`, and `inno_hdmi_bind`.

Control flow: platform code supplies PHY configs keyed by pixel clock plus a default config, then binds the bridge to a DRM encoder; mode enable paths select PHY pre-emphasis and voltage values and call optional platform enable.

State and persistence: no header-owned state. `struct inno_hdmi` is opaque; PHY config table lifetime is a platform contract, and hardware state lasts only while powered.

Dependencies and integration points: Linux types, DRM encoder/mode objects, device model, HDMI PHY setup, and DRM bridge/encoder attachment.

Risks and test signals: risks include missing defaults, incomplete PHY tables, invalid voltage/pre-emphasis values, and enable ordering bugs. Test bind cleanup, mode changes across clock thresholds, default fallback, and HDMI sink hotplug.
