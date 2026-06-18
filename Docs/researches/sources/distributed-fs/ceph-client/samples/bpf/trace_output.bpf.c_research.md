<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/trace_output.bpf.c -->
# sources/distributed-fs/ceph-client/samples/bpf/trace_output.bpf.c

## Purpose
`trace_output.bpf.c` is a minimal syscall tracing program that emits records to a perf event array on every `write()` syscall.

## Important APIs, Types, And Functions
The `my_map` `BPF_MAP_TYPE_PERF_EVENT_ARRAY` map is consumed by userspace. `bpf_prog1()` is attached to `ksyscall/write` and uses `bpf_get_current_pid_tgid()` and `bpf_perf_event_output()`.

## Control Flow
On each traced write syscall, the program fills a small struct with pid/tgid and constant cookie `0x12345678`, then outputs it to the perf event array for the current CPU.

## State And Persistence
The perf event array map persists while the BPF object is loaded. Event records are transient and delivered to perf buffers.

## Dependencies And Integration Points
It depends on syscall tracing attachment, perf event array maps, and the companion `trace_output_user.c` perf buffer reader.

## Risks And Edge Cases
High write rates can overflow perf buffers or increase overhead. The map has max entries `2`, so systems or readers expecting broader CPU coverage must size it appropriately or rely on sample constraints.

## Test Signals
The userspace reader should receive records with cookie `0x12345678` and print an event rate after `MAX_CNT` events without reporting cookie mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/trace_output.bpf.c -->
