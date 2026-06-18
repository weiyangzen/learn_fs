# sources/distributed-fs/ceph-client/drivers/phy/socionext/phy-uniphier-pcie.c

Purpose: UniPhier PCIe PHY provider for legacy Pro5 and newer LD20/PXs3/NX1 PHY blocks.

Important APIs, types, and functions: `uniphier_pciephy_testio_write/read()` implement the indirect TESTI/TESTO register interface; `uniphier_pciephy_set_param()` modifies PHY internal registers; `uniphier_pciephy_assert/deassert()` control manual PHY reset. `struct uniphier_pciephy_soc_data` distinguishes legacy, dual-PHY, and syscon mode callbacks. `uniphier_pciephy_ld20_setmode()` and `_nx1_setmode()` write USB/PCIe mux syscon bits.

Control flow: probe maps MMIO, obtains either named legacy clocks/resets (`gio`, `link`) or unnamed clock/reset, creates one PHY, optionally sets syscon mux mode, and registers simple xlate. `.init` enables clocks, deasserts resets, selects port 1, and for non-legacy PHYs programs RX EQ, VCO, and clamp settings for one or two PHY IDs before deasserting PHY reset. `.exit` asserts PHY reset for non-legacy devices and unwinds resets/clocks.

State and persistence: private state keeps clock/reset handles and SoC feature flags. Hardware state includes mux selection in syscon and internal PHY TESTIO parameters.

Dependencies and integration points: generic PHY, syscon/regmap, clock/reset framework, DT compatibles for Pro5/LD20/PXs3/NX1, and UniPhier PCIe controller users.

Risks: the driver supports only one port through `PORT_SEL_1`; systems expecting other ports require different data or driver changes. Optional syscon lookup failure is ignored, so mux setup can be silently skipped on bad DT. TESTIO access requires dummy reads and tight sequencing; regressions can be hardware-specific.

Test signals: PCIe enumeration per compatible, DT validation for `socionext,syscon`, link stability on dual PHY NX1, register readback of TESTIO parameters, and compile coverage for legacy/non-legacy paths.
