# sources/distributed-fs/ceph-client/include/drm/bridge/analogix_dp.h

Purpose: declares the platform interface for Analogix DisplayPort/eDP bridge core drivers.

Important APIs, types, and flow: `enum analogix_dp_devtype` identifies Exynos and Rockchip variants, with `is_rockchip()` grouping Rockchip DP/eDP devices. `struct analogix_dp_plat_data` passes device type, panel, encoder, connector, skip-connector flag, and platform callbacks for power, attach, and mode retrieval. APIs probe the core, bind/unbind it to a DRM device, suspend/resume, start/stop CRC capture, translate AUX to platform data, and retrieve the DP AUX object.

State and persistence: bridge state is owned by `struct analogix_dp_device` allocated by probe and bound to DRM components. No persistence exists.

Dependencies and integration: depends on DRM CRTC/panel/bridge/connector/DP AUX infrastructure and platform-specific power/attach hooks.

Risks and test signals: risks include connector ownership confusion when `skip_connector` is set, platform callback ordering, suspend/resume power sequencing, and AUX lifetime. Signals include DRM bridge bind/unbind tests, hotplug/mode enumeration, panel attach tests, Rockchip/Exynos variant coverage, CRC capture, and suspend/resume display recovery.
