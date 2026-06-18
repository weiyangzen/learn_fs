# sources/distributed-fs/ceph-client/drivers/net/phy/qcom/Kconfig

Purpose: Defines the Qualcomm/Atheros PHY driver build options under the PHY subsystem. It separates the shared Qualcomm helper library from concrete PHY families so multiple drivers can select common register, interrupt, WoL, LED, cable-test, and statistic helpers.

Important options: `QCOM_NET_PHYLIB` is a hidden tristate selected by all Qualcomm driver families. `AT803X_PHY` builds support for AR8030, AR8031, AR8033, AR8035, and IPQ5018 and depends on `REGULATOR` because AR8031 exposes VDDIO/VDDH regulators. `QCA83XX_PHY` supports internal QCA833x switch PHYs. `QCA808X_PHY` supports QCA8081. `QCA807X_PHY` supports QCA8072/QCA8075 and selects `PHY_PACKAGE`, with an `OF_MDIO` dependency because package-level configuration is device-tree driven.

Control flow: This file has no runtime control flow. Kconfig evaluates dependencies and `select` clauses, then the adjacent Makefile maps enabled symbols to objects. The hidden shared symbol ensures `qcom-phy-lib.o` is linked whenever any family using the exported helpers is enabled.

State and persistence: State is build-time configuration only. Tristate choices determine built-in versus module output and ensure unavailable dependency combinations are rejected before compile time.

Dependencies and integration: Integrates with the parent PHY Kconfig tree, the qcom Makefile, regulator framework availability, OF MDIO package descriptions, and `PHY_PACKAGE` support for multi-PHY packages.

Risks and test signals: Main risks are missing `select QCOM_NET_PHYLIB` for a driver that uses shared symbols, dependency drift for regulator or package APIs, and modules that fail to link when a selected helper is not built. Test with each Qualcomm symbol as `m` and `y`, all disabled, and mixed combinations involving `OF_MDIO`, `REGULATOR`, and `PHY_PACKAGE`.
