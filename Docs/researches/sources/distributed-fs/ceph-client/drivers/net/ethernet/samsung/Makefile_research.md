# sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/Makefile

Purpose: top-level Samsung Ethernet build glue.

Important rule: `obj-$(CONFIG_SXGBE_ETH) += sxgbe/` descends into the SXGBE driver directory when the config is built-in or modular.

Control flow: Kbuild expands the directory object according to `CONFIG_SXGBE_ETH`; the subdirectory Makefile assembles the concrete module objects.

State and persistence: no runtime state; only Kbuild object selection.

Dependencies and integration: tied to `drivers/net/ethernet/samsung/Kconfig` and the subdirectory `sxgbe/Makefile`.

Risks: none beyond ensuring config and directory names stay aligned. If additional Samsung drivers are added, this file is the inclusion point.

Test signals: built-in and module builds of `CONFIG_SXGBE_ETH`, and no descent when the option is unset.
