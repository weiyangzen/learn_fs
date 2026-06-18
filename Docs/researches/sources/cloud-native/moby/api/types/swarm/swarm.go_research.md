<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/swarm/swarm.go -->
# sources/cloud-native/moby/api/types/swarm/swarm.go

## Purpose
ClusterInfo represents info about the cluster for outputting in "info" it contains the same
information as "Swarm", but without the JoinTokens

## Important APIs, Types, And Functions
- Exported types: ClusterInfo, Swarm, JoinTokens, Spec, OrchestrationConfig, TaskDefaults, EncryptionConfig, RaftConfig, DispatcherConfig, CAConfig, ExternalCAProtocol, ExternalCA, InitRequest, JoinRequest, UnlockRequest, LocalNodeState, Info, Peer, and others.
- Constants: LocalNodeStateInactive, LocalNodeStatePending, LocalNodeStateActive, LocalNodeStateError, LocalNodeStateLocked, ExternalCAProtocolCFSSL.
- `ClusterInfo` fields include ID, Spec, TLSInfo, RootRotationInProgress, DefaultAddrPool, SubnetSize, DataPathPort.
- `Swarm` fields include JoinTokens.
- `JoinTokens` fields include Worker, Manager.
- `Spec` fields include Orchestration, Raft, Dispatcher, CAConfig, TaskDefaults, EncryptionConfig.
- `OrchestrationConfig` fields include TaskHistoryRetentionLimit.
- Source comments highlight: ClusterInfo represents info about the cluster for outputting in "info" it contains the same information as "Swarm", but without the JoinTokens Swarm represents a swarm. JoinTokens contains the tokens workers and managers need to join the swarm.

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Imports: `net/netip`, `time`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.
- Uses `net/netip` typed IP/prefix values, preserving validated address semantics instead of raw strings.
- Carries timestamp or duration fields that must remain JSON-compatible across daemon/client boundaries.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.
- Address parsing and JSON behavior depend on `netip` semantics; invalid or legacy textual addresses need explicit handling upstream.
- Duration and timestamp fields need stable units and timezone/zero-value behavior across API versions.

## Test Signals
- Package-level tests include `network_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/swarm/swarm.go -->
