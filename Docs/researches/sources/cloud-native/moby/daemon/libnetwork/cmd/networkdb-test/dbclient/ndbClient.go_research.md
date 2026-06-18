<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cmd/networkdb-test/dbclient/ndbClient.go -->
# sources/cloud-native/moby/daemon/libnetwork/cmd/networkdb-test/dbclient/ndbClient.go

## Purpose
Command-side client for the `networkdb-test` image. It drives a cluster of test servers through diagnostic HTTP endpoints, creating joins/leaves, network table writes/deletes, peer-count checks, queue checks, and convergence assertions.

## Important APIs, Types, And Functions
`Client` dispatches subcommands after resolving `tasks.<service>` and storing the shared `servicePort`. HTTP helpers include `httpGet`, `httpGetFatalError`, `joinCluster`, `joinNetwork`, `leaveNetwork`, `writeTableKey`, and `deleteTableKey`. Measurement helpers include `clusterPeersNumber`, `networkPeersNumber`, `dbTableEntriesNumber`, `dbQueueLength`, `clientWatchTable`, `clientTableEntriesNumber`, `checkTable`, and `waitWriters`. Workload drivers include `doReady`, `doJoin`, `doClusterPeers`, `doWriteKeys`, `doDeleteKeys`, `doWriteUniqueKeys`, `doWriteDeleteUniqueKeys`, and leave/join stress variants.

## Control Flow
The client validates rough argument counts, handles `debug`/`fail`, DNS-resolves service task IPs, then dispatches to a command function. Most commands fan out goroutines across task IPs and collect `resultTuple` values on buffered channels. Write workloads first enable dummy-client watches, start writer goroutines for a bounded count or bounded duration, then repeatedly poll server or watched-client tables until all nodes show the expected count for a stable interval or the context times out.

## State And Persistence
There is no local persistent state. Runtime state is in goroutine channels, DNS-resolved task IPs, context timeouts, and networkdb table entries persisted by the remote servers. `servicePort` is a package global used by polling helpers.

## Dependencies And Integration Points
Integrates with Swarm DNS, diagnostic HTTP paths exposed by `networkdb.NetworkDB`, and dummy-client watch endpoints. It assumes response text contains fixed phrases such as `total entries`, `qlen`, and `total elements`.

## Risks And Edge Cases
Regex parsing indexes matches without nil/length checks, so unexpected responses can panic. Several subcommands are missing from `cmdArgCheck`, so malformed arguments may fail later. `cmdArgCheck` defaults unknown commands to zero required args before the switch rejects them. Writer counts index directly into `ips`, so asking for more writers/leavers than service tasks can panic. Fatal logging makes this appropriate for test orchestration, not reusable library code.

## Test Signals
Success is printed to stderr by each `do*` command with convergence timing. Failures are fatal when peer counts, queue thresholds, table sizes, writer activity, readiness, or HTTP `OK` responses do not match expectations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cmd/networkdb-test/dbclient/ndbClient.go -->
