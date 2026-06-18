# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/rgb.c

Purpose: implements the display-controller local RGB/LVDS-style output path for Tegra DCs.

Important APIs/functions: `tegra_dc_rgb_probe()` finds the `rgb` child node, probes common output resources, gets display clocks and PLL parents, and stores the output on the DC. Encoder enable/disable programs pinmux/output tables, sync polarities, data-enable/interface format, and commits DC state. `tegra_rgb_encoder_atomic_check()` configures DC clock state, either by changing PLL-derived parent rate or by using the shift-clock divider when parent changes are unsafe. `tegra_dc_rgb_init()` creates the encoder, wraps direct panels into panel bridges, attaches bridges/connectors, initializes common output state, and limits possible CRTCs to the owning DC. Remove/exit release clocks and output resources.

Control flow and state: `struct tegra_rgb` stores common output, parent DC, PLL handles, parent clock, and DC clock. Probe-time resources persist until DC removal; encoder hooks program the DC during atomic modesets.

Dependencies/integration: uses common `tegra_output`, DRM bridge/panel connector helpers, Tegra DC register writes, clock APIs, and DT child node discovery.

Risks: older DT compatibility requires panel wrapping and optional bridge modeling. Clock parent policy differs by SoC and can produce approximate clocks via divider when PLL rate changes are not allowed. Static pin register tables are hardware-specific.

Test signals: panel and bridge DT variants, mode-set sync polarity, clock-rate validation on Tegra20 versus later SoCs, suspend/remove resource balance, and RGB-only possible CRTC mask.
