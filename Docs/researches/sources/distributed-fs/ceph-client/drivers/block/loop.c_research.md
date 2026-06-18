# sources/distributed-fs/ceph-client/drivers/block/loop.c

## Purpose
Implements Linux loop block devices: block devices backed by regular files or block devices. It manages dynamic `/dev/loopN` allocation, `/dev/loop-control`, ioctl-based binding/configuration, sysfs reporting, blk-mq request handling, cgroup-aware worker dispatch, direct-I/O enablement, discard/write-zeroes/flush forwarding, partition scanning, autoclear, and module lifecycle.

## Important APIs, Types, And Functions
- `struct loop_device` is the main device object. It stores identity, offset, sizelimit, flags, backing file, minimum direct-I/O alignment, owning block device, saved mapping GFP mask, state, queues, disk, mutexes/spinlocks, sysfs state, and per-cgroup worker structures.
- `struct loop_cmd` is the blk-mq per-request payload. It tracks queued work-list membership, AIO mode, completion refcount/result, `kiocb`, temporary bio-vector copies, and blkcg/memcg context references.
- Device states are `Lo_unbound`, `Lo_bound`, `Lo_rundown`, and `Lo_deleting`, with transitions guarded by `lo_mutex` plus `loop_validate_mutex` when loop-on-loop recursion must be serialized.
- `loop_configure()`, `loop_change_fd()`, `loop_clr_fd()`, and `__loop_clr_fd()` bind, switch, mark-for-clear, and fully unbind backing files.
- `lo_ioctl()`, `lo_simple_ioctl()`, `loop_set_status()`, `loop_get_status()`, `loop_set_block_size()`, `loop_set_capacity()`, and `loop_set_dio()` implement the loop ioctl ABI.
- `loop_queue_rq()`, `loop_queue_work()`, `loop_handle_cmd()`, `do_req_filebacked()`, `lo_rw_aio()`, `lo_fallocate()`, `lo_req_flush()`, and `lo_complete_rq()` implement request submission and completion.
- `loop_add()`, `loop_remove()`, `loop_control_ioctl()`, `loop_control_get_free()`, `loop_control_remove()`, `loop_init()`, and `loop_exit()` manage device creation/removal and `/dev/loop-control`.
- Sysfs reporting is provided by the read-only `loop` attribute group: `backing_file`, `offset`, `sizelimit`, `autoclear`, `partscan`, and `dio`.

## Control Flow
Module initialization computes `part_shift` from `max_part`, validates minor-space limits, registers the loop-control misc device, registers the loop block major with optional legacy autoload probe, and pre-creates `max_loop` devices with `loop_add()`. `loop_add()` allocates a `loop_device`, reserves an IDR slot, allocates a blk-mq tag set and disk, initializes state/locks/worker lists/timer, configures minors and partition-scan suppression, adds the disk, and marks it visible in the IDR.

Binding starts from `LOOP_SET_FD` or `LOOP_CONFIGURE`. `loop_configure()` gets the userspace file descriptor, verifies read/write iterator support, claims the block device if needed, takes global validation locks when backing another loop device, rejects already-bound devices and recursive loop chains, validates flags/status, creates the workqueue, suppresses uevents, marks media changed, sets read-only state, assigns the backing file, adjusts the backing mapping GFP mask to avoid filesystem recursion, updates queue limits and discard capabilities, flushes the file before possible direct I/O, updates effective direct-I/O flags, creates sysfs attributes, sets capacity, transitions to `Lo_bound`, releases locks, and optionally scans partitions.

I/O flow starts in `loop_queue_rq()`, which rejects unbound devices, chooses AIO/direct-I/O mode for read/write requests, captures the first bio's blkcg and memcg CSS references when cgroup support is enabled, and queues the command. `loop_queue_work()` sends root-cgroup work to a root list/work item or creates/uses an rb-tree-indexed per-blkcg worker. `loop_process_work()` runs commands with local throttling and no-IO memory-reclaim flags. `loop_handle_cmd()` rejects writes to read-only devices, clears `REQ_NOWAIT`, associates blkcg/memcg context, delegates to `do_req_filebacked()`, releases cgroup context, and completes synchronous commands. Reads and writes use `lo_rw_aio()` over `read_iter`/`write_iter`; flush uses `vfs_fsync`; discard and write-zeroes use `fallocate` or backing-block zeroing semantics.

Completion flow uses `lo_rw_aio_complete()` and `lo_rw_aio_do_completion()` for asynchronous or synchronous iterator results. `lo_complete_rq()` maps negative results to block status, handles full-length success, retries short reads with progress by updating the request and requeueing it, and zero-fills plus fails requests that return no data on read.

Unbind flow has two stages. `loop_clr_fd()` marks a bound device `LO_FLAGS_AUTOCLEAR` and, if there is only one opener, moves it to `Lo_rundown`. `lo_release()` invokes `__loop_clr_fd()` on last close for autoclear/rundown devices. Full clear drops the backing file under `lo_lock`, resets offset/sizelimit/name and block size, invalidates the disk, removes sysfs attributes, restores the backing mapping GFP mask, emits a media-change uevent, optionally rereads partitions to remove them, returns state to `Lo_unbound`, and then drops the file reference outside `lo_mutex`.

Control-device flow uses `LOOP_CTL_ADD` to create a requested index, `LOOP_CTL_REMOVE` to hide and remove an unbound unopened device, and `LOOP_CTL_GET_FREE` to return a visible unbound ID or allocate a new one. Legacy block-device probe can lazily create loop devices by minor when enabled and not capped by an explicit `max_loop`.

