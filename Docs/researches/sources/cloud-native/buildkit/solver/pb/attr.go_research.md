# sources/cloud-native/buildkit/solver/pb/attr.go

Purpose: this file defines string constants used as attribute keys and well-known attribute values for `pb.SourceOp.Attrs` and related LLB source behavior. It centralizes the keys that frontend code, solver code, and source implementations use to negotiate source-specific options.

Important APIs and constants: Git-related attributes include `AttrKeepGitDir`, `AttrFullRemoteURL`, authentication secrets, known-hosts and SSH socket keys, checksum, submodule, mtime, fetch-by-commit, bundle, checkout bundle, and signature verification options. Local-source attributes cover session identity, uniqueness, include/follow/exclude patterns, shared cache key hints, metadata transfer, and differ mode values. HTTP attributes cover checksum, filename, permission bits, UID/GID, auth header secret, header prefix, and signature verification. Image attributes cover resolve mode values, record type, layer limit, and checksum. OCI layout and LLB-build attributes are also defined.

Control flow: there is no runtime control flow; these constants are consumed by other packages when constructing or interpreting LLB protobuf messages. The only type alias is `type IsFileAction = isFileAction_Action`, which exposes the generated oneof interface under an exported name for code that needs to type against file-action variants.

State and persistence: no state is stored. The constants become part of serialized `SourceOp.Attrs` maps, so changing a key directly affects cache keys, remote compatibility, and how existing serialized definitions are interpreted.

Dependencies and integration points: the constants pair with `ops.proto`'s `SourceOp.attrs` map and with capabilities in `caps.go`. Source handlers for local, git, HTTP, image, OCI layout, and nested LLB build options depend on the exact strings. The historical external contract matters more than internal Go naming.

Risks and test signals: misspelling or changing a constant is compatibility-sensitive. The broader package already preserves one historical typo in `caps.go`, illustrating that string contracts are immutable once used. There are no direct tests in this file; coverage is indirect through LLB serialization, source resolver behavior, frontend emission, and capability negotiation tests.
