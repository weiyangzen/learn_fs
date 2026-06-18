# sources/distributed-fs/ceph-client/tools/testing/kunit/kunit_json.py

## Purpose

This module converts parsed KUnit `Test` trees into JSON shaped for KernelCI-style test reporting. It is used when `kunit.py` receives `--json` during run, exec, or parse commands.

## Important APIs, Types, And Data

`Metadata` is a dataclass carrying `arch`, `def_config`, and `build_dir`. `JsonObj` aliases `Dict[str, Any]`. `_status_map` maps parser statuses `SUCCESS`, `SKIPPED`, and `TEST_CRASHED` to `PASS`, `SKIP`, and `ERROR`; any other status becomes `FAIL`. `_get_group_json()` recursively converts a `Test` node into a group with `name`, `sub_groups`, `test_cases`, and `misc` count data. `get_json_result()` injects common metadata fields and returns pretty-printed JSON.

## Control Flow

`get_json_result()` builds common fields from metadata, calls `_get_group_json()` on the parsed root test, renames the top group to `KUnit Test Group`, and serializes with `json.dumps(indent=4)`. `_get_group_json()` partitions child tests into nested groups when a child has subtests, or leaf test cases otherwise, and appends aggregate counts from the parser's `TestCounts`.

## State And Persistence Behavior

The module has no persistent state. It returns a JSON string; `kunit.py` decides whether to print it or write it to a file. Several common metadata fields are intentionally set to `None` or fixed values such as `git_branch: kselftest`.

## Dependencies And Integration Points

It depends on `kunit_parser.Test` and `TestStatus`, standard `json`, dataclasses, and typing. It integrates with `kunit.py parse_tests()` and downstream systems expecting KernelCI-like fields such as `arch`, `defconfig`, `build_environment`, `sub_groups`, `test_cases`, and status strings.

## Risks And Edge Cases

Status mapping defaults all unrecognized statuses to `FAIL`, so `NO_TESTS` and parser failures collapse into failure rather than a more specific category. The top-level name is overwritten, which discards the parser's internal root name. Metadata is sparse and may not satisfy all KernelCI consumers without enrichment. Deeply nested or malformed `Test` trees are serialized recursively without cycle protection.

## Test Signals

Tests should verify pass/fail/skip/crash status mapping, nested group conversion, count fields, top-level naming, and file/stdout behavior through `kunit.py --json`. JSON validation with `json.loads()` and expected keys is sufficient for this module.
