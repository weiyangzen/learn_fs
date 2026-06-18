# sources/cloud-native/containerd/api/events/task_fieldpath.pb.go

Purpose: generated fieldpath accessors for task event messages.

Important APIs/types/functions: `Field` methods expose string fields across task messages: container IDs, bundle, checkpoint, IO stream paths, exec IDs, and task exit/delete IDs. Numeric, boolean, timestamp, and repeated mount fields are marked unhandled in comments.

Control flow: each method guards empty paths, switches on first path segment, and returns non-empty string field values. Nested `TaskCreate.io.*` delegates to `TaskIO.Field` when `IO` is non-nil.

State/persistence: stateless runtime field lookup.

Dependencies/integration: no external imports. Used by event filters that match string-valued task event fields.

Risks/test signals: filters cannot match PID, exit status, terminal, timestamps, or rootfs mounts through these generated helpers. `TaskCreate.io` is absent if the nested message is nil. Tests should cover nested IO lookup, unsupported fields returning false, and empty string IDs.
