# File Research: sources/block-storage/linux-dm/drivers/md/dm-ps-round-robin.c

## Purpose

`dm-ps-round-robin.c` implements the `round-robin` multipath selector. It distributes I/O by rotating through valid paths.

## State And Arguments

The selector owns `valid_paths` and `invalid_paths` lists protected by a spinlock. Each path has a `path_info` containing its `dm_path` and repeat count. Path arguments are optional `[<repeat_count>]`; repeat counts greater than 1 are deprecated and forced to 1.

## Selection And Failure Handling

`rr_select_path()` returns the first valid path and moves it to the tail, producing round-robin rotation. If no valid path exists, it returns `NULL`. `rr_fail_path()` moves the path to `invalid_paths`; `rr_reinstate_path()` moves it back to `valid_paths`.

## Status And Registration

Selector-level status emits `0`. Per-path table status emits repeat count; info status emits no per-path data. The module registers `round-robin` with one table arg and zero info args.

## Invariants And Risks

- The valid list order is the scheduling state.
- Fail/reinstate must move the selector’s existing `path_info`, not allocate a replacement.
- Repeat count is compatibility-only in this implementation.
- Empty valid lists are expected and signal no selector-available path to `dm-mpath`.

## Test Focus

Test optional repeat-count parsing, deprecated repeat coercion, rotation order, fail/reinstate ordering, empty valid list behavior, destroy freeing both lists, and table/info status formatting.
