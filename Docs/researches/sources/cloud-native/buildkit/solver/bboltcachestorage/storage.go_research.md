## sources/cloud-native/buildkit/solver/bboltcachestorage/storage.go

Purpose: persistent bbolt-backed implementation of solver `CacheKeyStorage`, storing cache result records and dependency links between cache keys.

Important APIs/types/functions: `NewStore` opens bbolt with `NoSync` and creates buckets `_result`, `_links`, `_byresult`, `_backlinks`. `Exists`, `Walk`, `WalkResults`, `Load`, `AddResult`, `Release`, `WalkIDsByResult`, `AddLink`, `WalkLinks`, `HasLink`, and `WalkBacklinks` implement cache metadata operations. `releaseHelper` and `emptyBranchWithParents` recursively delete unreferenced branches. `isEmptyBucket` checks bucket emptiness.

Control flow: results are stored under cache key id and reverse indexed by result id. Links are stored as `json(CacheInfoLink) + "@" + target`, with backlinks for reverse traversal. `Release` walks all cache ids for a result, deletes result entries and reverse indexes, then prunes empty link/result buckets and parent backlinks. Walk methods collect data inside read transactions then call callbacks outside the transaction.

State and persistence: bbolt database persists cache graph metadata, not actual result blobs. `NoSync` improves speed at durability risk. Link digests are normalized in walk methods by hashing digest plus output.

Dependencies and integration points: used by `cacheManager` as durable cache metadata. Actual result storage is a separate `CacheResultStorage`.

Risks and test signals: link key encoding uses `@` separator around JSON; digest strings in JSON should not break split but malformed keys error. Recursive pruning is subtle. `storage_test.go` runs shared cache storage tests.
