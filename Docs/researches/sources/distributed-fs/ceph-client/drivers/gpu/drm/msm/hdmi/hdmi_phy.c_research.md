# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_phy.c

## Purpose
Provides the platform driver and common resource management for MSM HDMI PHY instances, dispatching to SoC-specific PHY/PLL implementations.

## Important APIs, types, and functions
- `msm_hdmi_phy_resource_init()` obtains configured regulators and clocks.
- `msm_hdmi_phy_resource_enable()` and `msm_hdmi_phy_resource_disable()` handle runtime PM, regulators, and clocks.
- `msm_hdmi_phy_powerup()` and `msm_hdmi_phy_powerdown()` call optional SoC-specific callbacks.
- `msm_hdmi_phy_pll_init()` selects the 8960, 8996, or 8998 PLL registration path.
- `msm_hdmi_phy_probe()` maps MMIO, initializes resources, initializes the PLL clock provider, and publishes drvdata.

## Control flow
Probe allocates `struct hdmi_phy`, pulls the matched `hdmi_phy_cfg`, maps `hdmi_phy`, initializes regulators/clocks by name, enables runtime PM, temporarily enables resources so PLL setup can touch hardware, registers the PLL provider where supported, disables resources again, and stores platform data. Driver registration exposes DT compatibles for 8660, 8960, 8974, 8084, 8996, and 8998.

## State and persistence
State lives in the devm-managed `struct hdmi_phy`: config pointer, MMIO base, regulator bulk array, clock array, and platform device. Resources are enabled only around PHY operations. The PLL registration persists as a clock provider for the device lifetime.

## Dependencies and integration points
Depends on OF match data, regulator bulk APIs, common clock framework helpers from SoC-specific PLL files, runtime PM, and `msm_ioremap()`/`msm_clk_get()`. It integrates with HDMI bridge power sequencing through `hdmi->phy`.

## Risks
`msm_hdmi_phy_resource_enable()` returns immediately on regulator failure without undoing runtime PM; clock enable failure does not unwind already enabled clocks. Probe must enable resources before PLL init because PLL register access depends on powered clocks/regulators. Unsupported PLL types intentionally succeed, which can mask missing PLL support.

## Test signals
Probe logs for missing regulators/clocks/MMIO, runtime PM balance, successful clock provider registration, HDMI mode set with each compatible, and suspend/resume of PHY resources are useful signals.
