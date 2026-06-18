# sources/distributed-fs/juicefs/pkg/meta/info_test.go

## Purpose

`info_test.go` provides focused unit coverage for Redis version comparison, Redis version parsing, and parsing of selected fields from a raw Redis `INFO` response.

## Important Tests

`TestOlderThan` constructs `redisVersion{"2.2.10", 2, 2}` and checks comparison against newer major, newer minor, same version, older minor, itself, and the zero value. It asserts that comparison uses only major/minor ordering and that equality is not considered older.

`TestParseRedisVersion` has an invalid subtest with empty, nonnumeric, and missing-minor strings, all expected to return errors. Its valid subtest parses `6.2.19`, verifies `major == 6`, `minor == 2`, and confirms `String()` preserves the full original patch version.

`TestParseRedisInfo` embeds a large multiline Redis `INFO` fixture covering many sections. It calls `checkRedisInfo` and asserts `redisVersion == "6.1.240"`, `aofEnabled == false`, and `maxMemoryPolicy == "allkeys-lru"`.

## Control Flow And Test Data

The tests use standard Go `testing` subtests and fatal assertions. The large INFO fixture intentionally includes comments, indentation, unrelated fields, and `aof_enabled:0`, exercising line trimming, comment skipping, and selective field extraction. It does not assert on warning logs.

## Dependencies And Integration Points

The tests are same-package (`package meta`), so they access unexported `redisVersion`, `parseRedisVersion`, and `checkRedisInfo` directly. They serve as regression coverage for Redis backend initialization logic without requiring a live Redis instance.

## Risks And Gaps

No test covers a too-old but parseable version because `checkRedisInfo` calls `logger.Fatalf`, which is hard to assert without intercepting process exit/fatal behavior. `storage_provider:flash` behavior is not tested. The warning path for malformed `redis_version` inside `INFO` is not checked. The tests also do not verify `maxmemory_policy` handling beyond storing the value; any policy validation would need separate coverage.

## Test Signals

These tests are low-cost unit tests and should be run with normal package tests. They primarily signal parser stability and guard against accidental changes in major/minor comparison semantics.
