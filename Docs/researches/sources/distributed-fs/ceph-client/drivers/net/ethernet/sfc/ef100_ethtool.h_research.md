<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_ethtool.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_ethtool.h

## Purpose
Publishes the EF100 ethtool operation table for netdevice registration.

## Important APIs, Types, And Functions
- `extern const struct ethtool_ops ef100_ethtool_ops;` is consumed by `ef100_netdev.c`.

## Control Flow
No executable control flow exists. The declaration lets `ef100_register_netdev()` attach the operations table defined in `ef100_ethtool.c`.

## State And Persistence
No runtime state is owned here. The declared object is immutable operation-table metadata.

## Dependencies And Integration Points
Integrates EF100 netdev setup with ethtool handling. Consumers need Linux `struct ethtool_ops` visibility via existing kernel includes.

## Risks And Edge Cases
Like `ef100.h`, this is a minimal declaration-only header without an include guard. It is safe as written, but future expansion should add a guard and explicit ethtool type includes.

## Test Signals
Compile-time linkage and successful `net_dev->ethtool_ops` assignment validate this header. Runtime ethtool command success validates the linked table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_ethtool.h -->
