## sources/cloud-native/moby/daemon/libnetwork/networkdb/networkdb_test.go

Purpose: primary deterministic integration test suite for NetworkDB cluster behavior, node lifecycle, network membership, table CRUD, watches, bulk sync, garbage collection, node state transitions, reincarnation, parallel writes, and island/rejoin behavior.

Important APIs/types/functions: helpers include `launchNode`, `createNetworkDBInstances`, `closeNetworkDBInstances`, `verifyNodeExistence`, `verifyNetworkExistence`, `verifyEntryExistence`, `testWatch`, and `dumpTable`. Tests cover `Join`, `JoinNetwork`, `LeaveNetwork`, `CreateEntry`, `UpdateEntry`, `DeleteEntry`, `GetEntry`, `WalkTable`, `Watch`, `findNode`, `changeNodeState`, and `purgeReincarnation`.

Control flow: tests allocate loopback-bound memberlist ports from an atomic counter, form clusters by joining each new node to the previous node, poll for full peer visibility, then exercise operations and poll for replicated state. Several tests close nodes to force leave/failure handling and restart nodes with new IDs but reused addresses to verify reincarnation cleanup.

State and persistence behavior: NetworkDB state is in in-memory cluster maps and Lamport-clocked tables; tests inspect `nodes`, `leftNodes`, `failedNodes`, `thisNodeNetworks`, and entry counters directly. `TestNetworkDBGarbageCollection` configures reaping intervals and checks tombstone count decay. `TestMain` attempts to enable IPv6 on loopback and sets debug logging.

Dependencies and integration points: uses real `memberlist`, local network sockets, `containerd/log`, `go-events`, `errdefs`, and libnetwork string IDs. These tests integrate generated protobuf messages, gossip delegates, node management, watch broadcasting, and table storage.

Risks: tests are timing- and host-network-sensitive, particularly IPv6 setup, port reuse, memberlist timing, and long GC sleeps. Direct internal map inspection gives strong coverage but can couple tests to implementation shape. Parallel create/delete tests validate single-writer success but depend on race-safe NetworkDB internals.

Test signals: broad regression coverage. Specific signals include multi-network joins/leaves, isolation of non-member nodes, 1000-entry bulk sync, medium-cluster CRUD under concurrent reads, tombstone GC, node state map transitions, reincarnation by address/port, and cluster island recovery.
