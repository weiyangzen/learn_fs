# sources/cloud-native/moby/daemon/logger/jsonfilelog/jsonlog/jsonlog.go

Purpose: defines the decoded JSON log record shape.

Important APIs/types/functions: `JSONLog` has `Log`, `Stream`, `Created`, and optional `Attrs`. `Reset` zeroes scalar fields and clears the attrs map in place.

Control flow/state/persistence: no I/O. The struct tags define persisted json-file field names.

Dependencies/integration: used by `jsonfilelog/read.go` for decoding and by tests.

Risks: `Reset` preserves the map allocation when present; callers must not retain and mutate shared decoded maps unexpectedly.

Test signals: decoder/read tests validate field mappings and reset reuse.
