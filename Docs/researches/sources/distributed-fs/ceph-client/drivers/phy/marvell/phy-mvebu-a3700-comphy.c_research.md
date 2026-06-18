<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mvebu-a3700-comphy.c -->
# sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mvebu-a3700-comphy.c

Purpose: Implements Armada 3700 COMPHY lane control for SATA, USB3 host, PCIe, and Ethernet SGMII/1000Base-X/2500Base-X. It directly programs three multiplexed lanes and their selector registers without firmware mediation.

Important APIs and types: `struct mvebu_a3700_comphy_priv` stores common, lane0/lane1 direct, and lane2 indirect register bases, selector lock, and 40 MHz XTAL state. `struct mvebu_a3700_comphy_lane` stores lane id, requested PHY mode/submode, and polarity inversion. Key callbacks are `mvebu_a3700_comphy_set_mode()`, `mvebu_a3700_comphy_power_on()`, `mvebu_a3700_comphy_power_off()`, and `mvebu_a3700_comphy_xlate()`.

Control flow: Probe maps named resources, detects optional `xtal` clock rate, creates one PHY per child lane, initializes each lane to invalid mode, and powers off all lanes. `set_mode` validates against `mvebu_a3700_comphy_modes[]` and refuses mode changes while powered. Power-on dispatches to mode-specific sequences. SATA selects lane2, clears isolation, sets polarity, 40-bit width, SATA mode, reference clock, max PLL rate, and polls TX PLL ready. USB3 selects lane0 or lane2, programs PIPE, SSC, reference clock, power/PLL bits, idle sync, 20-bit width, speed cap, reset release, and polls PCLK. PCIe is lane1 only and sets PIPE/clock/ref/mode before polling PCLK. Ethernet selects lane0/1, resets sideband pins, chooses 1.25 or 3.125 Gbps, optionally writes the large 40 MHz GBE init table, powers PLL/RX/TX, and polls PLL/RX init.

State and persistence: Mode, submode, and polarity are stored per lane. Selector writes are serialized because the selector register is shared. Hardware COMPHY setup persists until power-off, reset, or a later mode setup.

Dependencies and integration points: Integrates with generic PHY consumers for SATA, PCIe, USB3, and Ethernet; OF child `reg`; two-argument phandle xlate for port and polarity; named MMIO resources; optional XTAL clock; and kernel `enum phy_mode`/Ethernet interface modes.

Risks: Mode/lane combinations are strict, and invalid phandle arguments fail xlate. Lane2 indirect access is shared with SATA/USB3 and relies on address/data ordering. The Ethernet table is hardware-sensitive, especially for 40 MHz references. Power-off is lane-based rather than current-mode-only and may touch inactive alternate functions.

Test signals: DT coverage for all lanes and supported modes, polarity phandle tests, SATA/USB3/PCIe link training, SGMII/1000Base-X/2500Base-X Ethernet on 25 and 40 MHz XTAL boards, PLL timeout paths, and mode-change while powered returning `-EBUSY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-mvebu-a3700-comphy.c -->
