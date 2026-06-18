# sources/distributed-fs/juicefs/pkg/meta/load_dump_test.go

## Purpose

`load_dump_test.go` is integration and regression coverage for legacy JSON metadata dumps and V2 protobuf metadata backups. It loads sample metadata into multiple engines, validates restored semantics, dumps back to canonical sample files, restores across engines, and checks secret/trash behavior.

## Important APIs And Helpers

`TestEscape` validates `escape`/`unescape` with UTF-8 and GBK byte sequences, spaces, `%`, quotes, and backslashes. `Utf8ToGbk` and `GbkToUtf8` support those byte-level cases.

`checkMeta` is the main semantic validator. It loads format settings, checks counters (`usedSpace`, `totalInodes`, `nextInode`, `nextChunk`, `nextSession`, `nextTrash`) with Redis-specific counter offsets, reads root entries, validates GBK/UTF-8 names, computes and compares directory stats, validates root dir quota usage, validates user/group quota limits, checks file attributes/flags/ACL IDs, decodes access/default ACL rules, reads file chunks, verifies hardlink parents, reads GBK symlink targets, and checks xattrs.

`testLoad`, `testDump`, `testLoadDump`, `testLoadSub`, `testDumpV2`, `testLoadDumpV2`, `testLoadOtherEngine`, and `testSecretAndTrash` compose engine-specific load/dump/restore scenarios.

## Control Flow And Persistence

Legacy tests reset a metadata engine, call `LoadMeta` with `metadata.sample`, validate state, dump with `DumpMeta` in fast and non-fast modes, and compare output with `diff`. Chroot/subdir behavior is tested by dumping `d1` as root and by loading a subdir sample into a fresh engine.

V2 tests dump with `DumpMetaV2`, load with `LoadMetaV2`, and verify same semantic state. They also load V2 dumps from one engine into another to exercise backend-neutral protobuf persistence. `testSecretAndTrash` verifies `DumpOption.KeepSecret`: encryption keys survive when true and become `"removed"` when false; it also scans trash files and checks inode/size expectations.

## Dependencies And Integration Points

The tests depend on live/available metadata engines depending on test selection: Redis, SQLite, Badger, TiKV, etcd, Postgres, and memkv. They use package-level `NewClient`, engine internals (`m.getBase().en`, `engine.doGetQuota`, `engine.doGetDirStat`), ACL APIs, sample dump files, and shell `diff`.

## Risks And Edge Cases

These tests can be environment-sensitive: Redis/TiKV/etcd/Postgres addresses must exist for some cases, while `SKIP_NON_CORE` only gates slow tests. Shelling out to `diff` assumes a Unix-like environment. The V2 cross-engine tests write dump files into the working directory (`sqlite-secret.dump`, engine dumps, `test.dump`), which can leave artifacts if tests abort. Counter expectations include Redis-specific off-by-one behavior, documenting backend divergence.

## Test Signals

This is the strongest regression signal for dump/load compatibility. It covers binary names, hardlinks, ACLs, xattrs, chunks, quotas, dir stats, trash, secret stripping, chroot dump, and cross-engine V2 portability.
