# sources/distributed-fs/ceph-client/include/linux/clk/davinci.h

Purpose: This compact header exposes early registration for TI DaVinci DA850 PLL0 clocks.

Important APIs/types/functions: It includes `<linux/device.h>` and `<linux/regmap.h>` and declares `da850_pll0_init(struct device *dev, void __iomem *base, struct regmap *cfgchip)`.

Control flow: Board or platform clock initialization passes a device, mapped PLL register base, and CFGCHIP regmap into `da850_pll0_init`, which registers the relevant clocks in the implementation.

State and persistence behavior: The header owns no state. The implementation will use MMIO and regmap-backed hardware state plus CCF registrations.

Dependencies and integration points: It integrates DaVinci PLL/PSC clock-controller code with platform device setup, CCF registration, and system configuration registers reachable through regmap.

Risks: Passing an unmapped or wrong base address or CFGCHIP regmap can corrupt unrelated clock configuration. Because this is early boot plumbing, probe ordering and availability of the regmap matter.

Test signals: DA850 boot logs, CCF clock tree contents, PLL0-derived clock rates, PSC consumer probe success, and suspend/resume behavior are the key checks.
