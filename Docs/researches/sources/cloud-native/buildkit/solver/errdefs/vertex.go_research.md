<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/vertex.go -->
## sources/cloud-native/buildkit/solver/errdefs/vertex.go

Purpose: associates errors with the LLB vertex digest that produced them and registers vertex/source error details.

Important APIs and types: `VertexError` wraps `*Vertex` and an underlying error, implements `Unwrap` and `ToProto`. `WrapVertex(err, dgst)` builds a `Vertex{Digest: dgst.String()}` detail; `(*Vertex).WrapError` rebuilds from decoded details. `init` registers both `Vertex` and `Source`.

Control flow: nil errors pass through. Shared op code defers `WrapVertex` so cache/exec failures consistently include the original LLB digest.

State and dependencies: no persistence. Dependencies include `typeurl`, BuildKit `grpcerrors`, and OCI `digest`.

Integration points: solver execution, cache, and slow-cache paths use this to link failures back to graph vertices and progress UI entries.

Risks and test signals: the file stores digest as string, so invalid or empty digests are not validated here. Direct tests are absent; scheduler/solve tests indirectly depend on error wrapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/vertex.go -->
