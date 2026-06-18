# sources/distributed-fs/lizardfs/src/nfs-ganesha/fileinfo_cache_unittest.cc

## Purpose
Provides GoogleTest coverage for the pNFS fileinfo cache.

## Important APIs, Types, And Functions
Defines tests `FileInfoCache.Basic`, `FileInfoCache.Full`, and `FileInfoCache.Reset`. They use create/acquire/attach/extract/release/pop/free/reset/destroy APIs.

## Control Flow
The basic test verifies that acquiring new entries has no fileinfo, attaching values persists across release/reacquire by inode, and expired entries can be popped after release. The full test creates more entries than the configured max, erases one active entry, releases the rest, and expects three expired pops. Reset confirms a long-timeout cache does not expire until parameters are reset to zero.

## State And Persistence Behavior
Tests use fake pointer values as fileinfo payloads and do not release real LizardFS handles. They exercise in-memory cache state only.

## Dependencies And Integration Points
Depends on `fileinfo_cache.h` and GoogleTest. It is built as part of the local test suite when nfs-ganesha tests are enabled.

## Risks And Edge Cases
No concurrency test, no real time delay test, and no attached-handle cleanup verification. The timestamp-unit bug is unlikely to be detected because all tested timeouts are zero or reset to zero.

## Test Signals
These tests are useful smoke coverage for list/tree transitions and parameter reset but should be supplemented with race and timeout-boundary tests.
