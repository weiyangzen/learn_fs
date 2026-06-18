# `sources/distributed-fs/ceph-client/drivers/md/dm-ebs-target.c`

## Purpose

`dm-ebs-target.c` implements the `ebs` target, which emulates a smaller exposed logical block size on a backing device with a larger logical block size. It is intended for cases such as 512-byte sector emulation over 4K-native media and for testing `dm-bufio` overhead.

## Important APIs, Types, and Functions

`struct ebs_c` stores the backing device, `dm_bufio_client`, ordered workqueue, queued bio list, lock, start sector, emulated and underlying block sizes, sector-to-block shift, and whether the underlying size was explicitly configured. `ebs_ctr()` parses `<dev_path> <offset> <ebs> [<ubs>]`, validates power-of-two sector sizes, infers `ubs` from the lower device if omitted, validates start alignment, creates the bufio client, and creates an ordered workqueue. `ebs_map()` remaps flushes directly, queues partial or overlapping IO for bufio processing, and remaps fully aligned IO directly after forgetting cached buffers. `__ebs_process_bios()` performs read, write, and discard processing from the queued list.

## Control Flow

Partial reads and writes are queued to the worker. The worker first prefetches all read buffers and misaligned write-edge buffers, then copies data between bio vectors and bufio blocks through `__ebs_rw_bio()`/`__ebs_rw_bvec()`. Writes use read-modify-write unless a full underlying block is overwritten, in which case `dm_bufio_new()` avoids an unnecessary read. Discards forget cached buffers and issue lower-device discards only for complete underlying blocks, avoiding partial-block data loss. Dirty buffers are written before bios are ended so FUA/sync semantics are addressed.

## State and Persistence Behavior

There is no independent metadata. Data persistence is the lower block device content, mediated by `dm-bufio` for partial-block modifications. `ebs_postsuspend()` resets the bufio client, dropping cached state at suspend.

## Dependencies and Integration Points

The target integrates through `.ctr`, `.dtr`, `.map`, `.postsuspend`, `.status`, `.io_hints`, `.prepare_ioctl`, and `.iterate_devices`. It depends on `dm-bufio`, ordered workqueues, bio lists, block queue limits, and lower-device logical block size. IO hints expose the emulated logical size and underlying physical size to upper layers.

## Risks and Edge Cases

Correctness depends on handling partial first and last underlying blocks without discarding or overwriting unrelated data. The worker records an error if any per-buffer copy fails but still attempts remaining buffers, so tests should inspect final bio status. Fully aligned direct IO must invalidate bufio cache ranges or stale cached data could later overwrite direct writes. Flushes are remapped, not bufio-queued, so dirty bufio write ordering around flush-sensitive workloads is an important test area.

## Test Signals

Tests should cover omitted and explicit `ubs`, invalid sizes and offsets, partial read/write at both edges, full-block direct IO, discard alignment, cache invalidation after direct writes, postsuspend cache reset, io-hints values, and ioctl forwarding only for exact full-device mappings.
