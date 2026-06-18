# sources/distributed-fs/juicefs/pkg/meta/base_test.go

## Purpose

This is the main cross-backend behavioral test suite for JuiceFS metadata engines. It drives a `Meta` implementation through Redis, Redis Cluster/KeyDB when available, SQL/TKV through other tests in the package, and the common `baseMeta` helpers. The suite intentionally validates filesystem semantics rather than only backend storage details: inode creation and deletion, lookup and path resolution, sessions, permissions, POSIX and BSD locks, chunk/slice accounting, compaction, trash, clone, quota, directory statistics, ACLs, Kerberos token persistence, atime modes, and read-only behavior.

## Important APIs, Types, And Helpers

`testConfig` and `testFormat` define the standard test fixture: default config with short directory-stat flushes and a format with `DirStats` enabled. `checkResult`, `waitCheckResult`, and `assertInodes` are polling helpers for asynchronous session-flushed directory usage. `TestRedisClient`, `TestKeyDB`, and `TestRedisCluster` create Redis-family clients and run `testMeta`; KeyDB also inspects Redis `INFO` fields to ensure flash and memory policies are compatible.

`testMeta` is the suite coordinator. After `Reset`, it calls feature-specific helpers in a fixed order and mutates `base.conf` for later feature modes such as open-cache, case-insensitive lookup, and read-only enforcement. `testContext` is a minimal `Context` implementation for quota ownership tests; it fixes uid/gid without cancellation.

Backend-specific repair helpers appear in `setAttr`, `testClone`, and lock cleanup checks. They branch over `*redisMeta`, `*dbMeta`, and `*kvMeta` to directly alter inode rows/keys, detached-node records, Redis lock sets, xorm rows, and kv keys.

## Control Flow And Coverage

The basic metadata path in `testMetaClient` initializes and loads format state, creates a session, verifies root attributes, exercises directory/file create, lookup of `.` and `..`, permission checks, SGID inheritance, `SetAttr`, directory reads, rename modes (`RenameWhiteout`, `RenameNoReplace`, `RenameExchange`), hardlinks, symlinks, open/close, slice writes/reads, fallocate validation, xattr create/replace/list/remove, `StatFS` with global capacity/inode limits, chrooted subdir statfs, directory quota-limited statfs, and recursive summaries.

Separate helpers stress special flows: `testAccess` and `testACL` validate POSIX mode and ACL mask/owner/group behavior plus ACL inheritance and cache loading. `testStickyBit`, `testResolve`, and `testReadOnly` cover permission-sensitive removal, path traversal, and write rejection. `testLocks` and `testListLocks` cover flock/plock acquisition, conflicts, range coalescing, concurrent blocking locks, list output, and backend lock-leak cleanup. `testConcurrentWrite` and `testConcurrentDir` run goroutine-heavy writes, mkdir/create/rename/unlink sequences, and lock-free directory races.

Data-lifecycle helpers cover slice and file state. `testCompaction` writes overlapping slices, appends many slices, invokes backend compaction, validates delayed deletion under trash, tests zero-length and sparse compaction, and verifies `CompactAll` plus `ListSlices`. `testTruncateAndDelete` checks directory truncate rejection, large truncation boundaries, sustained slice listing, and eventual deletion after unlink/close. `testCopyFileRange` builds sparse and non-sparse source/destination chunks and verifies exact resulting slice vectors.

Trash and clone paths are broad. `testTrash` verifies unlink/rmdir/rename-overwrite moves into trash, trash permission denial, name truncation for max-length names, `BatchUnlink`, skip-trash flags, recursive remove with and without trash, and cleanup of trash directories. `testClone` and `testBatchClone` verify recursive clone, hardlink/symlink/xattr/data preservation, statfs changes, mode preservation options, duplicate and invalid destination errors, immutable destination errors, detached-tree cleanup, delayed detached-node discovery, slice reference protection, and explicit rejection of cloning trash inodes.

Quota coverage is split between directory quotas and user/group quotas. `testQuota`, `testUserGroupQuota`, `testCheckQuotaFileOwner`, and the standalone `TestQuotaEdgeCases`/`TestCheckQuotaFileOwner` verify set/get/list/delete, nested directory quota accounting, quota loading/flushing, open/unlinked sustained files, quota attribution to file owner rather than operator, hardlink accounting differences between directory quotas and user/group quotas, batch unlink semantics under trash, symlink deletion accounting, concurrent quota operations, mixed quota types, zero/unlimited limits, and regression coverage for sustained inodes created before user/group quotas are enabled.

## State And Persistence Behavior

The suite is intentionally stateful. It uses persistent metadata constructs: format records, sessions, inode records, directory entries, xattrs, symlink targets, slice lists, delayed slice deletion queues, detached-node queues, quota records, ACL records/cache, lock records, trash namespace entries, token records, and directory-stat counters. Tests frequently call `NewSession`, `CloseSession`, `FlushSession`, `loadQuotas`, and `doFlushQuotas` because production behavior batches state changes. Some checks poll because directory statistics and quota state can be eventually flushed by session/background workers.

Backend persistence is validated both through public `Meta` APIs and through backend internals. `setAttr` corrupts inode nlink/full fields directly, then `Check` and repair paths must reconstruct expected state. `testClone` directly removes clone destination edges and expects detached cleanup to remove all backend keys/rows and eventually release slice references.

## Dependencies And Integration Points

The file depends on JuiceFS `meta` package types (`Meta`, `baseMeta`, `Attr`, `Entry`, `Slice`, `Quota`, `Format`, flags and constants), `aclAPI`, Redis client internals, xorm SQL sessions, `utils.MockProgress`, `testify/assert` and `require`, and Go `syscall`, `context`, `sync`, `runtime`, and time utilities. It integrates with backend constructors (`newRedisMeta`) and backend-specific methods/fields, so it is both a black-box `Meta` contract suite and a white-box regression suite for common engine internals.

## Risks And Maintenance Notes

The test is large, order-dependent, and mutates shared format/config state inside `testMeta`; failures can cascade if a helper leaves behind files, quotas, trash, sessions, or config flags. Many checks rely on sleeps and polling, so slow CI or backend latency can produce flakes. Direct backend mutation makes the suite valuable for repair validation but brittle against schema/key layout refactors. Several assertions encode current quota strategy, especially hardlink and trash behavior; those are high-risk when changing quota accounting. External Redis/KeyDB/cluster tests require services and are skipped only through environment or constructor failure paths.

## Test Signals

Passing this file signals that a metadata backend conforms to the package-wide filesystem contract across common and edge-case operations. Particularly strong regression signals include no lock leaks after `CloseSession`, no slice deletion before clone reference release, correct `EDQUOT` attribution to file owners, correct directory-stat deltas on rename/trash/batch operations, and successful repair after deliberately corrupted directory nlinks.
