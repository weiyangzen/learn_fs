## sources/distributed-fs/ipfs-kubo/test/sharness/lib/iptb-lib.sh

Purpose: sharness helper library for iptb-backed multi-node Kubo clusters.

Important functions and control flow: `ipfsi` runs `ipfs` commands in a numbered iptb node. `check_has_connection` inspects swarm peers for expected connectivity. `iptb` wraps the binary with the local testbed path. `startup_cluster` initializes, starts, waits for, and connects a cluster, writing useful node addresses and peer IDs. `iptb_wait_stop` waits for node shutdown.

State and dependencies: operates on iptb testbed directories in the current test trash area and on daemon processes managed by iptb. Dependencies include the `iptb` helper binary, Kubo daemons, shell polling, and sharness assertions.

Risks: cluster startup is timing-sensitive and depends on process cleanup. Incorrect testbed paths can leak or target wrong nodes. Test signals are successful cluster start/connect/stop and expected swarm peer visibility.
