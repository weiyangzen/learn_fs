# sources/distributed-fs/ceph-client/drivers/md/dm-ps-round-robin.c

## Purpose
Implements the classic `round-robin` multipath path selector. It cycles through currently valid paths in list order, moving the selected path to the tail after each selection.

## Important APIs, Types, And Functions
`struct selector` contains valid and invalid path lists protected by a spinlock. `struct path_info` stores the `dm_path` and repeat count. The selector callbacks are `rr_create()`, `rr_destroy()`, `rr_add_path()`, `rr_fail_path()`, `rr_reinstate_path()`, `rr_select_path()`, and `rr_status()`. The module registers `rr_ps` as `round-robin`, version `1.2.0`.

## Control Flow
Path addition accepts at most one repeat-count argument, warns that values above one are deprecated, and appends the path to the valid list. Selection takes the first valid path, moves it to the end of the valid list, and returns it. Failure moves a path to the invalid list; reinstatement moves it back to the valid list.

## State And Persistence
State is limited to volatile path lists and configured repeat counts. There are no in-flight counters, timing metrics, or persistent records.

## Dependencies And Integration Points
The file depends on the DM path-selector API and Linux module infrastructure. It is loaded by DM multipath when a table references `round-robin`; the multipath core owns path-group policy, I/O submission, and failure notification.

## Risks
Round-robin ignores path speed, queue depth, CPU locality, and request size, so it can perform poorly on asymmetric hardware. The deprecated repeat-count field remains visible in status but is clamped to one for values above one. List operations require correct failure/reinstate sequencing from multipath core.

## Test Signals
Test path cycling order, empty-valid-list behavior, fail/reinstate transitions, argument parsing, and table status round-trip. Under equal healthy paths, selected path sequence should rotate deterministically.
