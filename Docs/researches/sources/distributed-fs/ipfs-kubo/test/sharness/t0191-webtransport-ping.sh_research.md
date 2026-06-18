## sources/distributed-fs/ipfs-kubo/test/sharness/t0191-webtransport-ping.sh

Purpose: validates peer ping over WebTransport swarm addresses.

Important APIs and helpers: uses IPTB, `ipfsi config --json Addresses.Swarm`, peer IDs, `ipfsi ping -n2`, self-ping failure, zero-count failure, and cluster stop.

Control flow and state: initializes a two-node testbed, configures WebTransport addresses, starts nodes, records identities, performs bidirectional remote pings, asserts self-ping and `-n0` calls fail, then stops IPTB.

Dependencies and integration points: covers WebTransport transport setup, TLS/cert requirements hidden in Kubo transport config, libp2p ping, and command argument validation.

Risks and test signals: catches WebTransport listener or dialer regressions and command validation drift. Passing requires remote ping success over WebTransport and expected failures for invalid ping targets/counts.
