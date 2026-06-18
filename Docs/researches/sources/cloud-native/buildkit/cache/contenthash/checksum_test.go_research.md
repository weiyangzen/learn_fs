# sources/cloud-native/buildkit/cache/contenthash/checksum_test.go

Purpose: comprehensive behavioral tests for contenthash cache correctness, especially symlink resolution, scan minimization, filters, hardlinks, directory invalidation, and persistence.

Important APIs/types/functions: tests include `TestChecksumSymlinkNoParentScan`, `TestNeedScanChecksumRegression`, `TestChecksumNonLexicalSymlinks`, `TestChecksumHardlinks`, `TestChecksumWildcardOrFilter`, `TestSymlinksNoFollow`, `TestChecksumBasicFile`, include/exclude tests, symlink-path tests, `TestPersistence`, `TestChecksumUpdateDirectory`, and `TestChecksumIdenticalWithNoopExclude`. Helpers include `createRef`, `setupCacheManager`, `badMountable`, `changeStream`, `parseChange`, `emit`, `withHash`, and `writeChanges`.

Control flow: tests create native snapshotter-backed cache managers, synthesize filesystem trees either by writing actual files into mutable refs or by emitting fsutil change streams, then compare computed digests against fixed expected values. Several tests inspect `needsScan` and `scanCounter` to assert lazy scan behavior, not just digest equality.

State and persistence behavior: tests exercise ref creation/commit/release, metadata DB reopen, LRU purge, async contenthash save, and `HandleChange` transaction updates. Hardlink and directory replacement scenarios validate invalidation of cached records.

Dependencies and integration points: uses containerd metadata/content/snapshotter primitives, BuildKit cache manager, snapshot local mounter, winlayers wrappers, bbolt, fsutil stats, and testify. Windows has skips where bind-mount support is unavailable.

Risks: many expected digests are golden values; intentional hashing changes require careful updates. Tests rely on timing (`100ms`) for async persistence. Some behavior is OS-sensitive, especially symlink and mount behavior.

Test signals: this is the primary safety net for `checksum.go`, `filehash.go`, `path.go`, and proto persistence. It explicitly covers historical regression issue 5042 around repeated scans.
