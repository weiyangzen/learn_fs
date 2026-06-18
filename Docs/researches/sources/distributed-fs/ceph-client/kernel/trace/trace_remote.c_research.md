# sources/distributed-fs/ceph-client/kernel/trace/trace_remote.c

## Purpose

`trace_remote.c` implements tracefs support for remote trace producers such as firmware or hypervisors that write into trace-compatible ring buffers while the kernel reads them. It registers `remotes/<name>` controls, creates eventfs metadata, lazily loads/unloads remote buffers, and provides consuming `trace_pipe` plus non-consuming `trace` readers. The complete 1384-line file was read.

## Important APIs, Types, and Functions

Public APIs are `trace_remote_register()`, `trace_remote_alloc_buffer()`, and `trace_remote_free_buffer()`. Core types are `struct trace_remote` and `struct trace_remote_iterator`. Important helpers cover load/unload, tracing enable/disable, reset, reader get/put, iterator allocation/read/move/print, tracefs file operations, event enable/id/format files, event directory files, event attachment, and sorted event lookup.

## Control Flow

Registration allocates a remote, initializes locks/defaults, creates tracefs, attaches a sorted event table, creates eventfs directories, and invokes optional callback init. Enabling tracing loads the buffer and calls `enable_tracing(true)`. Readers also load the buffer and increment `nr_readers`. `trace_pipe` consumes events after polling/waiting; `trace` uses ring-buffer iterators for non-consuming chronological reads. The buffer unloads only when tracing is off, no readers remain, and it is empty.

## State and Persistence Behavior

`struct trace_remote` persists after registration and owns callbacks, private data, tracefs dentries, eventfs state, event metadata, buffer size, poll interval, tracing state, reader count, and locks. Buffer memory is loaded lazily. Event enable state is stored in caller-provided `remote_event` entries. Iterators hold trace sequences, ring iterators, delayed work, CPU selection, and current event data.

## Dependencies and Integration Points

It depends on `linux/trace_remote.h`, remote ring buffer APIs, tracefs, eventfs, seq_file, delayed work, CPU trace file helpers, and caller callbacks for buffer load/unload, reader-page swapping, reset, tracing enable, and event enable.

## Risks and Edge Cases

Risks include cleanup after partial registration failure, unsorted/duplicate event IDs, reader count overflow, per-CPU lock allocation failure, buffer-size changes while loaded, delayed poll work lifetime, event print overflow, missing CPU descriptors, and bulk event enable ignoring individual errors.

## Test Signals

Register a fake remote; validate tracefs/eventfs files; toggle tracing/events; resize while unloaded; read `trace` and `trace_pipe`; exercise per-CPU readers, lost events, unknown event IDs, sorted-event validation, and lazy unload after draining.
