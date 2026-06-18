<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex3.bpf.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tracex3.bpf.c

## Purpose
`tracex3.bpf.c` measures block I/O latency by recording timestamps at block I/O start tracepoints and adding completions to a logarithmic per-CPU latency histogram.

## Important APIs, Types, And Functions
Maps are `my_map` for start timestamps keyed by device/sector and `lat_map` as a 100-slot per-CPU array. Programs are `bpf_prog1()` for `tracepoint/block/block_io_start` and `bpf_prog2()` for `tracepoint/block/block_io_done`. Helper `log2l()` approximates log scaling.

## Control Flow
The start tracepoint stores `bpf_ktime_get_ns()` under a `start_key`. The done tracepoint looks up the start time, computes delta, deletes the start entry, converts latency to a log-scaled index, clamps it to the histogram range, and increments the per-CPU slot.

## State And Persistence
Outstanding I/O timestamps persist in `my_map` until completion. Histogram counts persist in `lat_map` until userspace reads and clears them.

## Dependencies And Integration Points
It depends on block tracepoint format, BPF per-CPU array maps, and the companion userspace histogram printer.

## Risks And Edge Cases
Device/sector alone may collide for overlapping requests. Missing start events produce no histogram increment. Long-lived entries can accumulate if completion events are missed. The log math is approximate by design.

## Test Signals
Under disk activity, the userspace program should print nonzero latency heatmap counts and clear slots between intervals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex3.bpf.c -->
