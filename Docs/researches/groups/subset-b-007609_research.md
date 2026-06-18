# subset-b-007609 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/base_test.go -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/base_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/benchmarks_test.go -->
# sources/distributed-fs/juicefs/pkg/meta/benchmarks_test.go

## Purpose

This file defines microbenchmarks for JuiceFS metadata operations and slice decoding. It measures common directory, file, xattr, link, and data paths across Redis, SQL/sqlite, and TKV/badger metadata engines. The benchmark suite is not correctness-comprehensive like `base_test.go`; instead it provides comparable performance signals for hot metadata APIs.

## Important APIs And Functions

`encodeSlices` and `encodeSlicesAsBuf` build fixed encoded slice records in two formats: a string slice consumed by `readSlices` and a contiguous byte buffer consumed by `readSliceBuf`. `BenchmarkReadSlices` and `BenchmarkReadSliceBuf` run small, mid, and large sizes to compare decoding costs.

`prepareParent` removes any previous benchmark directory and recreates it under root. The `bench*` helpers each isolate one operation: `benchMkdir`, `benchMvdir`, `benchRmdir`, `benchResolve`, `benchReaddir`, `benchMknod`, `benchCreate`, `benchRename`, `benchUnlink`, `benchLookup`, `benchGetAttr`, `benchSetAttr`, `benchAccess`, xattr operations, hardlink/symlink, `benchNewChunk`, `benchWrite`, and `benchRead`.

`benchmarkDir`, `benchmarkFile`, `benchmarkXattr`, `benchmarkLink`, and `benchmarkData` group those helpers into sub-benchmarks. `benchmarkAll` initializes a format with directory stats, creates a session, and runs all groups. `BenchmarkRedis`, `BenchmarkSQL`, and `BenchmarkTKV` instantiate the target engine URLs.

## Control Flow

Most benchmark helpers prepare a clean parent directory outside the timed section, create any prerequisite file or xattr while stopped or before `ResetTimer`, then loop `b.N` over the target metadata call. Delete-like benchmarks stop the timer while recreating an entry and measure only the remove operation. Rename benchmarks move one existing entry through incrementing names so each iteration remains valid. Read benchmarks prepopulate slices and repeatedly call `Read` into a reused slice variable.

`benchResolve` detects unsupported backend implementations with `ENOTSUP` and skips. `benchmarkData` registers no-op `DeleteSlice` and `CompactChunk` callbacks before exercising slice allocation/writes/reads so data-related background message hooks do not fail the benchmark.

## State And Persistence Behavior

Benchmarks create real metadata state in the target backend: directories, inodes, xattrs, hardlinks, symlinks, slices, and sessions. The Redis benchmark points at `redis://127.0.0.1/1`, while SQL and TKV use temporary sqlite/badger paths under `b.TempDir()`. Because `benchmarkAll` does not explicitly reset every backend at entry, benchmark directories are cleaned per helper through `prepareParent`, but backend-wide session or format state may persist during one benchmark invocation.

## Dependencies And Integration Points

The file depends on the `Meta` interface and common metadata constants (`RootInode` via literal `1`, `RmrDefaultThreads`, `ChunkSize`, `sliceBytes`), `utils.NewBuffer`, log setup through `utils.SetLogLevel`, and `logrus`. It integrates with `NewClient` and all registered backend URL schemes. The benchmark labels are stable sub-benchmark names useful for comparing engine changes.

## Risks And Test Signals

These benchmarks can be misleading if external Redis is unavailable, preloaded, or running with different persistence settings. Some helpers grow state proportional to `b.N`; long runs can create many entries/slices. The SQL and TKV benchmarks are more hermetic because they use temporary local stores. Performance regressions here point to hot metadata operations, but correctness must still be validated through the normal tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/benchmarks_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/config.go -->
# sources/distributed-fs/juicefs/pkg/meta/config.go

## Purpose

