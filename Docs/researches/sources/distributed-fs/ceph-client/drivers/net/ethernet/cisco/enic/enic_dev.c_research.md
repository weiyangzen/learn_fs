<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_dev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_dev.c

## Purpose

`enic_dev.c` provides locked wrappers around vNIC firmware device commands and small netdev-facing VLAN callbacks. It centralizes devcmd serialization and firmware status-to-errno translation.

## Important APIs, Types, and Functions

Wrappers include `enic_dev_fw_info`, `enic_dev_stats_dump`, station address add/delete, packet filter programming, arbitrary address add/delete, notification unset, hang notification, ingress VLAN rewrite mode setup, enable/disable reference counting, interrupt coalescing timer info, VLAN add/delete callbacks, and `enic_dev_status_to_errno`.

`enic_dev_enable` and `enic_dev_disable` maintain `enic->enable_count` so nested users only trigger firmware enable on first enable and firmware disable after the last disable.

## Control Flow

Most functions take `devcmd_lock` with bottom halves disabled, call the corresponding `vnic_dev_*` helper, and unlock. VLAN callbacks run under RTNL and delegate to `enic_add_vlan`/`enic_del_vlan` under the same lock. Status conversion maps firmware `ERR_*` codes to Linux negative errno values.

## State and Persistence Behavior

The wrappers mutate firmware state such as addresses, packet filters, VLAN tables, notification buffers, device enable state, and ingress VLAN rewrite mode. Local persistent state is limited to `enable_count` and generic stats such as any error accounting done by lower layers.

## Dependencies and Integration Points

The file depends on `vnic_dev`, `vnic_vic`, `enic_res`, `enic.h`, and `enic_dev.h`. It is called by open/stop/reset/probe paths, ethtool, address filtering, VLAN operations, and port-profile code.

## Risks and Edge Cases

Correct lock coverage is important because devcmd is a shared firmware mailbox. Enable-count imbalance would leave the vNIC enabled or disabled incorrectly. Address wrappers validate the station MAC but not arbitrary multicast/unicast addresses, relying on callers. Firmware status conversion defaults unknown positive statuses to `-1`, which is less specific than standard errno.

## Test Signals

Exercise firmware info/stats retrieval, open/stop enable-count transitions, filter mode changes, station MAC add/delete, VLAN add/delete, ingress VLAN rewrite programming, firmware failure status mapping, and concurrent devcmd callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_dev.c -->
