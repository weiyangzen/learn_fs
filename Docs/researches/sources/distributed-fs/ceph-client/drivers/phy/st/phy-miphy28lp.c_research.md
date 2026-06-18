# sources/distributed-fs/ceph-client/drivers/phy/st/phy-miphy28lp.c

Purpose: STiH407 MiPHY28LP multi-protocol PHY provider for SATA, PCIe, and USB3, including glue-logic syscfg selection, reset control, PLL calibration, protocol-specific analog programming, optional SSC, polarity, and impedance tuning.

Important APIs, types, and functions: `struct miphy28lp_phy` stores per-port resources, flags, syscfg offsets, reset, selected `type`, and SATA generation. `struct miphy28lp_dev` stores shared syscfg regmap, mutex, and port array. Key routines include `miphy28lp_set_reset()`, `miphy28lp_pll_calibration()`, protocol config functions for SATA/PCIe/USB3, `miphy28lp_compensation()`, SSC helpers, `miphy_is_ready()`, `miphy28lp_setup()`, and protocol init entry points. `miphy28lp_xlate()` chooses the child PHY by node, records the requested PHY type, maps type-specific resources, and returns the PHY.

Control flow: probe reads the shared `st,syscfg` regmap, allocates one PHY per child, parses child flags/properties/syscfg offsets, gets and deasserts the shared MiPHY reset, and registers custom xlate. Consumer xlate passes one type cell (`PHY_TYPE_SATA`, `PHY_TYPE_PCIE`, or `PHY_TYPE_USB3`), causing address mapping for `sata-up`, `pcie-up`, `usb3-up`, and optional `pipew`. Init is serialized by a mutex, then switches on type: SATA configures SATA/PCI glue, setup, SATA PLL/banks, compensation, optional RX polarity/SSC/impedance, and readiness; PCIe configures glue, setup, PCIe PLL/banks, PIPE wrapper, and readiness; USB3 performs setup with sync enable, USB3 PLL/RX/TX/PIPE writes, reset sequence, and readiness.

State and persistence: selected type is stored per port after xlate. Hardware programming persists across the PHY until reset/power cycle. Shared syscfg and child resets are protected by a mutex during init. DT properties control oscillator source/readiness, polarity inversion, SSC, impedance compensation, and SATA generation.

Dependencies and integration points: generic PHY, syscon/regmap, child-node resource naming, reset controller, dt-bindings PHY type cells, SATA/PCIe/USB3 controller consumers on STiH407.

Risks: extensive magic register recipes are hardware-sensitive and hard to validate without board testing. `miphy_dev->dev` is used in an error path before assignment if syscfg lookup fails. Type is mutable per xlate and not guarded against conflicting consumers. Resource mapping is delayed until xlate, so bad resource names fail at consumer lookup time rather than probe.

Test signals: per-protocol link bring-up, xlate with each type cell, syscfg bit readback, readiness and compensation timeout tests, DT property combinations for SSC/polarity/impedance, and repeated init calls across multiple child PHYs to validate mutex and shared reset behavior.
