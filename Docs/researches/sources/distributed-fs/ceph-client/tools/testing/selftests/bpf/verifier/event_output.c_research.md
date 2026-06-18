# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/event_output.c

Purpose: positive coverage for `bpf_perf_event_output` helper availability across program types using a common instruction sequence that emits an 8-byte stack payload.

Important APIs/types/functions: defines `__PERF_EVENT_INSNS__`, which stores `5` at `fp-8`, passes `ctx`, a perf-event-output map, flags `0`, data pointer, and size `8` to `BPF_FUNC_perf_event_output`, then returns `1`. Uses `.fixup_map_event_output = { 4 }`.

Control flow: ten entries reuse the same instruction macro for `SOCK_OPS`, `SCHED_CLS`, `LWT_OUT`, `XDP`, `SOCKET_FILTER`, `SK_SKB`, `CGROUP_SKB`, `CGROUP_DEVICE`, `CGROUP_SYSCTL`, and `CGROUP_SOCKOPT` with `BPF_CGROUP_SETSOCKOPT` attach type.

State and persistence behavior: transient stack payload only; successful runtime execution would emit a perf event sample through the harness-provided map. Verifier state must recognize initialized stack data and helper availability for each program type.

Dependencies and integration points: relies on perf-event-array map fixup at instruction 4. The source comment notes the sequence is embedded here, not in fill helpers, because map fixup is against static instruction indexes.

Risks: helper availability regressions for any supported program type will reject valid observability programs. Changing the macro instruction layout requires updating the fixup index.

Test signals: every entry expects `ACCEPT` with `.retval = 1`.
