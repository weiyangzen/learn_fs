# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/DefaultJournalMaster.java

## Purpose
`DefaultJournalMaster` implements journal management RPCs for master and job-master processes. It exposes embedded-journal quorum operations and node-state reporting through a master service.

## Important APIs, types, and functions
The constructor captures `JournalDomain`, `JournalSystem`, and `PrimarySelector` from `MasterContext`. `getQuorumInfo()`, `removeQuorumServer(NetAddress)`, `transferLeadership(NetAddress)`, `resetPriorities()`, and `getTransferLeaderMessage(String)` delegate to `RaftJournalSystem` after `checkQuorumOpSupported()`. `getNodeState()` returns primary selector state. `getName()` and `getServices()` integrate with the master service registry.

## Control flow
Quorum operations first verify the journal system is `RaftJournalSystem` and that the local process is the Raft leader. Unsupported journal type or non-leader calls throw `UnsupportedOperationException`. Service registration wraps `JournalMasterClientServiceHandler` with `ClientContextServerInjector`.

## State and persistence behavior
This master is `NoopJournaled`; it does not persist independent state. It manipulates the embedded journal subsystem, whose Raft state is persisted elsewhere.

## Dependencies and integration points
It depends on `AbstractMaster`, `MasterContext`, `RaftJournalSystem`, `PrimarySelector`, gRPC service definitions, and client-context injection. CLI/admin clients reach it through `JournalMasterClientServiceHandler`.

## Risks
Quorum operations must be routed to the current Raft leader or they fail. The exception message says quorum operations are supported for journal type `EMBEDDED` when rejecting non-Raft systems, which can be confusing wording. Casting after support checks must remain aligned with journal-system implementations.

## Test signals
Tests should cover UFS journal rejection, non-leader rejection, successful Raft delegation, node-state response, service map contents, and handler exception propagation.
