# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_ethtool.h

Purpose: Minimal internal header declaring ethtool setup for the `bnge` netdev.

Important APIs/types/functions: Exposes `bnge_set_ethtool_ops(struct net_device *dev)`, implemented in `bnge_ethtool.c`, for netdev initialization code to attach the driver's ethtool operation table.

Control flow support: The netdev allocation/configuration path calls this once after creating a `struct net_device` so later ethtool commands dispatch into the bnge handlers.

State/persistence: No state here; the call mutates `dev->ethtool_ops`.

Dependencies/integration: Requires `struct net_device` from Linux networking headers in the including translation unit.

Risks/test signals: Low risk, but missing this call leaves users without bnge ethtool features. Compile-test header inclusion and verify `ethtool -i`, `-S`, pause, and link settings are available after netdev registration.