`config.go` defines client runtime metadata configuration and persistent volume format metadata for JuiceFS. It also implements compatibility checks, secret redaction, and encryption/decryption of sensitive format fields before storage or display.

## Important APIs And Types

`Config` is the in-memory client/mount configuration. Important fields include retry/delete limits, case-insensitive mode, read-only mode, background-job disablement, open-cache settings, heartbeat, mount/subdir identity, atime mode, directory-stat flush period, session id, directory sorting, fast statfs, and network-interface selection. `DefaultConf` sets conservative defaults: 10 retries, max 2 deletes, 12 second heartbeat, `NoAtime`, and 1 second dir-stat flushes. `SelfCheck` normalizes dangerous heartbeat values and warns when object deletion is disabled.

`Format` is persistent volume configuration loaded from metadata storage. It records volume identity, storage backend and credentials, object layout parameters, capacity/inode limits, encryption settings, bandwidth limits, trash retention, metadata version, client version constraints, directory stats, user/group quota, ACL enablement, Ranger settings, change log limits, and Kerberos config. `String` returns JSON with secrets redacted through `RemoveSecret`.

`Format.update` compares a new format with an existing one. Without `force`, it rejects changes to name, block size, compression, shards, hash prefix, and metadata version. UUID changes are special: when only UUID differs, the method decrypts the new secrets using the new UUID, sets the old UUID, and re-encrypts so secret ciphertext stays decryptable under the persisted UUID. With `force`, it allows overwrite and logs a warning.

`CheckVersion` and `CheckCliVersion` enforce metadata and client version compatibility using `pkg/version`. `newCipher`, `Encrypt`, and `Decrypt` implement AEAD encryption for `SecretKey`, `SessionToken`, and `EncryptKey`. `newCipher` uses SM4-GCM with an SM3 KDF for `object.SM4GCM`, and otherwise AES-GCM with an MD5-derived key from the UUID.

## Control Flow

Encryption is idempotent: `Encrypt` returns immediately if `KeyEncrypted` is already true or there are no secrets. Otherwise it creates a cipher from `EncryptAlgo` and `UUID`, generates a random nonce per field, seals the plaintext, prepends nonce to ciphertext, base64-encodes it, and marks `KeyEncrypted`. `Decrypt` is similarly guarded by `KeyEncrypted`; it base64-decodes each field, opens the AEAD with the nonce prefix, restores plaintext, and clears `KeyEncrypted`. If a secret has been redacted to `"removed"`, decryption returns an actionable error asking the user to correct it via config.

## State And Persistence Behavior

`Config` is process-local, but `Format` is serialized to metadata storage and therefore acts as a persistent volume contract. `RemoveSecret` intentionally destroys in-memory secret values for safe display; after redaction, `Decrypt` cannot recover them. `Encrypt` mutates the `Format` in place and uses random nonces, so ciphertext changes across encryptions even for the same plaintext.

## Dependencies And Integration Points

The file integrates with object encryption constants (`pkg/object`), JuiceFS semantic version helpers, package logging, Go crypto packages, JSON serialization, and third-party GM/T SM3/SM4 implementations. Other metadata files call these methods during `Init`, `Load`, config update, mount setup, and CLI display paths.

## Risks And Test Signals

The UUID is the encryption key source, so UUID-change handling is sensitive. Reordering `Decrypt`/UUID assignment/`Encrypt` in `update` can make stored credentials unrecoverable. AES uses MD5 as a key derivation shortcut, which is compatibility-sensitive rather than modern KDF design. `Decrypt` assumes decoded buffers are at least nonce-sized; malformed stored ciphertext could panic if not guarded elsewhere. Tests in `config_test.go` cover redaction, round trips across supported algorithms, and UUID key-conflict update behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/config_test.go -->
# sources/distributed-fs/juicefs/pkg/meta/config_test.go

## Purpose

This file tests the sensitive-field behavior of `Format`: encryption, redaction, decryption failure after redaction, supported encryption algorithms, and UUID conflict handling during format updates.

