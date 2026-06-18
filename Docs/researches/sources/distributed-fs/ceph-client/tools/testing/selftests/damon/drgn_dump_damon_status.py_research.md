# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/drgn_dump_damon_status.py

## Purpose

`drgn_dump_damon_status.py` is a drgn script that reads live kernel DAMON structures for a kdamond pid and dumps selected fields as JSON for tests to compare against sysfs-staged configurations.

## Important APIs, Types, and Functions

It uses drgn helpers `find_task()`, `cast()`, `list_for_each_entry()`, and object field conversion helpers. Converters include `attrs_to_dict()`, `target_to_dict()`, `damos_access_pattern_to_dict()`, `damos_quota_to_dict()`, `damos_watermarks_to_dict()`, `damos_filter_to_dict()`, `scheme_to_dict()`, and `damon_ctx_to_dict()`.

## Control Flow

The script obtains a drgn program, parses `<kdamond pid> <file>`, reads `find_task(prog, pid).worker_private` as `struct kthread`, casts its `data` to `struct damon_ctx *`, converts one context to nested dictionaries/lists, and writes JSON to stdout or the requested file.

## State and Persistence Behavior

It does not mutate kernel state. It reads live kernel memory and persists a JSON snapshot if a filename is supplied.

## Dependencies and Integration Points

It depends on drgn, kernel debug type information sufficient for DAMON structs, Linux helper APIs, and stable internal DAMON struct field names. `sysfs.py` and `sysfs_no_op_commit_break.py` call it.

## Risks and Edge Cases

It is tightly coupled to internal kernel structs, including `worker_private` layout and DAMON field names. A typo checks `hugeapge_size` rather than `hugepage_size`, limiting that filter dump path. Missing drgn or debug symbols causes callers to fail or skip depending on wrapper logic.

## Test Signals

JSON output is compared against expected sysfs settings. Mismatches identify failed commit, wrong enum mapping, lost filters, quotas, attrs, targets, or schemes.
