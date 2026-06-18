# sources/cloud-native/containerd/api/events/sandbox_fieldpath.pb.go

Purpose: generated fieldpath accessors for sandbox events.

Important APIs/types/functions: `Field` methods for `SandboxCreate`, `SandboxStart`, and `SandboxExit` expose only `sandbox_id`. The `SandboxExit` method comments `exit_status` and `exited_at` as unhandled.

Control flow: empty paths return false; a switch on the first segment returns the sandbox ID if non-empty; unknown or unsupported fields return false.

State/persistence: no state; fieldpath output is computed from the event message.

Dependencies/integration: no external imports. Used by event filtering systems that operate on string field values.

Risks/test signals: callers cannot filter sandbox exits by exit status or timestamp through this helper. This is a deliberate limitation of the generator's supported scalar/string handling and should be documented in filter behavior tests.
