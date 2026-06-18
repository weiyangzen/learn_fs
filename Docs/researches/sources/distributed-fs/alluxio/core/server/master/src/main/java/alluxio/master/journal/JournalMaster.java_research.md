# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/JournalMaster.java

## Purpose
`JournalMaster` defines the master-facing contract for journal administration. It covers quorum inspection/mutation, leadership transfer, priority reset, transfer status messages, and node-state inspection.

## Important APIs, types, and functions
Methods are `getQuorumInfo()`, `removeQuorumServer(NetAddress)`, `transferLeadership(NetAddress)`, `resetPriorities()`, `getTransferLeaderMessage(String)`, and `getNodeState()`. It extends the generic `Master` interface.

## Control flow
The interface has no implementation flow, but method documentation states quorum operations are supported only for embedded journals, while `getNodeState` works for both UFS and embedded journals.

## State and persistence behavior
No state is defined here. Implementations decide whether state is journaled; `DefaultJournalMaster` is no-op journaled and delegates to the journal system.

## Dependencies and integration points
It depends on gRPC response/address types and the `Master` lifecycle/service contract. Client service handlers and factories target this interface.

## Risks
The interface mixes universally available node-state calls with embedded-only quorum calls, so clients must handle unsupported-operation errors. Transfer leadership returns a string transfer id rather than a structured status.

## Test signals
Contract tests should validate client behavior for supported and unsupported journal types, IOException propagation, and transfer-message lookup.
