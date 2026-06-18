# sources/distributed-fs/ceph-client/drivers/phy/socionext/phy-uniphier-usb3ss.c

Purpose: UniPhier USB3 super-speed PHY provider, programming SS PHY indirect trim/tuning registers and managing PHY/link clocks, resets, and optional VBUS.

Important APIs, types, and functions: `struct uniphier_u3ssphy_soc_data` has legacy flag and up to seven indirect parameters. `uniphier_u3ssphy_testio_write()` performs TESTI writes with required TESTO dummy reads. `uniphier_u3ssphy_set_param()` reads, masks, writes, pulses write-enable, and dummy-reads an internal PHY register. PHY ops provide init/exit and power on/off.

Control flow: probe obtains non-legacy `phy` clock, optional `phy-ext`, `phy` reset, or legacy GIO parent resources, plus common link clock/reset and optional VBUS. Init enables parent resources and applies non-legacy parameter table. Power-on enables optional external clock, PHY clock, deasserts reset, and enables VBUS. Shutdown reverses these operations.

State and persistence: SoC data tables encode CDR, TX PLL, bandgap, VCO, and VCOPLL settings. Runtime state is private resource handles. Hardware state persists in SS PHY internal TESTIO registers until reset/power loss.

Dependencies and integration points: generic PHY, clock/reset/regulator, MMIO, UniPhier USB3 controller, compatibles for Pro4/Pro5/PXs2/LD20/PXs3/NX1.

Risks: indirect writes require exact dummy-read sequencing. Legacy devices share the Pro4 data and skip SS parameter programming. Optional VBUS from the PHY device assumes a single supply. No explicit PLL-ready poll is done in this driver; failures surface through controller behavior.

Test signals: SuperSpeed link training on supported SoCs, register trace of parameter writes, VBUS and clock balance through bind/unbind or runtime PM, and compile coverage with `PHY_UNIPHIER_USB3` building both HS and SS objects.
