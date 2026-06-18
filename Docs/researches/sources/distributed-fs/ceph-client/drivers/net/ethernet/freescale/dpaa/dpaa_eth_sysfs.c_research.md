# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa/dpaa_eth_sysfs.c

## Purpose
This sidecar creates read-only sysfs attributes for DPAA1 netdevs, exposing MAC device address range, frame queue IDs, and buffer pool IDs.

## Important APIs, Types, and Functions
`dpaa_eth_show_addr()` prints `mac_dev->res->start` or `none`. `dpaa_eth_show_fqids()` iterates `priv->dpaa_fq_list`, groups contiguous FQID ranges of the same queue type, and labels RX default/error/PCD, TX, TX confirmation, and TX error queues. `dpaa_eth_show_bpids()` prints the primary BPID. `dpaa_eth_sysfs_init()` creates `device_addr`, `fqids`, and `bpids`; `dpaa_eth_sysfs_remove()` removes them.

## Control Flow
Probe calls `dpaa_eth_sysfs_init()` after registering the netdev. If any attribute creation fails, the function removes earlier files and returns without aborting probe. Remove calls `dpaa_eth_sysfs_remove()` to delete all known attributes.

## State and Persistence
The file exposes live driver state but does not own persistent state. Attribute contents reflect the current `dpaa_priv`, FQ list, and buffer pool.

## Dependencies and Integration Points
It depends on `to_net_dev()`, `netdev_priv()`, `struct dpaa_priv`, list traversal, and Linux device attributes. It integrates with the main driver's probe/remove lifecycle.

## Risks
The show methods use `sprintf()`/manual byte counts and assume output fits in a page. Very large FQ lists can approach sysfs page limits. The FQ grouping compares string pointer identity (`str == prevstr`), which is safe here because labels are string literals assigned in the switch. `dpaa_eth_sysfs_remove()` removes all attributes regardless of whether creation partially failed, which is acceptable for device attributes.

## Test Signals
Check `/sys/class/net/<if>/device_addr`, `fqids`, and `bpids` after probe; validate output on interfaces with many TX queues and PCD queues; exercise partial creation failure via fault injection.
