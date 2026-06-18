# sources/distributed-fs/ceph/src/rgw/rgw-gap-list-comparator

## Purpose
Awk helper that intersects two sorted `rgw-gap-list` result files. It is intended to reduce false positives by retaining only candidate gap lines that appear in two independent runs.

## Important APIs, Types, and Functions
- Accepts `-v filetwo=<second sorted file>` and `-v matchout=<output file>`.
- `advance_f2()` reads the next line from the second file.
- `test_lines()` compares the current primary input line with `f2line`, emits matches, and guides advancement.
- `status_out()` reports scan progress to stderr every 100k lines.

## Control Flow
On `BEGIN`, the script validates required variables, initializes counters, opens the second file, and prints a progress header. For each line of the first file, it advances through `filetwo` until the second line is at or beyond the first, then writes exact string matches to `matchout`. It exits early when the second file reaches EOF.

## State and Persistence
Only local awk counters and the current second-file line are kept in memory. Durable output is appended to `matchout`; callers are advised to remove old output before running.

## Dependencies and Integration Points
Designed to consume sorted text outputs from `rgw-gap-list`. It depends on awk string comparison using the same collation as the sorted files, so operators must use `LC_ALL=C` consistently.

## Risks and Edge Cases
Input files must be sorted identically or matches may be missed. Because output is append-only, stale results remain if `matchout` is not removed first. It does exact line matching, so harmless formatting changes in upstream output prevent correlation.

## Test Signals
Use fixture pairs with exact matches, non-overlapping data, duplicate lines, unsorted inputs, and EOF on either file. Verify progress counters do not affect stdout/stderr contracts.
