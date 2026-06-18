# sources/distributed-fs/ceph-client/drivers/phy/mscc/phy-ocelot-serdes.c

Purpose: This driver provides a generic PHY provider for the Microsemi Ocelot HSIO SerDes block. It creates one PHY per SerDes macro, lets consumers request a macro by port and index, muxes the HSIO hardware configuration for SGMII/QSGMII, and initializes either 1G or 6G SerDes lanes through regmap programming.

Important APIs/types/functions: `struct serdes_ctrl` holds the shared HSIO regmap and `phys[SERDES_MAX]`; `struct serdes_macro` stores a macro index, assigned port, and backpointer. MCB helpers `serdes_update_mcb_s1g/s6g()` and `serdes_commit_mcb_s1g/s6g()` trigger read/write one-shot operations and poll for completion. `serdes_init_s1g()` and `serdes_init_s6g()` program analog/digital lane settings. `struct serdes_mux` and `ocelot_serdes_muxes[]` encode legal macro/port/mode/submode combinations. The exported PHY op is `serdes_set_mode()`, and OF translation is handled by `serdes_simple_xlate()`.

Control flow: Probe obtains the syscon regmap from the parent node, falling back to named regmap resource lookup, creates `SERDES_MAX` PHYs, stores `serdes_macro` drvdata for each, and registers an OF PHY provider. Consumer phandle translation passes a port and SerDes index; non-QSGMII macros become busy once assigned, while `SERDES6G(0)` may serve QSGMII. `set_mode()` rejects non-Ethernet mode, searches the mux table, updates `HSIO_HW_CFG`, then initializes the selected 1G or 6G macro.

State and persistence: Driver state is in each macro's assigned `port` and the shared hardware register state. There is no remove-time reset and no persistent software storage. Register writes persist until reset or reconfiguration by another consumer.

Dependencies and integration points: It depends on OF, platform devices, generic PHY, regmap/syscon, `soc/mscc/ocelot_hsio.h`, and `dt-bindings/phy/phy-ocelot-serdes.h`. Ethernet MAC/PCS consumers are expected to call `phy_set_mode_ext()` or equivalent generic PHY APIs with SGMII/QSGMII submodes.

Risks: The mux table is the correctness boundary; missing or wrong entries break port-to-lane routing. `serdes_set_mode()` rejects `PHY_MODE_PCIE` even though a PCIe mux entry exists, so PCIe is intentionally unsupported. There is limited locking around macro port assignment, so concurrent consumers would rely on normal probe ordering. Initialization uses fixed sleeps and many unchecked `regmap_update_bits()` calls after early poll checks.

Test signals: Device-tree phandle translation should reject bad arg counts, invalid indexes, and busy macros. Runtime tests should validate SGMII and QSGMII links on all supported port mappings, MCB poll timeouts, HSIO mux bits, and stable link after mode changes. PCIe requests should fail with `-EOPNOTSUPP`.
