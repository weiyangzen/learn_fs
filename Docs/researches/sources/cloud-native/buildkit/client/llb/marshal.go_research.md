# sources/cloud-native/buildkit/client/llb/marshal.go

Purpose: shared definition serialization, constraint merging, metadata conversion, marshal caching, and deterministic protobuf marshaling helpers.

Important APIs/types/functions: `Definition` wraps op bytes, metadata, source maps, and constraints. `ToPB`, `FromPB`, `Head`, `WriteTo`, and `ReadFrom` bridge client and protobuf definitions. `MarshalConstraints` merges base/override constraints and emits `pb.Op` plus metadata. `MarshalCache` and `MarshalCacheInstance` cache per-constraints marshal results behind a mutex. `deterministicMarshal` uses deterministic protobuf serialization.

Control flow: definitions convert metadata key types between digest and string. `Head` parses the final pointer op and returns its first input digest. `MarshalConstraints` clones worker constraints, applies override platform/worker constraints/metadata, defaults platform when missing, and returns an op with platform and worker filters. Cache `Acquire` locks, `Load` looks up by constraints pointer, `Store` hashes bytes and records result, `Release` unlocks.

State and persistence: no external persistence except `WriteTo`/`ReadFrom` caller-provided streams. Marshal cache is in-memory and keyed by `*Constraints` identity rather than deep equality.

Dependencies/integration points: protobuf definition/op metadata, containerd platform defaults, digest, BuildKit metadata caps, and every vertex marshal implementation.

Risks/test signals: pointer-keyed cache means equivalent constraints objects do not share cache and mutated constraints under same pointer can reuse stale results. `ReadFrom` reads full stream into memory. Many tests in this subset implicitly verify deterministic byte output and definition roundtrip behavior.
