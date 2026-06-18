# sources/distributed-fs/ceph/src/rgw/rgw-gap-list

## Purpose
Bash diagnostic script that finds possible RGW bucket data gaps by comparing objects known to bucket indexes (`radosgw-admin bucket radoslist`) against actual objects present in one or more data pools (`rados ls`). It is explicitly experimental and designed to produce candidates requiring verification.

## Important APIs, Types, and Functions
- `prompt_pool()` lists pools and asks the operator which data pools to scan.
- `radosgw_radoslist()` runs `radosgw-admin bucket radoslist --rgw-obj-fs="$fs"`, sorts uniquely by RADOS object id, and writes intermediate files.
- `rados_ls()` scans supplied pools with `rados ls`, sorts unique object ids, and records failures through flag files.
- Embedded awk script performs a single-pass sorted comparison and emits unique `Bucket: ... Object: ...` candidate lines.

## Control Flow
The script parses `-m`, `-p`, and `-t`, validates pools with `rados lspools`, runs the RADOS and RGW listings either sequentially or in parallel, checks non-empty intermediates, writes an awk comparator to a temp file, runs it over sorted data, sorts the candidate output, and reports counts and file locations.

## State and Persistence
It writes timestamped intermediates and errors under the current working directory: `rados-*.intermediate`, `radosgw-admin-*.intermediate`, `*.error`, and `gap-list-*.gap`. Temporary files, flag files, and the generated awk script live under `temp_prefix`.

## Dependencies and Integration Points
Requires `bash`, `rados`, `radosgw-admin`, `sort`, `awk`, `grep`, `wc`, and Ceph environment variables such as `CEPH_ARGS`. It relies on `LC_ALL=C` for reproducible sorting and on `--rgw-obj-fs` using byte `0xFE` as a field separator.

## Risks and Edge Cases
The tool is prone to false positives if objects are created or deleted during listing, especially in multithread mode. It assumes the field separator cannot appear in normal output. It skips RADOS names containing NUL. Failures terminate via `TERM` to the top-level process, which can be brittle with background jobs.

## Test Signals
Tests can use synthetic sorted inputs for the embedded awk comparator, missing pool validation, multithread flag-file handling, empty intermediate rejection, duplicate bucket/object suppression, and output stability under `LC_ALL=C`.
