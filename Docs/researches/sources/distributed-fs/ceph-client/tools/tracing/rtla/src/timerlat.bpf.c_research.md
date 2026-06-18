# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat.bpf.c

## Purpose
`timerlat.bpf.c` is the eBPF program used by RTLA timerlat to collect timer latency histograms and summary statistics in-kernel and to signal userspace when configured latency thresholds are reached.

## Important APIs, Types, and Functions
The program defines per-CPU array maps for IRQ/thread/user histograms and summaries, a `stop_tracing` array flag, a `signal_stop_tracing` ring buffer, and a `bpf_action` program array for optional threshold tail calls. Read-only configuration variables include `bucket_size`, `output_divisor`, `entries`, `irq_threshold`, `thread_threshold`, and `aa_only`. Helpers update map values, histograms, summaries, and stop state. The main program is `SEC("tp/osnoise/timerlat_sample") int handle_timerlat_sample(...)`.

## Control Flow
For each `osnoise:timerlat_sample` event, the program exits if `stop_tracing` is set, scales latency for output and threshold comparisons, computes a bucket, and branches by context: IRQ (`context == 0`), thread (`context == 1`), or user. It updates the appropriate histogram and summary maps unless disabled, checks thresholds in microseconds, and calls `set_stop_tracing()` on overflow. That function sets the stop flag, emits a ring-buffer notification, and tail-calls an optional action program.

## State and Persistence
All state is BPF map data scoped to the loaded object. The userspace side reads maps, updates the stop flag to restart, and can install an action program in the `PROG_ARRAY`.

## Dependencies and Integration Points
The program depends on BPF CO-RE tracepoint layout, libbpf skeleton generation, and `timerlat_bpf.c` userspace setup. It includes `timerlat_bpf.h` for summary field indexes.

## Risks and Edge Cases
Histogram overflow increments summary overflow but `update_main_hist()` drops bucket counts beyond `entries`; userspace must display overflow separately. `entries == 0` disables histograms. `aa_only` disables summary maps. Tail-call action failures are silent by design. Incorrect context values are treated as user context.

## Test Signals
Build skeletons with clang/bpftool, load on kernels with `osnoise:timerlat_sample`, verify map values for IRQ/thread/user samples, threshold ring-buffer wakeups, restart behavior, and optional action tail calls.
