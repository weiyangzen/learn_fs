## sources/distributed-fs/ipfs-kubo/test/sharness/t0140-swarm.sh

Purpose: validates `ipfs swarm` and related address behavior, including local address reporting, announce/no-announce config, peering commands, connect/disconnect, and `/p2p` address support.

Important APIs and helpers: uses `ipfs swarm peers`, `swarm addrs local`, `ipfs id`, config keys `Addresses.Announce`, `Addresses.AppendAnnounce`, `Addresses.NoAnnounce`, `ipfs swarm peering ls/add/rm`, and IPTB cluster commands.

Control flow and state: checks disconnected daemon peer/address output, verifies local swarm addresses match `ipfs id`, modifies announce settings and confirms advertised address lists change, tests peering add/remove output and config state, creates a TCP testbed, connects and disconnects peers using transport-stripped addresses and `/p2p` addresses, and verifies IDs and peer address formatting.

Dependencies and integration points: covers swarm address manager, config-driven announce filtering, peering service persistence, peer ID formatting, and libp2p connection commands.

Risks and test signals: catches incorrect advertised addresses, ignored no-announce CIDR filters, peering config regressions, and broken address parsing. Signals are exact address presence/absence, peer counts, and successful connect/disconnect operations.
