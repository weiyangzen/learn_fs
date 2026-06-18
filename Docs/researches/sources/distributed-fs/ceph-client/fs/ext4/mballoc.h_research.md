# sources/distributed-fs/ceph-client/fs/ext4/mballoc.h

## Purpose
`mballoc.h` declares the data structures, defaults, debug macros, helper functions, and test-only exports used by ext4's multiblock allocator. It defines the allocator's shared vocabulary: free extents, allocation contexts, buddy views, preallocation descriptors, delayed-free descriptors, locality groups, scan tunables, and the callback signature for querying allocator ranges.

## Important APIs, Types, And Functions
Tunables include `MB_DEFAULT_MAX_TO_SCAN`, `MB_DEFAULT_MIN_TO_SCAN`, `MB_DEFAULT_STATS`, `MB_DEFAULT_STREAM_THRESHOLD`, `MB_DEFAULT_ORDER2_REQS`, `MB_DEFAULT_GROUP_PREALLOC`, `MB_DEFAULT_LINEAR_LIMIT`, `MB_DEFAULT_LINEAR_SCAN_THRESHOLD`, `MB_DEFAULT_BEST_AVAIL_TRIM_ORDER`, and `MB_NUM_ORDERS(sb)`.

`struct ext4_free_data` describes a free cluster extent that has been cleared from disk but cannot be returned to the buddy until its journal transaction commits. `struct ext4_prealloc_space` describes inode or group preallocation state, including object linkage, group linkage, locks, refcount, deletion state, physical/logical start, length/free counts, type, and owner. `struct ext4_free_extent` is the allocator's group-relative extent form. `struct ext4_locality_group` holds per-CPU group PA buckets. `struct ext4_allocation_context` is the allocator work object. `struct ext4_buddy` represents a loaded block group's bitmap and buddy.

Public declarations are `ext4_mballoc_query_range()` and `ext4_mb_mark_context()`. KUnit builds expose selected internal helpers from `mballoc.c`.

## Control Flow
This header shapes `mballoc.c` control flow. `ext4_mb_new_blocks()` fills `ext4_allocation_context` from `ext4_allocation_request`, normalizes `ext4_free_extent` values, consumes or creates `ext4_prealloc_space`, and loads groups via `ext4_buddy`.

The declared PA model determines the two preallocation paths: inode PAs are found by logical range in a per-inode rb-tree, while group PAs are selected from per-CPU locality buckets by remaining size and physical distance from the goal. `ext4_free_data` supports the delayed-free path keyed by journal transaction id.

## State And Persistence Behavior
All structures here are in-memory allocator state. They protect or mirror persistent bitmap/group-descriptor state but are not stored on disk. Many length/start fields are in clusters rather than filesystem blocks, which is critical for bigalloc.

`pa_count`, `pa_deleted`, `pa_lock`, `pa_node_lock`, and RCU/list/rb-tree linkage define PA lifetime. `extent_logical_end()` and `pa_logical_end()` return `loff_t` to avoid logical-block overflow.

## Dependencies And Integration Points
The header includes Linux fs/quota/buffer/proc/block/mutex/page headers plus `ext4_jbd2.h` and `ext4.h`. It depends on ext4 block, group, inode, journal, and allocation-request types. `mb_debug()` integrates with `CONFIG_EXT4_DEBUG`; test declarations integrate with ext4 KUnit modules.

## Risks And Edge Cases
The main risks are unit confusion between blocks and clusters, PA lifetime misuse, stale object lock pointers, incorrect rb-tree ordering/non-overlap assumptions, and overflow around large logical ends. Callers must respect the locking/lifetime model and use ext4 conversion macros consistently.

## Test Signals
Tests should cover bigalloc unit conversion, PA rb-tree ordering and deletion, logical-end calculations near the maximum block range, delayed-free transaction bucketing, and synchronization between KUnit declarations and exported implementations.
