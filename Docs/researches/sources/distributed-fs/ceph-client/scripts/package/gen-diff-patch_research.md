<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/package/gen-diff-patch -->
# sources/distributed-fs/ceph-client/scripts/package/gen-diff-patch

## Purpose

`gen-diff-patch` writes `git diff HEAD` to a requested patch file for Debian source package generation, then warns if untracked files might make the source package incomplete.

## Important APIs, Types, and Functions

It accepts an output patch path, creates its parent directory, and runs `git -C "${srctree:-.}" diff HEAD`.

## Control Flow

The script writes local tracked differences into the requested patch file. If the patch is empty, or if there are no untracked files, it exits quietly. If both tracked diffs and untracked files are present, it prints a multi-line warning. `mkdebian` later prepends subject/author metadata and adds the patch to `debian/patches/series` only if it is non-empty.

## State and Persistence Behavior

It persists the generated patch file and does not modify source files.

## Dependencies and Integration Points

It depends on shell and git. It integrates with `mkdebian --need-source` and Debian `3.0 (quilt)` source packages.

## Risks and Edge Cases

Only tracked diffs are captured; needed untracked files are not included and only trigger a warning. Uncommitted local changes become part of source packaging, so reproducibility depends on a clean or intentionally staged tree. Binary changes may not serialize usefully.

## Test Signals

Run with a clean tree, a modified tracked source file, tracked plus untracked files, and binary diffs. Verify warning behavior, non-empty behavior, and quilt applicability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/package/gen-diff-patch -->
