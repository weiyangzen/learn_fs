# sources/distributed-fs/ceph-client/include/trace/events/block.h

## Purpose
`block.h` is the block layer tracepoint schema. It records request and bio lifecycle events, queue plug/unplug behavior, remapping, splits, completions, errors, buffer-head touches, zone management, and zoned write plug activity.

## Important APIs, types, and functions
Event classes include `block_buffer`, `block_rq_completion`, `block_rq`, `block_bio`, `block_unplug`, and `block_zwplug`. Events include `block_rq_requeue`, `block_rq_complete`, `block_rq_error`, request insert/issue/merge/io-start/io-done, `block_bio_complete`, bio back/front merge and queue events, `block_getrq`, zone append update, plug/unplug, split, bio/request remap, `blkdev_zone_mgmt`, `disk_zone_wplug_add_bio`, and `blk_zone_wplug_bio`.

## Control flow
Call sites in buffer, bio, request, scheduler, mapper, and zoned-device paths emit events as I/O moves from bio creation, queueing, merging, request allocation, issue, completion/error, and remap/split transformations. Completion events convert `blk_status_t` to errno and preserve ioprio fields.

## State and persistence behavior
The header has no state. Records snapshot device ids, sectors, byte counts, rwbs strings, command placeholder strings, current task command, ioprio class/hint/level, old mapping device/sector, queue depth, zone number, and errors.

## Dependencies and integration points
It depends on block core types and helpers from `<linux/blkdev.h>`, `<linux/blktrace_api.h>`, buffer heads when configured, and uapi ioprio definitions. It is a stable integration point for blktrace-style tooling, ftrace, perf, BPF, and storage performance analysis.

## Risks and test signals
Risks include tracepoint ABI sensitivity, stale comments versus modern blk-mq behavior, null disk handling in some request events, and using event timing as a proxy without accounting for batching. Test signals are fio or xfstests workloads with expected queue/issue/complete ordering, remap traces through dm/md, split traces on limits, zone-management traces on zoned devices, and ioprio decoding.
