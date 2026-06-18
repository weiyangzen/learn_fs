## sources/distributed-fs/ipfs-kubo/test/sharness/t0121-bootstrap-iptb.sh

Purpose: verifies that bootstrap peer configuration affects real swarm connectivity in an IPTB cluster.

Important APIs and helpers: defines `betterwait`, uses `iptb testbed create`, `iptb start/stop/reset`, `ipfsi swarm peers`, `ipfsi bootstrap add/rm`, and disables mDNS to isolate bootstrap behavior.

Control flow and state: creates a local multi-node testbed, disables mDNS, starts nodes without bootstrap connectivity and checks peer counts, stops and resets nodes, configures bootstrap addresses, restarts, and checks the expected number of swarm peers. Persistent state is each node's bootstrap config and peerstore state after reset.

Dependencies and integration points: covers IPTB orchestration, Kubo bootstrap dialing, swarm peer discovery, mDNS isolation, and multi-node startup timing.

Risks and test signals: catches bootstrap peers being ignored, mDNS hiding bootstrap failures, and cluster timing issues. Pass signals are peer count checks before and after bootstrap configuration.
