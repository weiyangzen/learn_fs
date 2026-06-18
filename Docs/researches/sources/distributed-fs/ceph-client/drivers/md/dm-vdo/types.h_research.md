# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/types.h

## Purpose
`types.h` defines common VDO scalar typedefs, persisted enums, configuration structures, completion types, async action callback types, priorities, and the base `vio` wrapper used for block I/O.

## Important APIs, Types, And Functions
Important typedefs include block counts, logical/physical block numbers, sequence numbers, slab counts, thread IDs, and zone counts. Persisted enums include `vdo_state`, `journal_operation`, `partition_id`, `vdo_metadata_type`, and block mapping state. Important structs include `block_map_slot`, `data_location`, `slab_config`, `thread_count_config`, `device_config`, `vdo_completion`, and `vio`. Inline helpers classify VDO states requiring recovery or read-only rebuild.

## Control Flow
The only executable logic is in inline state predicates. The rest of the file establishes shared type contracts used by completion scheduling, metadata layout, device configuration, and I/O submission.

## State And Persistence
Several enums are explicitly persisted on storage, so numeric values must be preserved. `slab_config` and `thread_count_config` are packed and participate in equality or on-disk/parsed configuration comparisons. `vdo_completion` and `vio` are runtime structures that carry async callback, result, owning VDO, priority, queue link, bio, data buffer, and I/O sizing state.

## Dependencies And Integration Points
The file includes Linux bio/block/device-mapper/list/type headers and `funnel-queue.h`. It is foundational for most VDO modules, including slab depot, recovery journal, block map, VIO pools, and admin completion code.

## Risks
Changing persisted enum values, packed struct layout, or completion priority values can break compatibility or scheduling assumptions. `vdo_completion` is shared across async code, so callback thread IDs, completion type assertions, and queue links must be maintained consistently. `vio` embeds a bio pointer and merge list, making ownership and completion ordering important.

## Test Signals
Tests should verify persisted numeric values, packed sizes/layout where relevant, state predicate behavior, completion type assertions in users, VIO priority routing, and configuration equality/serialization compatibility.
