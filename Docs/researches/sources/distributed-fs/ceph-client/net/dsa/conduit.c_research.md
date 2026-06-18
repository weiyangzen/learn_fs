# sources/distributed-fs/ceph-client/net/dsa/conduit.c

## Purpose
This file manages DSA conduit devices: the CPU-facing netdevs through which switch traffic enters and leaves the host. It augments conduit ethtool operations with switch-side statistics/registers, exposes a sysfs `dsa/tagging` selector for runtime tag-protocol changes, adjusts MTU/promiscuity for tag overhead, validates hardware timestamp ownership, and handles conduit LAG setup/teardown.

## Important APIs, Types, And Functions
Public functions are `dsa_conduit_setup()`, `dsa_conduit_teardown()`, `dsa_conduit_lag_setup()`, `dsa_conduit_lag_teardown()`, and `__dsa_conduit_hwtstamp_validate()`. Internal ethtool wrappers are `dsa_conduit_get_regs_len()`, `dsa_conduit_get_regs()`, `dsa_conduit_get_ethtool_stats()`, `dsa_conduit_get_ethtool_phy_stats()`, `dsa_conduit_get_sset_count()`, and `dsa_conduit_get_strings()`.

The sysfs attribute `tagging` uses `dsa_tag_protocol_to_str()`, `dsa_tag_driver_get_by_name()`, `dsa_tree_change_tag_proto()`, and `dsa_tag_driver_put()` to switch the active tagger.

## Control Flow
Setup computes conduit MTU as Ethernet payload plus tag overhead, creates a device link from switch to conduit parent when possible, sets MTU, publishes `dev->dsa_ptr` after a write barrier, forces promiscuity if required by the tagger or missing unicast filtering, installs ethtool wrappers, and creates the sysfs group. Teardown removes sysfs, restores original ethtool ops, resets MTU to `ETH_DATA_LEN`, drops promiscuity, clears `dsa_ptr`, and issues another write barrier.

Ettool wrappers first call original conduit operations when present, then append CPU/DSA port data from every shared DSA port in the tree with stable string prefixes `sXX_pXX_`. HWTSTAMP validation rejects timestamping on the conduit if any switch port supports hardware timestamping, steering timestamp configuration to DSA user ports.

LAG setup ensures the LAG master is a conduit if not already, then joins the CPU port to the LAG. Teardown leaves the LAG and only tears down the conduit when no DSA user upper remains.

## State And Persistence
Runtime state is stored in `dev->dsa_ptr`, `cpu_dp->orig_ethtool_ops`, conduit MTU/promiscuity, sysfs group membership, and LAG membership in `struct dsa_port`. All state is in kernel memory and unwound during tree teardown or LAG leave.

## Dependencies And Integration Points
The file integrates with netdev ethtool ops, sysfs, device links, LAG netdevs, DSA tag drivers, `dsa_tree_change_tag_proto()`, port LAG helpers, phylink/hwtstamp policy, and DSA receive routing via `dev->dsa_ptr`.

## Risks And Edge Cases
Failure after MTU adjustment but before full setup currently unwinds promiscuity and ethtool state but does not reset MTU in the early error path. Runtime tagger switching depends on driver support and must restore module references correctly on failure. LAG teardown scans uppers under RCU assumptions; callers must satisfy locking expectations. `dsa_conduit_get_strings()` assumes original `ops` is non-NULL in one branch, so conduit devices without ethtool ops need careful coverage.

## Test Signals
Tests should cover conduit setup/teardown, ethtool stats/register aggregation, tagger sysfs show/store success/failure, MTU changes for tag overhead, hwtstamp rejection when a switch supports timestamping, and CPU-port LAG join/leave rollback.
