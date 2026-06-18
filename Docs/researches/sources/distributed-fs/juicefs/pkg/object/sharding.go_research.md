# sources/distributed-fs/juicefs/pkg/object/sharding.go

Purpose: composes multiple object stores into a deterministic key-sharded object store and supplies generic full-list helpers.

Important APIs and types: `sharded` holds `stores []ObjectStorage`, hashes keys with FNV-1a in `pick`, and implements object CRUD, tier support, multipart for same-key shards, restore, and merged `ListAll`. Package-level `ListAll` provides generic paginated listing fallback. `nextKey` and `nextObjects` implement a heap for k-way merge.

Control flow and state: writes, reads, heads, deletes, multipart, and restore route to the shard chosen by hashing the key. `Copy` is unsupported because source and destination could hash to different shards. `ListAll` first tries a backend-native method, then falls back to `List`, then to delimiter traversal if simple listing is unsupported. Sharded `ListAll` starts listing each shard, consumes first objects, and heap-merges sorted streams.

Persistence and integration: persistent state is distributed across endpoint instances created by `NewSharded`, which formats the endpoint string with shard index and calls `CreateStorage`.

Risks and test signals: key hash changes would relocate data. Shard list merge assumes each shard stream is sorted and uses nil as failure/end sentinel. Multipart upload-part-copy is disabled in limits. No direct tests in this subset.
