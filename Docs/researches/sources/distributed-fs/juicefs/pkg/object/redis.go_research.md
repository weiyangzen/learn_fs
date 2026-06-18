# sources/distributed-fs/juicefs/pkg/object/redis.go

Purpose: implements a Redis-backed object store for chunk data using Redis keys as object keys and values as object bytes.

Important APIs and types: `redisStore` embeds `DefaultObjectStorage` and holds a `redis.UniversalClient` plus sanitized URI. It implements `String`, `Get`, `Put`, `Delete`, `Head`, `ListAll`, and `newRedis`.

Control flow and state: `Put` reads the whole input into memory and writes `SET key value` without expiration. `Get` reads the whole value and slices it for range behavior. `Head` reads the value to report size and maps `redis.Nil` to `os.ErrNotExist`. `ListAll` scans either a single client or all cluster masters, filters keys greater than `marker`, sorts them globally, then pipelines `STRLEN` in batches to emit `obj` metadata.

Persistence and integration: persistence is Redis durability and cluster topology dependent. `newRedis` supports standard, cluster, and sentinel/failover URI shapes, explicit username/password overrides, sentinel password via `SENTINEL_PASSWORD_FOR_OBJ`, TLS settings from parsed URL, and disabled retries by default.

Risks and test signals: scanning all keys is explicitly slow for many objects; `Get`/`Head`/`Put` are whole-value operations and memory-bound. Reported mtimes are current time, not object modification time. No Redis-specific tests are included.
