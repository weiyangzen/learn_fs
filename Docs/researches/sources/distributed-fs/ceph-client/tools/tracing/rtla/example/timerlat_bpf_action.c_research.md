# sources/distributed-fs/ceph-client/tools/tracing/rtla/example/timerlat_bpf_action.c

## Purpose
This is a minimal BPF action program example for RTLA timerlat. It demonstrates the required `action_handler` symbol that can be tail-called by the main timerlat BPF program when a latency threshold is hit.

## Important APIs, Types, and Functions
The file defines a GPL license section, a CO-RE-compatible `struct trace_event_raw_timerlat_sample` with `timer_latency`, and `SEC("tp/timerlat_action") int action_handler(...)`. The handler calls `bpf_printk()` with the latency value and returns zero.

## Control Flow
There is no userspace control flow. When loaded and registered through `timerlat_load_bpf_action_program()`, the main RTLA BPF program tail-calls this handler from its threshold path.

## State and Persistence
The program stores no state. Its only side effect is BPF trace output via `bpf_printk()`.

## Dependencies and Integration Points
It depends on clang BPF compilation, BPF helper headers, libbpf loading, and the userspace requirement that the object contain a program named `action_handler`.

## Risks and Edge Cases
The tracepoint section name is example-specific; the actual registration is through a `PROG_ARRAY`, so the function name is more important to the loader than normal auto-attachment. `bpf_printk()` is useful for demonstration but can be noisy and inappropriate for production threshold actions.

## Test Signals
Build via `make examples`, run RTLA timerlat with `--on-threshold`/BPF action support, and confirm BPF verifier acceptance plus expected `bpf_printk()` output.
