## sources/distributed-fs/ipfs-kubo/test/sharness/t0280-plugin-peerlog.sh

Purpose: tests the peerlog plugin's default-disabled behavior and config-enabled logging of peer IDs in an `iptb` cluster.

Important commands and control flow: creates a two-node testbed and starts it, then asserts node 0 logs do not contain `peerlog`. It stops, recreates the testbed, sets `Plugins.Plugins.peerlog.Config.Enabled true`, starts again, checks logs for `peerlog`, obtains node 1's peer ID, and confirms node 0 logs include that ID.

State and persistence: config state is written through `ipfs config` inside each testbed repo. Runtime state is daemon logs and peer connections.

Dependencies and integration points: depends on `iptb`, `startup_cluster`, Kubo plugin config namespacing, daemon logging, and peer discovery/connection startup.

Risks and test signals: sensitive to log timing and exact log inclusion. It provides useful coverage that plugin config is honored and peer observation hooks are active only when enabled.
