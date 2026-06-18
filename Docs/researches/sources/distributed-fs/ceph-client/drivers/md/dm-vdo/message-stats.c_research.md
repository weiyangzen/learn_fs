# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/message-stats.c

## Purpose
`message-stats.c` serializes VDO runtime statistics and configuration into a textual, brace-delimited message format used by device-mapper status/config reporting paths.

## Important APIs, Types, and Functions
Public functions are `vdo_write_stats()` and `vdo_write_config()`. Small writer helpers serialize `u64`, `u32`, `u8`, booleans, strings, and block counts while advancing `buf` and reducing `maxlen`. Structured writers cover block allocator, commit, recovery journal, packer, slab journal, slab summary, ref counts, block map, hash lock, errors, bio stats, memory usage, index stats, full VDO stats, index memory, and index config.

## Control Flow
`vdo_write_stats()` allocates a temporary `struct vdo_statistics`, fetches a snapshot with `vdo_fetch_statistics()`, writes all fields through nested writer helpers, and frees the snapshot. `vdo_write_config()` writes version, physical/logical sizes, slab size, and index config directly from `vdo->states.vdo.config` and geometry. All helpers append with `scnprintf()` and update the caller's remaining buffer length.

## State and Persistence Behavior
The file does not own persistent state. It observes current statistics snapshots and configuration. Output is transient text written into caller-provided buffers.

## Dependencies and Integration Points
It depends on VDO dedupe/indexer/statistics/thread-device/VDO structures, logging, and allocation. It integrates with status-message paths that expose VDO operational counters and configuration to userspace.

## Risks and Edge Cases
The writers subtract `count` from an unsigned `maxlen`; if callers provide an already exhausted buffer, truncation behavior depends on `scnprintf()` return semantics and could underflow if misused. Output is manually formatted and must stay compatible with userspace parsers. `vdo_write_stats()` can fail only if temporary allocation fails.

## Test Signals
Validate full stats and config output for normal and small buffers, parser compatibility, fractional index memory values, every nested statistics block, allocation failure in stats snapshot, and stable field names expected by management tools.
