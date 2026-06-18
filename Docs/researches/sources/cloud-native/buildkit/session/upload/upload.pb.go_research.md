## sources/cloud-native/buildkit/session/upload/upload.pb.go

Purpose: generated protobuf message bindings for `upload.proto`.

Important APIs/types/functions: defines `BytesMessage` with `Data []byte` and standard generated protobuf methods/getters. The file descriptor encodes the `moby.upload.v1.Upload` service and its bidirectional streaming `Pull` method.

Control flow: generated `Reset`, `String`, reflection, descriptor, getter, and init functions delegate to protobuf runtime. There is no handwritten logic.

State and persistence: per-message protobuf runtime state, unknown fields, and size cache only.

Dependencies and integration points: consumed by `upload.go`, `uploadprovider/provider.go`, `upload_grpc.pb.go`, and vtproto helpers. Generated from `github.com/moby/buildkit/session/upload/upload.proto`.

Risks and test signals: field number `data = 1` must remain stable for wire compatibility. Generated file should not be edited manually. Behavioral coverage comes from upload provider/client paths outside this generated file.
