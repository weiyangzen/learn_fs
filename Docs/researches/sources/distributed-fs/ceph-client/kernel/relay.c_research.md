# sources/distributed-fs/ceph-client/kernel/relay.c

## Purpose
`relay.c` implements the generic relay channel API for high-volume kernel-to-userspace data transfer through per-CPU or global ring-like buffers exposed as files. It handles buffer allocation, vmalloc-backed mmap, sub-buffer switching, reader wakeups, hotplug buffer creation, file operations, and channel lifetime management.

## Important APIs, Types, and Functions
- Channel/buffer lifecycle: `relay_open()`, `relay_close()`, `relay_reset()`, `relay_flush()`, `relay_prepare_cpu()`, `relay_create_buf()`, `relay_destroy_buf()`, and `relay_close_buf()`.
- Buffer operations: `relay_buf_full()`, `relay_switch_subbuf()`, `relay_subbufs_consumed()`, `relay_stats()`, and callback wrapper `relay_subbuf_start()`.
- Mapping/allocation: `relay_alloc_buf()`, `relay_mmap_prepare_buf()`, `relay_buf_fault()`, and `relay_file_mmap_ops`.
- File operations: `relay_file_open()`, `relay_file_poll()`, `relay_file_mmap_prepare()`, `relay_file_read()`, `relay_file_release()`, and exported `relay_file_operations`.
- Read helpers: `relay_file_read_consume()`, `relay_file_read_avail()`, `relay_file_read_subbuf_avail()`, `relay_file_read_start_pos()`, and `relay_file_read_end_pos()`.

## Control Flow
`relay_open()` validates sizes and callbacks, allocates `struct rchan` plus a per-CPU pointer array, initializes channel metadata, and under `relay_channels_mutex` opens buffers for online CPUs. `relay_open_buf()` creates a buffer, optionally asks the client to create a relay file, initializes buffer state with `__relay_reset()`, and handles global-channel sharing. CPU hotplug calls `relay_prepare_cpu()` to add missing buffers for existing channels.

Writers reserve space through higher-level relay helpers and eventually call `relay_switch_subbuf()` when a sub-buffer is complete or an event does not fit. The function records padding, increments produced counts, updates inode size or early byte counts, uses a memory barrier before waking readers via deferred `irq_work`, calls the client `subbuf_start` callback for the next sub-buffer, and returns zero if the buffer is full or the event is too large.

Readers open relay files to get a buffer reference, poll on `read_wait`, mmap through vm fault translation from vmalloc addresses to pages, or read through `relay_file_read()`. Reads are serialized by the inode lock, skip padding, consume complete sub-buffers, handle overwritten data by advancing consumed counters, copy available bytes to userspace, and update file position modulo the circular buffer.

Closing a channel removes it from the global list, marks each buffer finalized, synchronizes pending wakeup irq work, calls client `remove_buf_file`, and drops krefs. Buffer destruction unmaps vmap memory, frees pages and padding, clears the per-CPU pointer, and drops the channel kref.

## State and Persistence
Global state is `relay_channels` protected by `relay_channels_mutex`. Channel state includes sub-buffer size/count, allocation size, base filename, parent dentry, callbacks, private data, per-CPU buffer pointers, global-channel flag, and kref. Buffer state includes vmapped pages, page array, padding array, produced/consumed counters, bytes consumed, current data pointer and offset, dentry, waitqueue, irq work, stats, finalized flag, CPU number, early byte count, and kref. Data lives in memory and is exposed through relay files; it is not durable.

## Dependencies and Integration Points
The file depends on relay API structures and client callbacks, debugfs or another filesystem chosen by `create_buf_file`, vmalloc/vmap and page allocation, mmap VM operations, wait queues, irq_work, poll/read file operations, CPU hotplug, per-CPU allocation, krefs, usercopy, and inode sizing. Users include tracing and instrumentation subsystems that need efficient streaming to userspace.

## Risks
Risks include buffer size overflow, allocation failure across many CPUs, races with CPU hotplug and channel close, readers seeing overwritten data, incorrect padding accounting, wakeups from scheduler-sensitive contexts, mmap faults after buffer teardown, and callback misuse. The code mitigates some hazards with `relay_channels_mutex`, krefs, inode read locking, irq_work-deferred wakeups, size validation, and finalized checks, but clients must still coordinate reset/close with active writers.

## Test Signals
Signals include relay open failure on invalid sizes or missing callbacks, per-CPU file creation during CPU hotplug, read/poll behavior when sub-buffers are produced, mmap page faults over the whole allocation, `relay_stats()` full/big counters, overwrite/consume behavior under slow readers, reset/flush semantics with active mappings, and kref cleanup after file release and channel close.
