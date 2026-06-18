## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/Makefile

Purpose: defines the original X-Gene Ethernet module object list.

Important APIs, types, and functions: `xgene-enet-objs` links `xgene_enet_hw.o`, `xgene_enet_sgmac.o`, `xgene_enet_xgmac.o`, `xgene_enet_main.o`, `xgene_enet_ring2.o`, `xgene_enet_ethtool.o`, and `xgene_enet_cle.o`; `obj-$(CONFIG_NET_XGENE)` emits `xgene-enet.o`.

Control flow, state, and dependencies: all MAC variants, ring variants, ethtool, classifier, and platform netdev code are compiled into one module so runtime PHY mode and hardware version choose operation tables.

Integration points: must include every file that implements operation-table symbols referenced by `xgene_enet_main.c`.

Risks: object omissions produce link failures for `xgene_gmac_ops`, `xgene_sgmac_ops`, `xgene_xgmac_ops`, `xgene_ring2_ops`, or `xgene_cle3in_ops`. Reordering is low risk but symbol inclusion is critical.

Test signals: build `M=drivers/net/ethernet/apm/xgene`; verify a single `xgene-enet.o` module and no unresolved operation-table symbols.
