# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/output.c

Purpose: common output/connector support for Tegra display outputs, including panel/bridge discovery, EDID/DDC, HPD, CEC notifier, connector mode acquisition, and output suspend/resume.

Important APIs/functions: `tegra_output_probe()` discovers panel/bridge through graph or legacy `nvidia,panel`, obtains DDC adapter, optional fixed EDID, HPD GPIO/IRQ, and initializes polling. `tegra_output_connector_get_modes()` prefers panel modes, otherwise reads fixed or DDC EDID, updates connector display info, updates CEC physical address, and adds modes. `tegra_output_connector_detect()` uses HPD GPIO or panel presence and invalidates CEC on disconnect. `tegra_output_init()/exit()` enable/disable HPD IRQ and create HDMI CEC notifier. `tegra_output_find_possible_crtcs()` computes encoder CRTC mask from DT output mapping with a fallback mask.

Control flow and state: `struct tegra_output` owns panel/bridge/DDC/EDID/HPD/CEC resources used by output-specific drivers such as HDMI and RGB. HPD IRQ is requested during probe but disabled until connector initialization.

Dependencies/integration: uses DRM OF, panel, bridge connector, EDID, HPD helper, I2C, GPIO descriptor, and CEC notifier APIs.

Risks: mixing graph and legacy panel bindings triggers a warning and legacy panel assignment. HPD IRQ ordering is important to avoid handler access before connector setup. `drm_edid_alloc()` result is stored without explicit null-error distinction.

Test signals: DT graph and legacy panel variants, DDC EDID and fixed EDID, HPD connect/disconnect, CEC physical address updates, suspend/resume IRQ balancing.
