# sources/distributed-fs/juicefs/pkg/meta/quota.go

## Purpose

`quota.go` implements directory stats, filesystem capacity checks, directory quotas, user quotas, group quotas, quota flushing, quota scans/repair, and Prometheus quota metrics for JuiceFS metadata. It is the central enforcement and reconciliation layer between in-memory quota counters and engine-persisted quota records.

## Important APIs, Types, And Functions

`dirStat` tracks directory `length`, `space`, and `inodes`. Quota types are `DirQuotaType`, `UserQuotaType`, `GroupQuotaType`, and `AllQuotaType`. `Quota` stores limits, persisted usage, and pending deltas (`newSpace`, `newInodes`). `Quota.check`, `update`, `snap`, and `sanitize` perform atomic limit checks and counter movement.

Directory stat paths include `calcDirStat`, `GetDirStat`, `updateDirStat`, `updateParentStat`, `flushDirStat`, and `doFlushDirStat`. Volume stats use `flushStats`, `doFlushStats`, and `syncVolumeStat`.

Quota enforcement uses `checkQuota`, `checkDirQuota`, `checkUserQuota`, `checkGroupQuota`, `updateDirQuota`, and `updateUserGroupStat`. Loading/flushing uses `loadQuotas`, `syncQuotaMaps`, `collectQuotas`, `updateQuota`, `flushQuotas`, and `doFlushQuotas`.

CLI/API quota handling is routed by `HandleQuota` into `handleQuotaSet`, `handleQuotaGet`, `handleQuotaList`, and `handleQuotaCheck`. Repair/reconciliation helpers include `calcDirQuotaUsage`, `ScanUserGroupUsage`, `scanGlobalUserGroupUsage`, `checkDirUsage`, `compareUGUsage`, `repairUsage`, `repairUgUsage`, and `checkUGUsage`. Metrics are maintained by `updateQuotaMetrics`, type-specific update helpers, and `cleanupQuotaMetrics`.

## Control Flow And Persistence

Quota enforcement first checks user and group quotas, then global capacity/inode limits, then ancestor directory quotas when `Format.DirStats` is enabled. Positive `space`/`inodes` deltas are rejected with `EDQUOT` for quota limits or `ENOSPC` for global volume limits. Updates are staged in `newSpace/newInodes` atomics and flushed asynchronously. `doFlushQuotas` snapshots pending deltas, persists them through `m.en.doFlushQuotas`, then moves deltas into `UsedSpace/UsedInodes` only after successful persistence.

Setting a directory quota enables `DirStats` in the format if needed, persists limits with unknown usage (`-1`), and if newly created, computes recursive usage through `GetSummary`. Setting user/group quota may enable `UserGroupQuota` and trigger a global usage scan. Scans walk root and optional trash, count directory/file ownership, de-duplicate hardlinked files, and include sustained inodes. Repair can clean and rewrite user/group usage records.

## Dependencies And Integration Points

This file is tightly coupled to `baseMeta`, engine methods (`doLoadQuotas`, `doSetQuota`, `doGetQuota`, `doFlushQuotas`, `doUpdateDirStat`, `doReaddir`, `doScanSustainedInodes`, `cleanUgUsage`, etc.), `Format` flags, path resolution, summaries, parent caches, metrics collectors, and human-readable logging via `go-humanize`.

## Risks And Edge Cases

Quota checks use pending deltas plus persisted usage, so failed flushes can keep enforcement conservative until persistence succeeds. `syncQuotaMaps` deletes missing directory quotas but intentionally does not delete missing user/group quotas, because user/group maps may contain usage-only records. Global user/group scans are expensive and can be affected by concurrent mutations. The scan counts directories as inodes and files by aligned length, but ignores non-file/non-directory sizes except sustained files. Trash inclusion depends on `TrashDays` and existence of `TrashInode`. Metrics cleanup must delete label values for removed/unlimited quotas to avoid stale series.

## Test Signals

`load_dump_test.go` validates restored dir/user/group quotas from sample metadata. `random_test.go` checks `StatFS` against a model and exercises operations that update quota-relevant stats. Dedicated quota tests are not in this subset, so scan/repair behavior relies on broader integration coverage.
