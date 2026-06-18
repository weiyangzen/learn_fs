# sources/distributed-fs/ceph-client/include/trace/events/hugetlbfs.h

Purpose: hugetlbfs tracepoints for inode allocation/free/eviction, attribute changes, and fallocate operations.

Important APIs/types/functions: Declares trace-event macros/classes `class:hugetlbfs__inode`, `event:hugetlbfs_evict_inode`, `event:hugetlbfs_free_inode`, `trace:hugetlbfs_alloc_inode`, `trace:hugetlbfs_fallocate`, `trace:hugetlbfs_setattr`. Defines or exports symbolic enums/helpers none. Representative payload fields include `blocks:blkcnt_t`, `d_len:unsigned int`, `d_name`, `dev:dev_t`, `dir:u64`, `ia_mode:unsigned int`, `ia_size:loff_t`, `ia_valid:unsigned int`, `ino:u64`, `len:loff_t`, `mode:__u16`, `mode:int`, `nlink:unsigned int`, `offset:loff_t`, `old_size:loff_t`, `ret:int`, `seals:unsigned int`, `size:loff_t`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. The header uses inode event classes plus setattr/fallocate events to expose huge page size, inode numbers, blocks, mode, uid/gid, offsets, lengths, and return codes. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Persistent state is inode/page cache/filesystem state; trace buffers hold sampled metadata during operations. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Large offsets and huge-page alignment failures must be printed accurately or capacity and reservation bugs are hard to reproduce. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Mount hugetlbfs, create/unlink files, change attributes, and run fallocate punch/allocate cases while checking trace metadata. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/hugetlbfs`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
