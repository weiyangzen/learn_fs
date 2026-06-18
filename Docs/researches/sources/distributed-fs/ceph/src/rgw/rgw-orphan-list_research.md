# sources/distributed-fs/ceph/src/rgw/rgw-orphan-list

## Purpose
Experimental Bash diagnostic script that finds possible orphaned RGW data objects by comparing `rados ls --all` output from data pools against `radosgw-admin bucket radoslist`. It warns that indexless buckets appear entirely orphaned.

## Important APIs, Types, and Functions
- `prompt_pool()` interactively selects one or more RGW data pools.
- `rados_ls()` scans pools with `rados ls --all`, separates namespace/locator entries into an issues file, extracts plain object ids, and sorts them.
- `radosgw_radoslist()` generates and sorts the RGW-admin view.
- Final comparison uses `ceph-diff-sorted "$rados_out" "$rgwadmin_out" | grep "^<"` to capture objects present in RADOS but absent from RGW-admin listing.

## Control Flow
The script validates arguments and pools, produces both sorted listings, warns on empty intermediate files, computes the delta, calculates candidate count and percentage, and prints locations of outputs and issue files.

## State and Persistence
Timestamped intermediates, error files, issue files, and `orphan-list-*.out` are written in the current directory. Temporary sorting files are created under `/tmp` or an optional temp directory.

## Dependencies and Integration Points
Requires Ceph client tools, `radosgw-admin`, `ceph-diff-sorted`, standard Unix text tools, and `CEPH_CONF` when configuration is not in the default path. It relies on the ceph-radosgw package for `ceph-diff-tool`/`ceph-diff-sorted`.

## Risks and Edge Cases
Indexless buckets invalidate results. Namespaces or locators are excluded from normal orphan detection and require manual review. Live cluster mutations can produce false positives. Empty inputs only warn rather than always fail, so operator judgment is required.

## Test Signals
Synthetic fixture tests should cover namespace/locator filtering, delta computation, empty-input warning behavior, missing pool detection, and `ceph-diff-sorted` error propagation through `PIPESTATUS`.
