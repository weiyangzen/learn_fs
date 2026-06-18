# sources/distributed-fs/ceph-client/include/linux/tracepoint-defs.h

## Purpose
Provides lightweight tracepoint structure definitions for code that needs tracepoint keys or print flag tables without including the full tracepoint macro system.

## Important APIs, Types, And Functions
Defines `struct trace_print_flags`, `struct trace_print_flags_u64`, `struct tracepoint_func`, `struct tracepoint_ext`, `struct tracepoint`, `tracepoint_ptr_t`, `struct bpf_raw_event_map`, `DECLARE_TRACEPOINT()`, and `tracepoint_enabled()`.

## Control Flow
The only inline-like behavior is `tracepoint_enabled()`, which checks the tracepoint static key when tracepoints are configured and returns false otherwise. Full probe iteration and registration are in `tracepoint.h` and tracing core.

## State, Persistence, And Dependencies
`struct tracepoint` stores name, static key, static call metadata, iterator/probestub pointers, RCU-protected function array, and optional extension flags such as `faultable`. Dependencies are atomic and static-key infrastructure.

## Integration Points
Used by headers that need safe `tracepoint_enabled()` guards before calling out-of-line trace wrappers, and by BPF raw tracepoint registration through `bpf_raw_event_map`.

## Risks And Test Signals
Risks include calling tracepoints directly from headers causing bloat or side effects, failing to guard out-of-line calls, and bad alignment of BPF maps. Test signals include disabled tracepoint branch behavior, header-only users compiling without full tracepoint macros, and BPF raw tracepoint metadata validation.
