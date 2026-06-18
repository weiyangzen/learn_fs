<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/subrequests/convertllb/convertllb.go -->
# sources/cloud-native/buildkit/frontend/subrequests/convertllb/convertllb.go

Purpose: defines the `frontend.convertllb` subrequest result format for converting a Dockerfile frontend invocation into an inspectable LLB graph. It packages protobuf solver operations, op metadata, and the root source into gateway result metadata.

Important APIs, types, and functions: `RequestConvertLLB` is the public request id. `SubrequestConvertLLBDefinition` declares version `0.1.0`, RPC type, description, and `result.json` metadata. `Result` carries `Def map[digest.Digest]*pb.Op`, `Metadata map[digest.Digest]llb.OpMetadata`, and `Source *pb.Source`. `(*Result).ToResult` creates a `client.Result`, adds formatted JSON under `result.json`, and records the request version. `(*Result).MarshalJSON` custom-marshals protobuf fields using `protojson`.

Control flow and state: the file is stateless apart from the request definition. Serialization iterates over digest-keyed ops, marshals each `pb.Op`, copies metadata directly, marshals `Source`, and then delegates to `encoding/json` for the final envelope.

Dependencies and integration: integrates with `frontend/gateway/client.Result` metadata, `client/llb` metadata, `solver/pb` protobuf types, and OCI digests. Dockerfile frontend code can expose this subrequest and buildctl-style callers can read `result.json`.

Risks and test signals: `MarshalJSON` assumes `Source` is non-nil and returns protobuf marshal errors directly. Digest-keyed JSON maps depend on digest string encoding. There are no direct tests in this file; coverage should come from frontend subrequest tests that assert valid `result.json` and version metadata.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/subrequests/convertllb/convertllb.go -->
