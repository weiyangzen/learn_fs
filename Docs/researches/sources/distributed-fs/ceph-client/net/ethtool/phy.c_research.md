# sources/distributed-fs/ceph-client/net/ethtool/phy.c

## Purpose
This file implements netlink `PHY_GET`, exposing metadata for PHY devices attached to a netdevice or selected by PHY index: PHY index, driver name, MDIO device name, upstream topology, and SFP bus names.

## Important APIs, Types, And Functions
`struct phy_reply_data` stores copied strings and topology fields. Main callbacks are `phy_prepare_data()`, `phy_reply_size()`, `phy_fill_reply()`, and `phy_cleanup_data()`. `ethnl_phy_request_ops` registers a per-PHY GET operation.

## Control Flow
Preparation resolves the target PHY with `ethnl_req_get_phydev()`, finds its node in `dev->link_topo->phys`, copies the MDIO name, optional driver name, upstream type, optional upstream PHY index, parent SFP bus name, and downstream SFP bus name. Fill emits the scalar and string attributes, and cleanup frees all copied strings.

## State And Persistence
The file is read-only. Reply strings are duplicated per request and freed after reply or dump item completion.

## Dependencies And Integration Points
It depends on PHY link topology (`struct phy_link_topology`, xarray of PHY nodes), SFP bus names, `ethnl_req_get_phydev()`, and per-PHY dump support in `netlink.c`. RTNL is expected to be held while topology is inspected.

## Risks And Edge Cases
Missing or null PHY returns `-EOPNOTSUPP` rather than a more specific no-device status. `upstream_index` is emitted only if nonzero, so a valid upstream PHY index of zero would be suppressed; PHY indexes are generally minimum one in header policy. Partial allocation failures unwind already duplicated strings.

## Test Signals
Tests should cover attached PHY default selection, explicit `phy_index`, missing topology node, PHY without driver, upstream PHY versus SFP topology, downstream SFP name, and allocation failure cleanup.
