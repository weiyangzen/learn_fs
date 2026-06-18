# sources/distributed-fs/ceph-client/include/linux/phylib_stubs.h

## Purpose
Small indirection layer allowing networking code to call selected PHYLIB services while tolerating PHYLIB being optional.

## Important APIs, Types, and Functions
When PHYLIB is enabled, declares global `phylib_stubs` and `struct phylib_stubs` callbacks for hardware timestamp get/set, PHY stats, and link extended stats. Inline wrappers `phy_hwtstamp_get()`, `phy_hwtstamp_set()`, `phy_ethtool_get_phy_stats()`, and `phy_ethtool_get_link_ext_stats()` assert RTNL, check the stub table, and dispatch or return/do nothing. Disabled builds return `-EOPNOTSUPP` or no-op.

## Control Flow
Callers enter under RTNL, wrapper checks whether PHYLIB registered the stub table, then dispatches. Registration/unregistration is synchronized externally under RTNL.

## State and Persistence
The only persistent state is the global callback-table pointer supplied by PHYLIB.

## Dependencies and Integration Points
Depends on rtnetlink locking, ethtool stats/timestamp structures, netlink extack, and optional PHYLIB module state.

## Risks
Calling without RTNL violates synchronization. Null stub table must be treated as unsupported. Callback pointer lifetime depends on PHYLIB registration discipline.

## Test Signals
Builds with PHYLIB enabled/disabled, RTNL lockdep assertions, timestamp get/set tests, and ethtool stats calls before and after PHYLIB stub registration.
