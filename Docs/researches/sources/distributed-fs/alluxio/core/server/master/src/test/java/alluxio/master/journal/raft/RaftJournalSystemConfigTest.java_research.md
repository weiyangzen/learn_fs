# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/raft/RaftJournalSystemConfigTest.java

## Purpose
`RaftJournalSystemConfigTest` validates how `RaftJournalSystem` derives local and cluster raft addresses from master and job-master configuration.

## Important APIs, Types, and Functions
It constructs `RaftJournalSystem` for `ServiceType.MASTER_RAFT` and `JOB_MASTER_RAFT`, uses reflection helpers `getLocalAddress` and `getClusterAddresses`, and checks `NetworkAddressUtils.containsLocalIp`.

## Control Flow, State, and Persistence
Each test sets relevant `PropertyKey` values, creates a journal system with a temporary URI, reflects its private address fields, and asserts host/port derivation. Cleanup reloads configuration after each test.

## Dependencies and Integration Points
The test depends on Alluxio configuration keys for master hostname, embedded journal addresses and ports, job-master hostname and journal addresses, temporary folders, service-type defaults, Guava sets, and network address utilities.

## Risks
The test reaches private fields reflectively, so internal field renames break it even if behavior is preserved. Address derivation is sensitive to hostname defaults and local-IP matching.

## Test Signals
Signals include default master port `19200`, explicit master raft port propagation, master hostname derivation, job-master hostname fallback from master hostname, job-master port override from master addresses, direct job-master address parsing, and local IP containment when hostnames differ.
