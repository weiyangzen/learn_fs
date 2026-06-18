# sources/distributed-fs/ceph-client/drivers/md/dm-rq.h

## Purpose
Defines the internal request-based DM interface shared by request mapping, table mempool sizing, and sysfs compatibility attributes.

## Important APIs, Types, And Functions
`struct dm_rq_clone_bio_info` stores the original bio, request `tio`, and embedded clone bio used with bioset front padding. The header declares queue lifecycle helpers `dm_mq_init_request_queue()` and `dm_mq_cleanup_mapped_device()`, queue controls `dm_start_queue()`, `dm_stop_queue()`, `dm_mq_kick_requeue_list()`, reserved IO sizing, and legacy `rq_based_seq_io_merge_deadline` sysfs handlers.

## Control Flow
The header has no executable flow. `dm-table.c` uses its clone-bio layout for request-based mempools; `dm-rq.c` implements the declared blk-mq setup and queue helpers; `dm-sysfs.c` exposes the compatibility attribute declarations.

## State And Persistence
No state is stored here. The structures describe runtime clone-bio metadata only; no persistence exists.

## Dependencies And Integration Points
Includes Linux bio/kthread headers and `dm-stats.h`, with a forward declaration of `struct mapped_device`. It is an internal contract for request-based mapped devices.

## Risks
The embedded `struct bio clone` must remain compatible with front-pad allocation and `container_of()` recovery. Removing compatibility declarations can break old userspace probes.

## Test Signals
Compile request-based DM and run multi-bio cloned request tests, sysfs read/write tests for `rq_based_seq_io_merge_deadline`, queue quiesce/unquiesce, and mempool allocation on request-based table load.
