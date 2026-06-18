## sources/cloud-native/buildkit/session/sshforward/ssh.pb.go

Purpose: generated protobuf message bindings for `ssh.proto`.

Important APIs/types/functions: defines `BytesMessage` with `Data []byte`, `CheckAgentRequest` with `ID string`, and empty `CheckAgentResponse`. Each type has generated `Reset`, `String`, `ProtoMessage`, `ProtoReflect`, deprecated `Descriptor`, and getter methods. The file descriptor encodes the `moby.sshforward.v1.SSH` service with unary `CheckAgent` and bidirectional streaming `ForwardAgent`.

Control flow: there is no handwritten control flow. Generated methods delegate to `protoimpl` for reflection, descriptor compression, message info storage, and init-time type construction.

State and persistence: message state is per-instance protobuf runtime state, unknown fields, and size cache. No persistence is performed here.

Dependencies and integration points: generated from `github.com/moby/buildkit/session/sshforward/ssh.proto`; used by `ssh.go`, `raw_provider.go`, vtproto fast paths, and generated gRPC stubs.

Risks and test signals: do not manually edit. Schema changes must be made in `ssh.proto` and regenerated with matching protoc/protoc-gen-go versions. Compatibility risk is field-number stability: `data = 1` and `ID = 1` must remain compatible with clients. Functional behavior is tested through provider and SSH forwarding tests rather than generated methods directly.
