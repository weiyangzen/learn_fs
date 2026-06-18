# sources/distributed-fs/ceph-client/include/linux/relay.h

Purpose: this header declares the relay channel API, a high-throughput per-CPU buffering interface used to stream kernel data to files, often through relayfs/debugfs.

Important APIs/types/functions: core types are `struct rchan`, `struct rchan_buf`, `struct rchan_callbacks`, and `struct rchan_buf_stats`. APIs include `relay_open()`, `relay_close()`, `relay_flush()`, `relay_stats()`, `relay_subbufs_consumed()`, `relay_reset()`, `relay_buf_full()`, `relay_switch_subbuf()`, `relay_write()`, `__relay_write()`, `relay_reserve()`, `subbuf_start_reserve()`, and exported `relay_file_operations`.

Control flow: clients open a channel with sub-buffer sizing and callbacks. The core creates one per-CPU buffer or one global buffer through `create_buf_file()`. Producers write to the current CPU buffer; if `offset + length` exceeds `subbuf_size`, `relay_switch_subbuf()` finalizes the current sub-buffer and starts another. Consumers read via relay file operations and report consumption with `relay_subbufs_consumed()`. `subbuf_start` may reserve header bytes at each new sub-buffer.

State and persistence: `rchan` owns channel geometry, callbacks, private data, per-CPU buffers, dentry metadata, and reference count. `rchan_buf` tracks buffer pointers, offsets, produced/consumed sub-buffer counters, wait queues, IRQ wakeups, padding, stats, CPU, and finalization state. Data is volatile kernel memory exposed through files while the channel exists.

Dependencies and integration points: depends on scheduler/preemption, timers, wait queues, lists, irq_work, VFS dentries/file operations, krefs, and percpu APIs. It integrates with tracing and custom kernel instrumentation.

Risks: callers must choose `relay_write()` for interrupt-context safety or `__relay_write()` for preemption-only protection; `relay_reserve()` performs no synchronization beyond CPU pinning. Incorrect consumed counts can stall writers or lose data. Test signals include per-CPU write/read tests, buffer-full/stat counter checks, callback sequencing, CPU hotplug via `relay_prepare_cpu`, and teardown while readers hold references.
