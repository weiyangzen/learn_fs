# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockReportLeaseManager.java

## Purpose

`BlockReportLeaseManager` rate-limits full block reports reaching the NameNode by granting a bounded number of leases to datanodes. Lease ID zero remains an intentional bypass for compatibility and manually triggered full block reports.

## Important APIs and types

- `NodeData` stores datanode UUID, lease ID, lease time, and doubly linked-list pointers.
- `register` and `unregister` manage datanode membership.
- `requestLease` grants a nonzero lease when pending leases are below `maxPending`.
- `checkLease` validates a report lease, accepts ID zero, rejects unknown, expired, missing, or mismatched leases.
- `removeLease` clears a lease after use.
- `pruneExpiredPending` and `pruneIfExpired` reclaim expired leases.

## Control flow

Two circular lists partition nodes: deferred nodes without leases and pending nodes with active leases. Registration inserts at the front of deferred. `requestLease` registers unknown datanodes on demand, removes any existing list entry, prunes expired pending leases from the oldest end, and returns zero if the pending cap is reached. Otherwise it issues a new nonzero monotonically advanced ID, records the monotonic timestamp, appends to pending, and increments `numPending`. Successful `removeLease` moves the node to the end of deferred so older reporters can be prioritized.

## State and persistence behavior

All state is in-memory and synchronized on the manager. Lease IDs are initialized from a random long and never use zero. State is lost on NameNode restart, and ID zero compatibility lets reports still be accepted outside the lease flow.

## Dependencies and integration points

It uses NameNode datanode descriptors, DFS full-block-report lease configuration, monotonic time, and heartbeat/block-report protocol fields. It protects `BlockManager` from bursts of expensive full block reports.

## Risks and edge cases

All methods are synchronized, so correctness is simple but latency-sensitive if logging or large pending lists grow. Expiration pruning stops at the first unexpired pending entry, relying on pending list order by lease time. Re-requesting a lease discards the previous lease, which is necessary for datanode restart but invalidates in-flight old reports.

## Test signals

Tests should cover max-pending enforcement, zero-ID bypass, unknown datanode registration, duplicate register/unregister behavior, lease expiry, ID mismatch rejection, nonzero ID generation across overflow, and deferred/pending order after remove.
