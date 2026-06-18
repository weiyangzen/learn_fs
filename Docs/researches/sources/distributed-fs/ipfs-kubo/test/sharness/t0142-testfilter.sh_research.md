## sources/distributed-fs/ipfs-kubo/test/sharness/t0142-testfilter.sh

Purpose: verifies swarm address filters are enforced during real peer connection attempts.

Important APIs and helpers: uses IPTB setup, `ipfsi config Swarm.AddrFilters`, `iptb start`, `iptb connect`, `ipfsi swarm peers`, and DNS-style addresses.

Control flow and state: creates a multi-node testbed, applies a filter for `127.0.0.0/24` on one node, starts the cluster, confirms connections involving the filtered node fail in both directions including DNS addresses, and confirms other unfiltered nodes can connect. State is per-node swarm filter config and live libp2p connections.

Dependencies and integration points: covers address filter enforcement, transport dialing, DNS multiaddr resolution, and IPTB cluster connectivity.

Risks and test signals: catches filters that only affect displayed addresses but not actual dialing, or that overblock unrelated peers. Pass signals are failed filtered connects, zero peer count for blocked nodes, and successful allowed connects.
