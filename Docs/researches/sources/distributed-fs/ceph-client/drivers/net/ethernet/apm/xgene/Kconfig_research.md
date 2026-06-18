## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/Kconfig

Purpose: defines `NET_XGENE`, the original APM X-Gene SoC Ethernet driver.

Important APIs, types, and functions: the symbol is tristate, depends on `ARCH_XGENE || COMPILE_TEST`, selects `PHYLIB`, `MDIO_XGENE`, and `GPIOLIB`, and documents module name `xgene_enet`.

Control flow, state, and dependencies: build-time selection enables the multi-file X-Gene driver supporting RGMII, SGMII, and XGMII modes with PHY, MDIO, GPIO/SFP, and classifier dependencies.

Integration points: paired with `xgene/Makefile`; selected symbols match code paths in `xgene_enet_main.c` and hardware helpers.

Risks: removing selected dependencies will break optional but compiled code paths such as PHY connection, MDIO bus setup, and SFP GPIO lookup. `COMPILE_TEST` should remain available because hardware-specific code benefits from broad build coverage.

Test signals: enable as module and built-in; compile with ACPI/OF, PHYLIB, MDIO_XGENE, and GPIO combinations.
