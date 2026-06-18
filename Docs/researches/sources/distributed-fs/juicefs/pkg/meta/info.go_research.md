# sources/distributed-fs/juicefs/pkg/meta/info.go

## Purpose

`info.go` parses selected Redis/KeyDB `INFO` fields and enforces minimum compatibility assumptions for Redis-backed metadata. It is a small safety layer used during metadata client setup to warn about durability-sensitive Redis settings and reject too-old server versions.

## Important APIs, Types, And Functions

`redisVersion` stores the original version string plus parsed `major` and `minor` numbers. `oldestSupportedVer` is `4.0.x`. `parseRedisVersion` splits a string on `.`, requires at least major/minor components, parses the first two components with `strconv.Atoi`, and preserves the original string for logging. `redisVersion.olderThan` compares major, then minor. `String` returns the original version string.

`redisInfo` stores four parsed fields: `aofEnabled`, `maxMemoryPolicy`, `redisVersion`, and `storageProvider`. `checkRedisInfo` scans a raw `INFO` response line by line, skips blank/comment lines, splits `key:value`, and handles `aof_enabled`, `maxmemory_policy`, `redis_version`, and `storage_provider`. For Redis version parsing errors it logs a warning; for a parsed version older than `oldestSupportedVer` it calls `logger.Fatalf`. For `aof_enabled:0` it logs a data-loss warning. For `storage_provider`, only `flash` is retained; `none` and absent values collapse to the empty string.

## Control Flow And State

The parser is stateless and returns a `redisInfo` value plus an error, although normal malformed non-version lines are ignored rather than surfaced. Fatal version rejection is process-level behavior through the logger, not an ordinary returned error. This means callers cannot recover from too-old Redis unless the logger fatal behavior is intercepted in tests.

## Dependencies And Integration Points

The file depends only on `fmt`, `strconv`, `strings`, and the package logger. It is tied to Redis metadata backends and likely called by Redis client initialization code after fetching server info. The `storageProvider` field supports KeyDB/flash distinctions without exposing provider-specific parsing elsewhere.

## Risks And Edge Cases

Only major/minor are compared; patch and prerelease/build metadata are ignored. Version strings such as `6.2.19` parse, while `3` or nonnumeric components fail. On parse failure the warning currently formats the zero-value parsed version rather than the raw string in the `%q` slot, which may make diagnostics less clear. `checkRedisInfo` does not enforce `maxmemory_policy` or AOF, it only records/warns, so higher-level code must decide how to react.

## Test Signals

`info_test.go` covers `olderThan`, invalid/valid version parsing, `String`, and a large representative Redis `INFO` payload where `redis_version`, `aof_enabled`, and `maxmemory_policy` are extracted.
