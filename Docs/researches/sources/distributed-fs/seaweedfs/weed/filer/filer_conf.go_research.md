<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_conf.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_conf.go

## Purpose
Loads, stores, matches, mutates, and serializes filer path configuration. These rules drive collection, replication, TTL, disk type, read-only, chunk-deletion, WORM, and quota-derived behavior.

## Important APIs and Types
`FilerConf` wraps a prefix trie of `filer_pb.FilerConf_PathConf`. Key functions are `ReadFilerConf`, `ReadFilerConfFromFilers`, `NewFilerConf`, `loadFromFiler`, `LoadFromBytes`, `MatchStorageRule`, `ClonePathConf`, `ApplyBucketQuotaReadOnly`, `GetCollectionTtls`, `mergePathConf`, `ToProto`, and `ToText`.

## Control Flow and State
Remote reads first try one of the supplied filer gRPC addresses, using either `ReadEntry` with a master client or `ReadInsideFiler`. Local loads read `/etc/seaweedfs/filer.conf` from inline content or chunks. Prefix matching uses a fast path: no match returns immutable `emptyPathConf`, one match returns the stored config, multiple matches merge all matching prefixes into a new config.

## Persistence Behavior
Config is persisted as a filer entry under `/etc/seaweedfs/filer.conf`, encoded as protobuf JSON. In-memory trie state is replaced or mutated by setters and reload paths.

## Dependencies and Integration Points
Depends on filer protobufs, `ptrie`, gRPC filer clients, master chunk reading, and utility proto text/JSON. Storage rules feed volume assignment, chunk deletion disabling, max filename lengths, and bucket quota read-only toggling.

## Risks
`doLoadConf` returns nil on `SetLocationConf` error, losing the original error. `MatchStorageRule` can return pointers callers must not mutate; unsafe callers can corrupt shared config. Merge semantics are mostly OR/non-empty, so nested rules cannot clear booleans inherited from broader prefixes.

## Test Signals
`filer_conf_test.go` covers prefix merge, clone completeness by reflection, nil clone, and quota read-only toggling. It does not cover load parse failures, gRPC failover, or text serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_conf.go -->
