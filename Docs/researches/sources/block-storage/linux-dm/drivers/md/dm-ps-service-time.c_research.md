# File Research: sources/block-storage/linux-dm/drivers/md/dm-ps-service-time.c

## Purpose

`dm-ps-service-time.c` implements the `service-time` multipath selector. It estimates the best path by comparing current in-flight byte load adjusted by each path’s relative throughput.

## State And Arguments

The selector keeps valid and failed path lists under a spinlock. Each path stores `dm_path`, repeat count, relative throughput, and atomic in-flight byte count. Path arguments are `[<repeat_count> [<relative_throughput>]]`; repeat counts greater than 1 are deprecated and forced to 1. Relative throughput defaults to 1 and must be between 0 and 100. A throughput of 0 means the path is avoided while any positive-throughput path is available.

## Selection And Accounting

`st_select_path()` scans valid paths and chooses the path with the lowest estimated service time. `st_compare_load()` compares `(in_flight_size + incoming) / relative_throughput` without division by cross-multiplying, with overflow avoidance for very large in-flight sizes. Equal estimates prefer higher throughput. The selected path is moved to the tail for balancing.

`st_start_io()` atomically adds request size to the path’s in-flight byte count; `st_end_io()` subtracts it.

## Failure And Status

Failure moves a path to `failed_paths`; reinstatement moves it back to the valid tail. Selector-level status emits `0`. Per-path info reports in-flight byte count and relative throughput; table status reports repeat count and relative throughput. The selector registers as `service-time` with two table args and two info args.

## Invariants And Risks

- Byte-count accounting depends on balanced `start_io()`/`end_io()` calls.
- Cross-multiplication depends on overflow guard shifting when in-flight size is large.
- Relative throughput zero is valid but deprioritized.
- Reinstated paths retain their in-flight byte counter and throughput.
- `atomic_t` stores byte counts, so very large or long-lived accounting should be checked against platform integer width.

## Test Focus

Test argument bounds, throughput-zero behavior, equal-throughput least-load behavior, higher-throughput tie breaking, overflow guard paths, list rotation, start/end byte accounting, fail/reinstate movement, empty valid list behavior, and table/info status.
