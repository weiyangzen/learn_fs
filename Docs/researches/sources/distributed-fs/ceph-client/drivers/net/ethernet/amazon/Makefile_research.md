# sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/Makefile

Purpose: this Makefile connects the Amazon Ethernet vendor directory to the ENA subdirectory in Kbuild.

Important APIs, types, and functions: the single rule `obj-$(CONFIG_ENA_ETHERNET) += ena/` includes the `ena` directory when ENA is built-in or modular.

Control flow: there is no runtime behavior. During kernel build, Kbuild descends into `amazon/ena` only when the ENA Kconfig symbol is enabled.

State and persistence: build state is determined solely by `CONFIG_ENA_ETHERNET`.

Dependencies and integration points: it depends on the sibling Kconfig file and the `amazon/ena/Makefile` composite object definition.

Risks: adding another Amazon Ethernet driver would require another conditional subdirectory or object line. A symbol rename in Kconfig without updating this Makefile would silently omit ENA from builds.

Test signals: `make M=drivers/net/ethernet/amazon` with ENA enabled should descend into `ena/`; with ENA disabled it should not build ENA objects.
