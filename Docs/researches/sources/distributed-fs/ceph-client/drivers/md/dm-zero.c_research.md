# sources/distributed-fs/ceph-client/drivers/md/dm-zero.c

## Purpose
`dm-zero.c` implements the simple `zero` device-mapper target. It behaves like a virtual block device that returns zeroes for reads and silently drops writes and discards.

## Important APIs, Types, and Functions
The implementation consists of `zero_ctr()`, `zero_map()`, `zero_io_hints()`, and the `zero_target` registration. `zero_ctr()` accepts no target arguments and enables discard support. `zero_map()` handles reads, writes, and discards. `zero_io_hints()` advertises broad discard capability.

## Control Flow
Target construction fails if any arguments are supplied. On mapped reads, readahead is killed because populating cache with zero pages is wasteful; non-readahead reads are satisfied by `zero_fill_bio()` and completed immediately. Writes and discards are accepted and completed without forwarding. Unknown operations are killed.

## State and Persistence Behavior
The target has no private state and no persistence. All accepted I/O is completed synchronously without issuing lower-level requests. Writes and discards have no lasting effect.

## Dependencies and Integration Points
The file uses device-mapper target registration, Linux bio helpers, and module metadata. It registers as `zero`, version 1.2.0, with `DM_TARGET_NOWAIT`, constructor, map, and I/O hints hooks.

## Risks and Test Signals
Risk is low, but behavior must remain exact because upper layers may use this target for tests or sparse mappings. Tests should cover argument rejection, read zero-fill, readahead kill, write/drop completion, discard/drop completion, unknown operation kill, and queue-limit discard hints.
