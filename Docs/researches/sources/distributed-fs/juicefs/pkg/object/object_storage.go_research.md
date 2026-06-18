# sources/distributed-fs/juicefs/pkg/object/object_storage.go


Purpose: provides shared object-storage infrastructure: registration, default unsupported methods, file metadata helpers, list traversal, temp naming, and tier management.

Important APIs and flow: `Register`, `IsSupported`, and `CreateStorage` manage backend constructors. `DefaultObjectStorage` supplies nil/no-op/`notSupported` implementations so providers can override only supported features. `MarshalObject` and `UnmarshalObject` serialize object/file metadata. `ListAllWithDelimiter` recursively walks delimiter-based listings with prefetch worker goroutines and ordered output. `generateListResult`, `decodeKey`, and `TmpFilePath` are small shared helpers. `tierStorage` implements `SupportTier`, validates tags, encodes tags for HTTP headers, and returns a tier from `context` via `TierKey`.

State and persistence: global state includes `ctx`, logger, `UserAgent`, registry map, and pooled copy buffers. Tier state is per storage instance.

Dependencies and integration: used by nearly every backend. `Shutdown` is defined in `interface.go`; wrappers and providers rely on `DefaultObjectStorage` and tier helpers.

Risks: `storages` map is global and unguarded, safe for init-time registration but not concurrent mutation. `ListAllWithDelimiter` has complex coordination and sends `nil` as an error sentinel. `UnmarshalObject` assumes JSON-decoded numeric fields are `float64` and can panic on malformed maps. `TmpFilePath` uses `math/rand` global randomness, not collision-proof.

Test signals: broad indirect coverage through all storage tests; `TestMarsharl`, `TestNameString`, and `TestListAllWithDelimiterDeepStart` cover selected helpers.
