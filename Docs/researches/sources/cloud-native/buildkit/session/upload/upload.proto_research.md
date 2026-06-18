## sources/cloud-native/buildkit/session/upload/upload.proto

Purpose: declares the BuildKit session upload streaming contract.

Important APIs/types/functions: package `moby.upload.v1`, Go package `github.com/moby/buildkit/session/upload`. Service `Upload` has a bidirectional streaming `Pull(stream BytesMessage) returns (stream BytesMessage)`. `BytesMessage` contains raw `bytes data = 1`.

Control flow: runtime users currently use the server-to-client direction to send chunks from an `io.ReadCloser` and the client receives until EOF. The bidirectional signature leaves room for request messages, but provider code in this subset ignores inbound messages and only sends data.

State and persistence: none in schema.

Dependencies and integration points: generates `upload.pb.go`, `upload_grpc.pb.go`, and `upload_vtproto.pb.go`; used by session upload helper and provider.

Risks and test signals: changing stream direction or field number would break existing clients. Since the schema is minimal, most risk sits in provider lifecycle and chunking rather than protobuf design.
