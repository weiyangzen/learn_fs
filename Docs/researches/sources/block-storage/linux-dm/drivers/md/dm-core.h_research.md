# File Research: sources/block-storage/linux-dm/drivers/md/dm-core.h

## Purpose
Defines Device Mapper core internal structures and helpers used by `dm.c`, `dm-rq.c`, and `dm-table.c`. It explicitly warns that DM targets must not directly dereference `mapped_device` or `dm_table` internals.

## Main Interfaces
- Core structures: `struct mapped_device`, `struct dm_table`, `struct dm_target_io`, `struct dm_io`.
- Flags: `DMF_BLOCK_IO_FOR_SUSPEND`, `DMF_SUSPENDED`, `DMF_FROZEN`, `DMF_FREEING`, `DMF_DELETING`, `DMF_NOFLUSH_SUSPENDING`, `DMF_DEFERRED_REMOVE`, `DMF_SUSPENDED_INTERNALLY`, `DMF_POST_SUSPENDING`, `DMF_EMULATE_ZONE_APPEND`.
- Helpers: `dm_get_size()`, `dm_get_stats()`, `dm_emulate_zone_append()`, `dm_io_inc_pending()`, `dm_get_completion_from_kobject()`, `dm_message_test_buffer_overflow()`.
- Declarations: discard/write-same/write-zeroes disabling, pending I/O decrement, module-param access, and global event signaling.

## Control Flow
The header does not implement target behavior; it establishes the shared in-memory shape of mapped devices, tables, cloned target bios, and original bio tracking. Inline helpers expose safe access to capacity, stats, zone-append emulation state, pending I/O count increment, kobject completion lookup, and message-buffer overflow checks.

## State And Synchronization
`mapped_device` carries suspend/table/device locks, RCU table pointer, queue/type lock, holder/open counts, deferred bio list, event queues, mempools, workqueue, stats, blk-mq tag set, SRCU I/O barrier, optional zoned state, and optional IMA measurements. `dm_table` stores the btree target index, target array, device list, event callback, mempools, mode, integrity, and optional inline crypto profile. `dm_io` and `dm_target_io` track original and cloned bio completion state.

## Integration Points
This is an internal dependency for DM core implementation files, not ordinary targets. It bridges block-layer types, DM public declarations, IMA measurement support, blk-mq, inline encryption, zoned block devices, and block trace events.

## Notable Behaviors
- `dm_table` supports up to `DM_TABLE_MAX_DEPTH` btree levels.
- `dm_target_io` embeds the cloned `bio` as its last field.
- `dm_io` embeds the first target I/O object and tracks aggregate completion status.
- Global DM event state is declared for cross-device event notification.

## Risks And Review Focus
- The internal-only boundary matters: target code should use exported helpers rather than depending on these layouts.
- Flag bits coordinate suspend, remove, noflush suspend, and zone append emulation, so changes have broad core behavior impact.
- Embedded bio/layout assumptions in `dm_target_io` and `dm_io` are allocation-sensitive.
