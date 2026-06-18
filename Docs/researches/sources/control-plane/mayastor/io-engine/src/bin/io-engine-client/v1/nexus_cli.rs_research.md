<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/nexus_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/nexus_cli.rs

### Purpose
`nexus_cli.rs` implements v1 nexus lifecycle and control commands. It creates named nexus devices, manages sharing and ANA state, lists nexus and child health, adds/removes children, resizes nexus devices, and delegates child state operations.

### Important APIs, Types, And Functions
`NexusArgs` wraps `NexusCommands` for create, destroy, shutdown, publish, unpublish, ANA state, add, remove, list, children, resize, and nested child commands. `NexusShareProtocol`, `ResvType`, and `NvmeAnaState` model CLI enums. `ResvType` converts to `NvmeReservation`. Helper functions map nexus, child, reason, and ANA enum values to strings.

### Control Flow
`nexus_create` treats an empty UUID string as "generate one", defaults name to UUID, requires children, maps reservation type, and sends `CreateNexusRequest` with controller IDs, reservation keys, and nexus-info key. Destroy sends a request then lists nexus for JSON output. List prints name, UUID, size, state, rebuild count, path, and optional child URIs. Children list filters by UUID or name and includes reason plus fault timestamp. Publish defaults to NVMf and propagates allowed hosts. Resize sends requested size and prints confirmation.

### State, Persistence, And Dependencies
All durable effects are remote nexus changes. The module depends on v1 nexus/common protobufs, `byte_unit`, `url`, `uuid`, tonic status, colored JSON, and the shared context. It integrates with replica backends, NVMf target export, rebuild state, and persistent NexusInfo keys.

### Risks And Test Signals
Many response fields and enum conversions use `unwrap`; missing nexus payloads or unknown enum values can panic. Destroy returns a list response in JSON mode rather than the destroy result. Tests should cover generated UUIDs, no-child validation, reservation mapping, publish defaults, allowed hosts, child reason/fault timestamp output, resize request sizing, and unknown/missing response fields.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/nexus_cli.rs -->
