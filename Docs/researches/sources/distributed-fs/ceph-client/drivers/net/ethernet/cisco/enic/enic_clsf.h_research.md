<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_clsf.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_clsf.h

## Purpose

`enic_clsf.h` declares ENIC classifier/RFS helpers and provides timer wrappers that compile away when accelerated RFS is disabled.

## Important APIs, Types, and Definitions

It defines `ENIC_CLSF_EXPIRE_COUNT` as 128 buckets per expiry pass. It declares `enic_addfltr_5t`, `enic_delfltr`, RFS table init/free, and filter-ID lookup. Under `CONFIG_RFS_ACCEL`, it declares `enic_rx_flow_steer` and `enic_flow_may_expire`, plus inline `enic_rfs_timer_start` and `enic_rfs_timer_stop`. Without RFS, the timer helpers are empty.

## Control Flow

The header has no direct runtime flow except inline timer setup/deletion when RFS acceleration is enabled.

## State and Persistence Behavior

Timer helpers operate on `enic->rfs_h.rfs_may_expire`; otherwise no state is stored here.

## Dependencies and Integration Points

It includes `vnic_dev.h` and `enic.h`, and is used by `enic_main.c` and `enic_ethtool.c` to integrate RFS and ethtool RXNFC behavior.

## Risks and Edge Cases

The compile-time split must stay consistent with netdev ops: `ndo_rx_flow_steer` is only installed under `CONFIG_RFS_ACCEL`. Timer deletion uses synchronous deletion to avoid use-after-free of classifier nodes.

## Test Signals

Build with and without `CONFIG_RFS_ACCEL`, verify timer lifecycle during open/stop, and exercise ethtool RXNFC rule views for active RFS filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_clsf.h -->
