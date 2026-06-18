<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta.h

Purpose: Shared Strobelight metadata BPF program body used by the small configuration wrappers; it samples stacks on `raw_tracepoint/kfree_skb` and conditionally copies thread-local integer, string, and map metadata into perf-event samples.

Important APIs/types/functions: Defines strobe value/map/config/payload/sample structs, `samples`, `stacks_0`, `stacks_1`, `sample_heap`, `strobemeta_cfgs`, TLS helpers `calc_location`, readers `read_int_var`, `read_str_var`, `read_map_var`, optional `read_var_callback`, `read_strobe_meta`, and `on_event`.

Control flow: `on_event` fetches a per-CPU sample, records pid/comm/time, resolves current task as TLS base, calls `read_strobe_meta`, alternates stack-trace maps by epoch bit, and submits the used sample prefix. Metadata reading looks up pid config, walks configured int/string/map slots through unrolled loops, no-unroll loops, or `bpf_loop`, and maintains a packed payload offset.

State and persistence: Persistent state is entirely in BPF maps and globals: per-pid metadata configs, stack trace tables, per-CPU heap sample, and perf output ring. It reads user TLS/GOT/dtv memory but does not mutate user state.

Dependencies and integration: Depends on BPF helpers for map lookup, user reads, stack ids, current task, comm, ktime, perf output, plus `bpf_compiler.h` loop pragmas and wrapper-provided `STROBE_MAX_*` constants.

Risks: Verifier-sensitive pointer arithmetic, payload bounds, TLS ABI assumptions for x86-64/aarch64, `bpf_probe_read_user_str` error casting, large loop bounds, and exact sample-size calculation are the main hazards.

Test signals: Wrapper variants should load successfully and report expected metadata, stack ids, and payload lengths; negative signals include verifier rejection for imprecise offsets or out-of-bounds payload writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta.h -->
