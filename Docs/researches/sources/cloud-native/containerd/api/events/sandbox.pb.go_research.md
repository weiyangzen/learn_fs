# sources/cloud-native/containerd/api/events/sandbox.pb.go

Purpose: generated Go protobuf bindings for sandbox lifecycle event payloads.

Important APIs/types/functions: defines `SandboxCreate`, `SandboxStart`, and `SandboxExit`. Create/start carry `SandboxID`; exit carries `SandboxID`, `ExitStatus`, and `ExitedAt *timestamppb.Timestamp`. Generated getters return zero values for nil receivers.

Control flow: only protobuf reflection/descriptor initialization and field getters. `file_events_sandbox_proto_init` registers three message types and timestamp dependency metadata.

State/persistence: no internal persistence. Wire fields capture sandbox lifecycle facts emitted elsewhere.

Dependencies/integration: depends on protobuf runtime/reflection and `google.protobuf.Timestamp`. Integrates with sandbox runtimes and event consumers tracking sandbox start/exit.

Risks/test signals: fieldpath generation for sandbox events handles only `sandbox_id`, so filters cannot directly match exit status or timestamp. Tests should validate timestamp marshaling and event consumers' handling of zero exit status versus unset fields.
