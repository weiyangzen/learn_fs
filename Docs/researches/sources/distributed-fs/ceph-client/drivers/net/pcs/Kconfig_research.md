# sources/distributed-fs/ceph-client/drivers/net/pcs/Kconfig

Purpose: Defines Kconfig entries for PCS-layer drivers in this directory.

Important APIs, types, and functions: `PCS_XPCS` is a tristate for Synopsys DesignWare Ethernet XPCS and selects `PHYLINK`. `PCS_LYNX` is a tristate helper library for NXP Layerscape/QorIQ Lynx PCS. `PCS_MTK_LYNXI` is a tristate helper selecting `PHY_COMMON_PROPS` and `REGMAP`. `PCS_RZN1_MIIC` is a user-visible tristate for Renesas RZ/N1, RZ/N2H, and RZ/T2H MII converter PCS, depending on OF and Renesas architecture or compile-test.

Control flow: These symbols control which object files the PCS Makefile builds and which phylink helper providers are available to MAC drivers.

State and persistence behavior: No runtime state; this is build configuration.

Dependencies and integration points: It integrates with the kernel networking driver menu, phylink, regmap, OF, architecture symbols, and compile-test coverage.

Risks and edge cases: Library-style symbols such as `PCS_LYNX` and `PCS_MTK_LYNXI` are not prompt-visible here, so consumers must select them. Missing `PHYLINK`/`REGMAP` selections would surface as link errors. The Renesas driver is OF-only.

Test signals: Kconfig matrix builds for each symbol as built-in/module, allmodconfig, allyesconfig, compile-test without Renesas hardware, and consumer drivers selecting hidden library symbols.
