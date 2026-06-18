<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/stack/stack.proto -->
# sources/cloud-native/buildkit/util/stack/stack.proto

Purpose: protobuf schema for serializable BuildKit stack trace data.

Important APIs and types: `Stack` message with repeated `Frame`, repeated command line, pid, version, and revision; `Frame` message with name, file, and line.

Control flow: declarative schema only; generated Go code is in `stack.pb.go` and vtproto helpers in `stack_vtproto.pb.go`.

State and persistence: defines the wire contract for persisted or transported stack traces.

Dependencies and integration: `go_package` targets `github.com/moby/buildkit/util/stack`; `stack.go` registers this type with containerd typeurl.

Risks: field numbers are persistent wire compatibility commitments. Changing or reusing field numbers would break serialized stack data.

Test signals: generated code is not directly tested; stack extraction/formatting tests cover usage.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/stack/stack.proto -->
