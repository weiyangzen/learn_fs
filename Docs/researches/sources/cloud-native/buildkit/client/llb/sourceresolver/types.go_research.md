# sources/cloud-native/buildkit/client/llb/sourceresolver/types.go

Purpose: type definitions for source metadata resolver requests and responses across image, OCI layout, git, and HTTP sources.

Important APIs/types/functions: `ResolverType`, `MetaResolver`, `Opt`, `MetaResponse`, `ResolveImageOpt`, `ResolveImageResponse`, `AttestationChain`, `Blob`, `ResolveGitOpt`, `ResolveGitResponse`, `ResolveHTTPOpt`, checksum request/response types, `ResolveOCILayoutOpt`, and `ResolveImageConfigOptStore`.

Control flow: no executable flow; structs are populated by callers and resolver implementations.

State and persistence: no internal state. `Opt` can carry source policies, platform, resolve modes, attestation requests, OCI store IDs, git return-object flags, and HTTP checksum requests.

Dependencies/integration points: solver `pb.SourceOp`, source policy protobuf, OCI descriptors/digests/platforms, and resolver implementations such as `imageresolver.go`.

Risks/test signals: these structs are cross-package contracts; field changes affect frontends, resolver implementations, and client image metadata flows. No direct tests in this subset.
