## sources/cloud-native/buildkit/solver/errdefs/errdefs.proto

Purpose: schema for typed solver errors and metadata attached to BuildKit gRPC errors.

Important APIs/types/functions: messages identify failing vertices, sources with ranges, frontends, frontend capabilities, compatibility features, subrequests, solve context, file actions, content cache entries, and incomplete provenance materials. `Solve` carries input IDs, mount IDs, the failing `pb.Op`, a oneof subject for file/cache, and description map.

Control flow: schema only; runtime wrappers in neighboring files attach these messages to errors and gRPC utilities serialize them.

State and persistence: serialized proto payloads can persist in error responses/logs, not as solver state.

Dependencies and integration points: imports `github.com/moby/buildkit/solver/pb/ops.proto`; generates `errdefs.pb.go` and vtproto variants. Used throughout solver/frontend error handling to preserve machine-readable context.

Risks and test signals: compatibility depends on stable field numbers and oneof membership. Adding fields is safe; renaming/removing/renumbering is not. Neighbor tests cover selected typed error propagation such as provenance.
