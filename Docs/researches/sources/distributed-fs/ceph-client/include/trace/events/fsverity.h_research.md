# sources/distributed-fs/ceph-client/include/trace/events/fsverity.h

Purpose: fs-verity tracing for enablement, Merkle tree construction completion, data block verification, Merkle cache hits, and Merkle block verification.

Important APIs/types/functions: Declares trace-event macros/classes `trace:fsverity_enable`, `trace:fsverity_merkle_hit`, `trace:fsverity_tree_done`, `trace:fsverity_verify_data_block`, `trace:fsverity_verify_merkle_block`. Defines or exports symbolic enums/helpers none. Representative payload fields include `data_pos:u64`, `data_size:u64`, `file_digest:u8`, `hblock_idx:unsigned long`, `hidx:unsigned int`, `ino:u64`, `level:unsigned int`, `levels:unsigned int`, `merkle_block:unsigned int`, `num_levels:unsigned int`, `root_hash:u8`, `tree_size:u64`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. The events follow the fs-verity lifecycle from enabling an inode through tree building and per-block verification at data and Merkle levels. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Trace payloads snapshot inode numbers, tree/data sizes, Merkle tree levels, data positions, hash block indexes, and cache-hit metadata. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Incorrect level/block indexing in traces can mask integrity bugs or make cache-hit accounting look correct when verification used a different block. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Enable fs-verity on test files, read verified ranges, force Merkle cache hits/misses, and corrupt data/Merkle blocks to confirm traces and failures. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/fsverity`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
