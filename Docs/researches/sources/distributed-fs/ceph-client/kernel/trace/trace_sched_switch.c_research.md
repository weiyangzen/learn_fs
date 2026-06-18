# sources/distributed-fs/ceph-client/kernel/trace/trace_sched_switch.c

## Purpose

`trace_sched_switch.c` records task command names and TGIDs for trace output correlation. It registers scheduler tracepoint probes on demand, maintains saved command-line and TGID caches, and exposes tracefs operations for saved command lines, command-line cache size, and saved TGIDs. The complete 665-line file was read.

## Important APIs, Types, and Functions

Public functions include `tracing_start_cmdline_record()`, `tracing_stop_cmdline_record()`, `tracing_start_tgid_record()`, `tracing_stop_tgid_record()`, `trace_create_savedcmd()`, `trace_save_cmdline()`, `trace_find_cmdline()`, `trace_find_tgid()`, `tracing_record_taskinfo()`, `tracing_record_taskinfo_sched_switch()`, `trace_alloc_tgid_map()`, and file operations for saved TGIDs, cmdlines, and cmdline size.

## Control Flow

Start/stop helpers reference count command-name and TGID needs. The first reference registers `sched_wakeup`, `sched_wakeup_new`, and `sched_switch`; the last unregisters them. Tracepoint probes record both sides of switches and wakeups. Command-line recording hashes PID into a rotating cache under `trace_cmdline_lock`; TGID recording writes to a PID-indexed map.

## State and Persistence Behavior

Global state includes tracepoint refcounts, `tgid_map`, `tgid_map_max`, and `savedcmd`. Command-line cache storage is fixed-size but resizable through tracefs. TGID map size follows `init_pid_ns.pid_max`. Per-CPU `trace_taskinfo_save` suppresses repeated recording.

## Dependencies and Integration Points

The file depends on scheduler tracepoints, task structs, tracing per-CPU flags, tracefs open helpers, seq_file, kmemleak annotations, and trace output paths that call `trace_find_cmdline()` or `trace_find_tgid()`.

## Risks and Edge Cases

The command-line cache is lossy due to PID hashing and rotation. `trace_save_cmdline()` uses trylock in scheduler context and may skip updates. TGID map publication relies on release/acquire ordering. Start/stop calls must be balanced. Resizing swaps the global command cache while readers/writers are spinlock protected.

## Test Signals

Check saved cmdline and TGID tracefs reads, cache resize, map allocation, balanced reference counts, tracepoint registration failures, PID reuse, idle task handling, and trace output with comm/TGID after scheduler events.
