<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kwork.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/kwork.h

## Purpose

`kwork.h` defines the data model and BPF hook interface for perf's kernel work analysis commands, covering IRQs, softirqs, workqueues, and scheduler work.

## Important APIs, Types, and Functions

It defines class/report/trace enums, `struct kwork_atom`, `kwork_atom_page`, `kwork_work`, `kwork_class`, `trace_kwork_handler`, `kwork_top_stat`, and `perf_kwork`. It declares BPF-backed prepare/read/start/finish/cleanup functions when `HAVE_BPF_SKEL` is set and inline failure/no-op stubs otherwise.

## Control Flow

Trace handlers classify raise/entry/exit/sched-switch events into classes and works. Work objects own atom lists by trace type and derived runtime, latency, and top statistics. `perf_kwork` holds global filters, options, class lists, atom page pool, sorted work roots, and callback to add/find work.

## State and Persistence Behavior

State is in-memory for a run. Atom pages pool fixed arrays of 128 atoms with a bitmap allocator. Works accumulate max/total runtime and latency, CPU usage, TGID, and kthread flags. Filters include CPU bitmap and time interval.

## Dependencies and Integration Points

It depends on perf tool/session/sample types, time utilities, Linux bitmaps/lists/rbtree/types, and optional BPF skeleton support. It integrates command-line options, tracepoint handlers, BPF collection, and report/top rendering code elsewhere.

## Risks and Edge Cases

The nested class/work/atom model requires consistent lifetime management and atom pairing. Missing BPF support returns `-1` from prepare/read and no-ops lifecycle hooks, so callers need fallback behavior. Fixed `MAX_NR_CPUS` bitmaps and atom-page pooling need bounds checks.

## Test Signals

Tests should cover tracepoint and BPF paths, IRQ/softirq/workqueue/sched classes, runtime/latency/top reports, CPU and time filters, atom allocation exhaustion/reuse, lost-event accounting, and no-BPF fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kwork.h -->
