# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_cookie.c

Purpose: broad coverage of BPF link/program cookies across kprobes, multi-kprobes, uprobes, multi-uprobes, tracepoints, perf events, trampoline links, LSM, BTF tracepoints, and raw tracepoints.

Important APIs/types/functions: uses `test_bpf_cookie.skel.h`, `kprobe_multi.skel.h`, and `uprobe_multi.skel.h`. Helpers attach with cookie-bearing option structs: `bpf_kprobe_opts`, `bpf_kprobe_multi_opts`, `bpf_uprobe_opts`, `bpf_uprobe_multi_opts`, `bpf_tracepoint_opts`, `bpf_perf_event_opts`, `bpf_link_create_opts`, `bpf_raw_tp_opts`, `bpf_trace_opts`, and `bpf_raw_tracepoint_opts`. `verify_tracing_link_info` and `verify_raw_tp_link_info` read cookie fields from `bpf_link_info`.

Control flow: top-level loads the cookie skeleton, stores current TID, then runs subtests. Single kprobe/uprobe tests attach duplicate probes with different cookies and assert ORed BSS results after trigger. Multi-kprobe tests use low-level link create by resolved addresses and high-level symbol attach APIs, then run a trigger program. Multi-uprobe attaches symbols in `/proc/self/exe` and triggers local functions. Tracepoint tests detach/reattach to ensure cookies survive prog-array reshuffling. Perf-event test reattaches on the same perf FD after disconnecting a link. Trampoline, LSM, tp_btf, and raw_tp tests create links with cookies, trigger, and verify BSS plus link info.

State and persistence behavior: BSS fields accumulate observed cookies. Link FDs/pointers own attachment lifetime and are explicitly destroyed/closed. Perf event FD is reused across link lifetimes. Some tests depend on testmod symbols and current process executable symbols.

Dependencies and integration points: depends on libbpf attach APIs, BPF link create, perf_event_open, kallsyms/testmod, `network_helpers.h` for `sys_gettid`, executable symbol availability, and `stack_mprotect` helper for LSM trigger.

Risks: high environmental sensitivity: testmod, tracepoint availability, perf permissions, LSM hook support, and CPU affinity for perf triggering. Cookie expectations are exact constants; link-info struct layout must match kernel support. Long CPU burn loops can be slow.

Test signals: BSS cookie fields equal expected bitwise OR or exact cookie values, link-info cookie fields match, expected `EPERM` from LSM-protected `stack_mprotect`, and successful attach/detach/reuse paths.
