# File Research: sources/block-storage/linux-dm/drivers/md/dm-ps-queue-length.c

## Purpose

`dm-ps-queue-length.c` implements the `queue-length` multipath selector. It chooses the currently valid path with the fewest in-flight I/Os.

## State And Arguments

The selector maintains `valid_paths` and `failed_paths` under a spinlock. Each path stores a `dm_path`, repeat count, and atomic `qlen` in-flight I/O count. Path arguments are optional `[<repeat_count>]`; values greater than 1 are deprecated and coerced to 1.

## Selection And Accounting

`ql_select_path()` scans valid paths for the smallest `qlen`, stops early when it finds a zero-load path, moves the selected path to the tail for even balancing, and returns its `dm_path`. `ql_start_io()` increments the selected path’s `qlen`; `ql_end_io()` decrements it.

## Failure And Status

Failure moves a path to `failed_paths`; reinstatement moves it back to the valid list tail. Selector-level status emits `0`. Per-path info status reports current queue length, and table status reports repeat count. The selector registers as `queue-length` with one table arg and one info arg.

## Invariants And Risks

- `start_io()` and `end_io()` must remain balanced or `qlen` will bias future selection.
- List membership changes are locked; per-path load uses atomics for low-cost I/O updates.
- Reinstated paths retain their queue-length counter.
- Repeat count is kept only for compatibility and coerced to one.

## Test Focus

Test path argument parsing, repeat-count deprecation, least-queue selection, tie balancing via list rotation, start/end balance on success and error completions, fail/reinstate list movement, empty valid list returning `NULL`, and status output.