## Important Tests

`TestRemoveSecret` creates a format with `SecretKey`, `EncryptKey`, and `SessionToken`, encrypts it, calls `RemoveSecret`, and asserts all three fields become `"removed"`. It then verifies that `Decrypt` returns an error containing `"secret was removed"` instead of silently producing invalid values.

`TestEncrypt` iterates over `object.AES256GCM_RSA`, `object.CHACHA20_RSA`, and `object.SM4GCM`. For each algorithm label it encrypts a format and verifies secrets are no longer plaintext, then decrypts and verifies exact restoration. The first two algorithm constants use the default AES-GCM branch in `newCipher`; SM4 uses the SM4-GCM branch.

`TestFormat_Update_KeyConflict` builds an old format with UUID A and a new format with UUID B plus a secret. It encrypts the new format, calls `update(old, false)`, and asserts the new format adopts UUID A while remaining encrypted. A final decrypt must recover the original secret, proving `update` rekeys encrypted secrets correctly when UUID is the only conflict.

## State And Persistence Behavior

All tests mutate `Format` structs in memory but model persistent metadata transitions. The UUID conflict test is especially important because persisted format updates happen around encrypted credentials; losing the old UUID/key relationship would break future mounts. Redaction is treated as irreversible for encrypted fields.

## Dependencies And Integration Points

The tests import `pkg/object` for encryption algorithm constants and `testify/assert` for key-conflict assertions. They directly cover `Format.Encrypt`, `Format.Decrypt`, `Format.RemoveSecret`, and the unexported `Format.update`.

## Risks And Test Signals

These tests give strong signals for happy-path encryption and UUID rekeying but do not cover malformed base64, truncated ciphertext, empty UUIDs, or `CheckCliVersion`. They also do not verify randomness/non-determinism of nonces. A failure here usually indicates a compatibility risk for stored credentials or CLI-safe format display.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/context.go -->
# sources/distributed-fs/juicefs/pkg/meta/context.go

## Purpose

`context.go` defines the metadata package's request context abstraction. It extends Go's `context.Context` with filesystem identity (`uid`, `gid`, supplementary gids, pid), package-specific cancellation helpers, immutable `WithValue` chaining, and a permission-check hook.

## Important APIs And Types

`CtxKey` is a string alias for package context keys. `Context` embeds `context.Context` and adds `Gid`, `Gids`, `Uid`, `Pid`, `WithValue`, `Cancel`, `Canceled`, and `CheckPermission`.

`wrapContext` is the default implementation. It stores an embedded context, cancel function, pid, uid, and gids. `Uid`, `Gid`, `Gids`, and `Pid` expose identity. `Cancel` invokes the stored cancel function when present. `Canceled` returns whether the embedded context has an error. `WithValue` shallow-copies the wrapper, replaces the embedded context with `context.WithValue`, and preserves identity/cancel state. `CheckPermission` currently returns true.

Constructor helpers are `Background`, `NewContext`, `WrapContext`, `WrapWithCancel`, `WrapWithTimeout`, and `WrapWithoutCancel`. `containsGid` checks whether a gid is in the supplementary group list.

## Control Flow

`Background` wraps `context.Background()` as root uid/gid/pid zero. `NewContext` creates a cancelable context with explicit process and user/group identity. `WrapWithCancel` always derives a new cancelable child context from the provided context. `WrapWithTimeout` derives a timed child and copies pid/uid/gids from an existing metadata context. `WrapWithoutCancel` preserves an existing context without installing a cancel function, so calling `Cancel` is a no-op for that wrapper.

## State And Persistence Behavior

The file has no persistent storage. It carries request-local state used by all metadata operations for permission checks, quota attribution, lock ownership context, and cancellation. The `gids` slice is assumed immutable enough for shallow copying; callers that mutate the slice after passing it in could affect existing contexts.

## Dependencies And Integration Points

