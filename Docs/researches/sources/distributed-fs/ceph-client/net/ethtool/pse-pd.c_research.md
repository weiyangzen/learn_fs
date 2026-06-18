<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/pse-pd.c -->
# sources/distributed-fs/ceph-client/net/ethtool/pse-pd.c

## Purpose
Implements the ethtool generic-netlink interface for Ethernet PSE and PD control and status. It exposes `ETHTOOL_MSG_PSE_GET`, `ETHTOOL_MSG_PSE_SET`, and PSE event notification plumbing for PHY-attached Power Sourcing Equipment, including PoDL, Clause 33, available power limits, power limit ranges, priority, and device identity.

## APIs, Types, and Functions
The file defines `struct pse_req_info`, `struct pse_reply_data`, `ethnl_pse_get_policy`, `ethnl_pse_set_policy`, and `ethnl_pse_request_ops`. The read path is `pse_prepare_data()`, `pse_get_pse_attributes()`, `pse_reply_size()`, `pse_fill_reply()`, `pse_put_pw_limit_ranges()`, and `pse_cleanup_data()`. The write path is `ethnl_set_pse_validate()` and `ethnl_set_pse()`. `ethnl_pse_send_ntf()` is exported for drivers or PSE core code to multicast PSE event bits.

## Control Flow, State, and Persistence
GET resolves the target PHY from the ethtool header, enters the device ethtool critical section with `ethnl_ops_begin()`, validates that a `phy_device` and `phydev->psec` exist, clears `data->status`, then delegates to `pse_ethtool_get_status()`. Reply sizing and serialization are sparse: only positive or nonzero status fields are emitted, and allocated power limit ranges are released in cleanup. SET resolves the same PHY, validates attached PSE support and PoDL/C33 capability, then applies priority, available power limit, and admin control changes in sequence. The file itself persists no configuration; persistence is in the PSE controller reached through `phydev->psec`.

## Dependencies and Integration
Depends on ethtool netlink helpers, phylib, and the PSE core in `linux/pse-pd/pse.h`. Integration points are `ethnl_req_get_phydev()`, `ethnl_ops_begin()/complete()`, `pse_ethtool_get_status()`, `pse_ethtool_set_prio()`, `pse_ethtool_set_pw_limit()`, `pse_ethtool_set_config()`, and `ethnl_multicast()`.

## Risks and Test Signals
Risks include partial SET ordering if earlier updates succeed and later updates fail, mismatch between reply size and optional fields, driver/PSE allocations for `c33_pw_limit_ranges`, and unsupported PHY/PSE paths returning accurate extack messages. Test signals are netlink policy validation, GET with no PHY, GET with no PSE, SET unsupported PoDL/C33 controls, range serialization, priority update, power-limit update, and notification multicast failure tolerance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/pse-pd.c -->
