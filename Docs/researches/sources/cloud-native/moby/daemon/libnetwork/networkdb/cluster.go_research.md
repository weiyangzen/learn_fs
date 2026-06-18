# sources/cloud-native/moby/daemon/libnetwork/networkdb/cluster.go

## Purpose
Cluster/memberlist orchestration for NetworkDB: key management, memberlist initialization, join/leave, reconnect/rejoin, periodic reaping, gossip fanout, bulk sync, and random peer sampling.

## Important APIs, Types, And Functions
Key functions include `SetKey`, `SetPrimaryKey`, `RemoveKey`, `clusterInit`, `retryJoin`, `clusterJoin`, `clusterLeave`, `triggerFunc`, `reapDeadNode`, `rejoinClusterBootStrap`, `reconnectNode`, `reapState`, `reapNetworks`, `reapTableEntries`, `gossip`, `bulkSyncTables`, `bulkSync`, `bulkSyncNode`, and `mRandomNodes`. Constants define reap/retry periods and rebroadcast queue limits.

## Control Flow
`clusterInit` builds memberlist config, installs delegates, optional keyring, creates transmit queues, starts memberlist, and launches staggered ticker goroutines. Join sends a node join event after memberlist join. Leave sends node leave, asks memberlist to leave, cancels context, stops tickers, and shuts down. Gossip periodically picks up to three random peers per joined network and sends compound table messages. Bulk sync sends all table entries for common networks over reliable TCP and optionally waits for an ACK response.

## State And Persistence
State is in-memory: memberlist instance, keyring, bootstrap IPs, failed/left node maps, timers, queue counters, random generator, table tombstone reap timers, and health/stat timestamps. No disk persistence.

## Dependencies And Integration Points
Integrates with Hashicorp memberlist, NetworkDB delegates, protobuf message encoding, node management helpers, immutable radix indexes, and Docker logging.

## Risks
Concurrency and timing dominate: ticker goroutines must stop on close, locks must not be held across slow network operations except where intended, bulk sync ACK table cleanup must not leak, and tombstone residual times must avoid premature deletion or endless rebroadcast. `mRandomNodes` fairness matters for convergence and load distribution.

## Test Signals
`cluster_test.go` property-tests `mRandomNodes` for exclusion of local node, uniqueness, sample size, permutation coverage, and approximate distribution fairness.