## State And Persistence
Persistent kernel state is held in `loop_index_idr`, guarded by `loop_ctl_mutex`, and in each `loop_device`. Bound devices persist their backing file reference, file name, offset, size limit, flags, queue limits, read-only status, disk capacity, sysfs attributes, cgroup worker tree, idle-worker timer, and modified backing mapping GFP mask until clear. `old_gfp_mask` is restored only during `__loop_clr_fd()`, so clear/unbind correctness matters for backing filesystem reclaim behavior.

The backing file contents are the durable storage for the loop block device; loop-specific configuration is in memory and exposed through ioctls/sysfs but not persisted across module unload or reboot. Capacity is derived from backing file or block device size minus offset and sizelimit, rounded to 512-byte sectors.

Worker state persists while commands are active or idle. Non-root blkcg workers are stored in an rb-tree by CSS pointer and moved to an idle list after work drains; a deferrable timer frees idle workers after `LOOP_IDLE_WORKER_TIMEOUT`. Commands hold temporary bvec arrays only when a request spans multiple bios and release them on completion.

## Dependencies And Integration Points
The file integrates with blk-mq (`struct gendisk`, request queues, queue limits, tag sets, request completions), the VFS (`struct file`, `read_iter`, `write_iter`, `fallocate`, `fsync`, `vfs_getattr`, `vfs_statfs`), block-device helpers for capacity, partition rescans, claiming, invalidation, direct I/O alignment, and media-change events, and the IDR/miscdevice infrastructure for dynamic device management.

It exposes the UAPI in `uapi/linux/loop.h` through block-device ioctls and `/dev/loop-control`, including old `struct loop_info`, `struct loop_info64`, `struct loop_config`, and 32-bit compat translations. It also integrates with sysfs through per-disk `loop/*` attributes, module and boot parameters (`max_loop`, `max_part`, `hw_queue_depth`), `CONFIG_BLOCK_LEGACY_AUTOLOAD`, cgroup block and memory controllers, the freezer-aware unbound workqueue system, and module reference counting.

Direct-I/O behavior depends on `FMODE_CAN_ODIRECT`, `O_DIRECT`, `LO_FLAGS_DIRECT_IO`, logical block size, loop offset alignment, filesystem `STATX_DIOALIGN`, and fallback backing block-device logical block size. Discard/write-zeroes behavior depends on file `fallocate` support, statfs block size, and backing block-device zeroing/discard characteristics.

## Risks And Edge Cases
Recursive loop backing is a primary correctness risk. `loop_validate_file()` walks loop-backed files under `loop_validate_mutex` and checks for self-reference; callers must use the global lock when binding or changing to another loop device to avoid races with concurrent clear/configure.

Locking order is delicate. Binding and status changes must coordinate `lo_mutex`, `loop_validate_mutex`, block-device claims, queue freezing, open mutex use during partition scans, and delayed `fput()` outside `lo_mutex` to avoid circular lock dependencies. State reads in request paths use `READ_ONCE`/`data_race` because queueing is hot and can overlap clear.

Direct I/O is effective rather than purely requested. It can be silently cleared when queue logical block size or offset alignment is incompatible, and it requires flushing dirty backing data before enabling. Block-size or offset changes must freeze/drain queues enough to keep bios from being interpreted against inconsistent limits.

Short-read behavior is subtle: partial read progress is requeued, but zero-length reads zero-fill bios and fail with `BLK_STS_IOERR`. Any filesystem or network backing store that returns unusual short I/O should be tested. `REQ_NOWAIT` is explicitly ignored because worker context can block.

Discard/write-zeroes support is optimistic and disabled dynamically when `fallocate` reports unsupported. `loop_clear_limits()` updates queue limits from inside `queue_rq`, which the source comments flag as against the usual queue-freezing protocol and therefore an area of technical debt.

Autoclear and removal races can expose confusing userspace behavior if visibility, opener counts, and state transitions are wrong. `LOOP_CTL_REMOVE` hides a device before checking state and must restore visibility on failure. Forced module unload is explicitly unsafe according to the exit comment.

## Test Signals
Configuration tests should cover `LOOP_CONFIGURE`, legacy `LOOP_SET_FD`, old/new status get/set, invalid encryption types, offset/sizelimit overflow, read-only fallback when backing file or loop opener is not writable, partition-scan flag behavior, block-size changes, direct-I/O enable/disable with aligned and unaligned offsets, and capacity changes after backing-file growth.

I/O tests should cover buffered and direct read/write, flush, discard, write-zeroes with and without `REQ_NOUNMAP`, short reads from sparse/truncated files, writes to read-only loop devices, backing block devices versus regular files, cgroup-specific worker dispatch, memcg association release, request timeout injection, and idle worker cleanup.

Lifecycle tests should cover repeated add/remove through `/dev/loop-control`, `LOOP_CTL_GET_FREE` racing with configure, legacy autoload probe, autoclear after last close, explicit clear while multiple openers exist, change-fd only on read-only loop devices and only to same-size backing stores, loop-on-loop recursion rejection, module unload cleanup, and sysfs attributes before/after bind and clear.

Diagnostics should include lockdep around configure/change/clear/partition-scan paths, KASAN/KCSAN for clear versus in-flight request races, queue-limit correctness after fallocate unsupported responses, restored backing mapping GFP masks after clear, and correct module reference counts across bind/unbind.
