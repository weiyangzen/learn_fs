<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/swarm/node.go -->
# sources/cloud-native/moby/api/types/swarm/node.go

## Purpose
Node represents a node.

## Important APIs, Types, And Functions
- Exported types: Node, NodeSpec, NodeRole, NodeAvailability, NodeDescription, Platform, EngineDescription, NodeCSIInfo, PluginDescription, NodeStatus, Reachability, ManagerStatus, NodeState, Topology.
- Constants: NodeRoleWorker, NodeRoleManager, NodeAvailabilityActive, NodeAvailabilityPause, NodeAvailabilityDrain, ReachabilityUnknown, ReachabilityUnreachable, ReachabilityReachable, NodeStateUnknown, NodeStateDown, NodeStateReady, NodeStateDisconnected.
- `Node` fields include ID, Spec, Description, Status, ManagerStatus.
- `NodeSpec` fields include Role, Availability.
- `NodeDescription` fields include Hostname, Platform, Resources, Engine, TLSInfo, CSIInfo.
- `Platform` fields include Architecture, OS.
- `EngineDescription` fields include EngineVersion, Labels, Plugins.
- Source comments highlight: Node represents a node. NodeSpec represents the spec of a node. NodeRole represents the role of a node.

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.

## Test Signals
- Package-level tests include `network_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/swarm/node.go -->
