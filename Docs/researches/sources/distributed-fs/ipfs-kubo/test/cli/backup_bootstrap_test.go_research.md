# sources/distributed-fs/ipfs-kubo/test/cli/backup_bootstrap_test.go

Purpose: integration test for backup bootstrap peer persistence and reconnection. It verifies that peers learned during runtime can be saved as temporary backup bootstrap peers and used after restart to rejoin a small network.

Important test: `TestBackupBootstrapPeers`. It creates three nodes, clears configured bootstrap peers, assigns random local swarm ports, disables mDNS, and sets `Internal.BackupBootstrapInterval` to 250 ms. Nodes 0 and 1 are connected, then stopped after backup time; nodes 1 and 2 form a connection; node 0 restarts and is expected to discover both peers.

Control flow starts all daemons, checks initial peer counts, connects pairs, sleeps for backup persistence, restarts selected daemons, then asserts all three peer counts reach 2. State includes peerstore/swarm connections and whatever backup bootstrap storage Kubo writes in the repo. Dependencies include local networking, harness `Connect`, config mutation, and timing intervals. Risks include sleep-based timing, port contention, and peer connection convergence delays. Test signal is end-to-end: backup bootstrap should restore enough connectivity to bridge the three-node graph.
