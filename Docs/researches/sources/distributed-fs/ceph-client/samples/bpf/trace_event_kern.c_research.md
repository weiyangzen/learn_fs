<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/trace_event_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/trace_event_kern.c

## Purpose
`trace_event_kern.c` is a perf-event BPF program that collects kernel and user stack traces keyed by current command and stack ids, while also demonstrating perf-event value and address reads.

## Important APIs, Types, And Functions
The maps are `counts` (`BPF_MAP_TYPE_HASH`) and `stackmap` (`BPF_MAP_TYPE_STACK_TRACE`). The entry point `bpf_prog1()` uses `bpf_get_current_comm()`, `bpf_get_stackid()`, `bpf_perf_prog_read_value()`, `bpf_get_smp_processor_id()`, `PT_REGS_IP()`, `bpf_map_lookup_elem()`, and `bpf_map_update_elem()`.

## Control Flow
The program ignores warmup samples with small `sample_period`, records current command, gets kernel and user stack ids, prints fallback diagnostics when both stack ids fail, reads perf-event enabled/running time, optionally prints recorded address, then increments or creates the count for the `(comm,kernstack,userstack)` key.

## State And Persistence
Stack trace samples persist in `stackmap`; aggregate counts persist in `counts` until userspace drains and deletes them. Other values are per-event.

## Dependencies And Integration Points
It depends on perf-event program attachment, stack trace helper support, perf event data context, and the companion userspace program that attaches across event types and prints stacks.

## Risks And Edge Cases
Stack id collection can fail due to collisions, missing user stacks, or unsupported contexts. `bpf_perf_prog_read_value()` can fail for inherited task events. Trace printing can be noisy and changes timing.

## Test Signals
Expected signals are nonzero count entries, stack ids resolvable from `stackmap`, perf enabled/running trace lines for all-CPU events, optional address lines for precise events, and userspace validation that kernel stacks include read/write syscall paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/trace_event_kern.c -->
