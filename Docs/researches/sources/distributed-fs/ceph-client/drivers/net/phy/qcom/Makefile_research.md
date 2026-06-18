# sources/distributed-fs/ceph-client/drivers/net/phy/qcom/Makefile

Purpose: Maps Qualcomm PHY Kconfig symbols to kbuild objects.

Important entries: `CONFIG_QCOM_NET_PHYLIB` builds `qcom-phy-lib.o`; `CONFIG_AT803X_PHY` builds `at803x.o`; `CONFIG_QCA83XX_PHY` builds `qca83xx.o`; `CONFIG_QCA808X_PHY` builds `qca808x.o`; `CONFIG_QCA807X_PHY` builds `qca807x.o`.

Control flow: kbuild expands each `obj-$(CONFIG_...)` line to either built-in object linkage, module linkage, or omission. Because family Kconfig options select `QCOM_NET_PHYLIB`, shared helper symbols are available to the family modules.

State and persistence: No runtime state. This is persistent build metadata only.

Dependencies and integration: Integrates with `drivers/net/phy/qcom/Kconfig`, module autoload tables in each C driver, and the kernel's composite object/module build process.

Risks and test signals: Risks are stale symbol names, missing object entries for new drivers, or helper object omission leading to unresolved exports. Test by building every legal built-in/module combination and confirming expected module/object names.
