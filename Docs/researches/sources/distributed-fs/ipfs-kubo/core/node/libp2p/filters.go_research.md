# sources/distributed-fs/ipfs-kubo/core/node/libp2p/filters.go

Purpose: adapts multiaddr filters into libp2p's `connmgr.ConnectionGater`. Important type is `filtersConnectionGater`.

Control flow: `InterceptAddrDial`, `InterceptAccept`, and `InterceptSecured` deny addresses blocked by the filter. `InterceptPeerDial` and `InterceptUpgraded` always allow, because filtering is address-level rather than peer-level after upgrade.

State and persistence: no persistence; the gater is an in-memory wrapper over `ma.Filters`.

Dependencies/integration: depends on libp2p connmgr/control/network/peer and multiaddr filters. Created by `AddrFilters` in `addrs.go` and passed to libp2p as `ConnectionGater`.

Risks: filtering at multiple phases can reject inbound and outbound connections; peer-level allowance means bad peers are not blocked absent address matches. No direct tests for the adapter, but address behavior is covered through `addrs_test.go`.