The only external dependencies are Go `context` and `time`. The interface is used throughout the metadata engines, tests, quota logic, ACL/mode access checks, cleanup tasks, and cancellation-sensitive long operations. `context_cancellation_test.go` specifically validates cancellation behavior through metadata APIs.

## Risks And Test Signals

`Gid` indexes `gids[0]` with no empty-slice guard, so constructors must receive at least one gid. `Canceled` treats deadline exceeded and explicit cancel the same because both set `Err`. `WithValue` preserving the original cancel function is convenient, but canceling either wrapper cancels the shared underlying context. Tests focus on cancellation propagation at higher metadata layers rather than direct unit coverage of this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/context.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/context_cancellation_test.go -->
# sources/distributed-fs/juicefs/pkg/meta/context_cancellation_test.go

## Purpose

This file is a focused regression suite for metadata context cancellation. It verifies that long-running or transactional metadata paths notice canceled `Context` values and return interruption/cancellation errors instead of continuing work indefinitely.

## Important Tests And Helpers

`createSummaryTestTree` builds a configurable tree of directories and files under a parent inode using `Mkdir` and `Create`. It is used to make tree-summary traversal large enough to invoke progress callbacks repeatedly.

`TestGetTreeSummaryCanceledByProgressCallback` creates an in-memory KV metadata engine, initializes it, populates 50 directories with 20 files each, and calls `GetTreeSummary` with a progress callback. After ten progress updates the callback cancels the context; the expected result is `syscall.EINTR`.

`TestKVTxnReturnsEINTRWhenContextAlreadyCanceled` creates a `memkv` engine, cancels a context before calling `kvMeta.txn`, and expects `syscall.EINTR` without running useful transaction work. `TestBadgerKVTxnReturnsEINTRWhenContextAlreadyCanceled` repeats the same signal against a badger-backed TKV URL in a temp directory.

`TestCleanupTrashBeforeReturnsEINTRWhenContextAlreadyCanceled` initializes a KV engine and calls `CleanupTrashBefore` with an already-canceled context. It accepts `EINTR` or `0` because an empty-trash fast path may complete before observing cancellation.

`TestCleanupDelayedSlicesReturnsCanceledWhenContextCanceled` injects 128 delayed-slice keys through a transaction, cancels the context, then calls `doCleanupDelayedSlices`; the expected Go error wraps or equals `context.Canceled`.

`TestRemoveEmptyDirReturnsEINTRWhenCanceled` creates an empty directory, cancels a context, and verifies recursive `Remove` returns `EINTR`.

## Control Flow

Each test constructs an isolated metadata engine, resets it, initializes the standard test format, creates only the state needed for that cancellation path, then cancels a `NewContext` before or during the target operation. Assertions use either syscall errno values (`EINTR`) for public metadata APIs or `errors.Is(err, context.Canceled)` for lower-level cleanup internals.

## State And Persistence Behavior

The tests use volatile `memkv` stores for most cases and a temporary badger store for the TKV transaction case. They persist enough metadata state to exercise traversal, trash cleanup, delayed-slice cleanup, and remove logic, but all stores are test-local. The delayed-slice test writes raw delayed slice keys with `km.delSliceKey`, so it is coupled to KV persistence layout.

## Dependencies And Integration Points

The file depends on `newKVMeta`, `NewClient`, `kvMeta`, `kvTxn`, `TreeSummary`, `RootInode`, `testConfig`, `testFormat`, and public `Meta` operations. It integrates with Go `context`, `errors`, `filepath`, `syscall`, and `time`. It provides direct regression coverage for cancellation checks in KV transactions, cleanup workers, tree traversal, and recursive removal.

## Risks And Test Signals

These tests are strongest for KV-family engines; Redis and SQL cancellation behavior is not directly exercised here. Some paths accept fast-path success when there is no work, so they signal responsiveness without requiring every empty operation to fail. Failures indicate operations may ignore cancellation and block unmounts, CLI interrupts, or maintenance jobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/context_cancellation_test.go -->
