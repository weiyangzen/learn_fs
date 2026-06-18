# sources/distributed-fs/ceph-client/samples/bpf/spintest_user.c

Purpose: userspace loader and reporter for the spinlock tracing sample.

Important APIs/types/functions: loads BPF object, attaches each program, reads map entries, resolves symbols through `trace_helpers`, and prints counts.

Control flow: iterates BPF programs attaching them, sleeps for a requested duration or default loop, then iterates count map keys and prints symbolized IPs with counts.

State and persistence: BPF links and maps live during process execution; user state includes link array and symbol table.

Dependencies and integration: pairs with `spintest.bpf.c`, requires libbpf, kprobe permissions, and kallsyms access.

Risks: fixed link array size can be exceeded if program count grows. Some probes may fail on kernels without matching symbols. Running on hot paths can perturb performance.

Test signals: attach output shows links, map dump includes spinlock symbols with positive counts.
