<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/stack/stack.pb.go -->
# sources/cloud-native/buildkit/util/stack/stack.pb.go

Purpose: generated Go protobuf bindings for `stack.proto`.

Important APIs and types: messages `Stack` and `Frame`, getters, `ProtoReflect`, descriptors, and initialization function `file_github_com_moby_buildkit_util_stack_stack_proto_init`.

Control flow: standard `protoc-gen-go` output builds a file descriptor with two messages. Message getters return zero values on nil receivers. Reset and ProtoReflect wire messages into the protobuf runtime.

State and persistence: protobuf message state, unknown fields, and size cache are embedded per object. Descriptor raw data is compressed once through `sync.Once`.

Dependencies and integration: used by `stack.go`, vtprotobuf generated helpers, typeurl registration, and any protobuf serialization/deserialization of BuildKit stack traces.

Risks: generated file should not be hand-edited; schema changes must flow from `stack.proto` regeneration. Field names for `Frame` are capitalized in proto, which is reflected in generated JSON/protobuf names.

Test signals: no direct generated-code tests; exercised indirectly by stack consumers.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/stack/stack.pb.go -->
