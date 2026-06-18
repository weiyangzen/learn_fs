# sources/cloud-native/containerd/api/events/sandbox.proto

Purpose: source schema for sandbox lifecycle events.

Important APIs/types/functions: package `containerd.events`, Go package `api/events;events`. `SandboxCreate` and `SandboxStart` contain `sandbox_id`; `SandboxExit` adds `exit_status` and `google.protobuf.Timestamp exited_at`.

Control flow: declarative event payload definition. Runtime behavior is outside this file in sandbox/runtime components that publish events.

State/persistence: field numbers define persistent API compatibility. No storage.

Dependencies/integration: imports `google/protobuf/timestamp.proto`. Unlike several peer event protos, it does not import `types/fieldpath.proto` or set `fieldpath_all`, though a generated fieldpath file exists for string fields.

Risks/test signals: timestamp presence and zero exit code need clear consumer interpretation. Tests should cover create/start/exit event publication and backward compatibility for the three fields.
