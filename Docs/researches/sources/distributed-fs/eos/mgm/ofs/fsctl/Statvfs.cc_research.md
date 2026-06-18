<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Statvfs.cc -->
# sources/distributed-fs/eos/mgm/ofs/fsctl/Statvfs.cc

Source read size: 138 lines, 4974 bytes.

## Purpose

Implements the FUSE statvfs fsctl endpoint. It returns space-wide or quota-specific availability and capacity counters for a requested EOS space/path.

## Important APIs, Types, and Functions

The function reads `path` from the env, optionally URL-decodes it, uses `FsView::gFsView.mSpaceView["default"]` aggregate statfs counters for shallow/default requests, or calls `Quota::GetIndividualQuota` for deeper quota paths. It returns `f_avail_bytes`, `f_avail_files`, `f_max_bytes`, and `f_max_files`.

## Control Flow

After read access, stall, redirect, and stats, the handler decodes the requested space/path and counts slash depth. Unless `EOS_MGM_STATVFS_ONLY_QUOTA` is set, shallow paths or `EOS_MGM_STATVFS_ONLY_SPACE` use a static cached default-space aggregate guarded by `statvfsmutex`; the cache refreshes after a randomized 5-15 second interval. Other paths call the quota subsystem. Empty path returns `EINVAL`.

## State and Persistence Behavior

The file owns static process-local cache state for statvfs counters and last refresh time. It does not persist to disk.

## Dependencies and Integration Points

Integrates FUSE statvfs with `FsView`, space statfs counters, quota lookup, random cache jitter, env-controlled behavior, and XRootD response formatting.

## Risks and Edge Cases

Only the `default` space is used for aggregate statfs, regardless of the decoded path. Environment variables change semantics globally. Cached values can be stale for up to the randomized interval. Slash-depth heuristic determines whether quota is consulted.

## Test Signals

Test empty path, encoded path, shallow aggregate path, deep quota path, env overrides, missing default space, cache refresh timing, and quota values for users with and without limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Statvfs.cc -->
