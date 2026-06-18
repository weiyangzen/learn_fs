# sources/distributed-fs/ceph-client/samples/bpf/spintest.bpf.c

Purpose: BPF tracing sample that counts stack traces or instruction pointers around spinlock-related functions.

Important APIs/types/functions: maps for counts and stacks, macro `PROG(foo)` defining kprobe handlers, and probes for `spin_*lock*`, `*_spin_on_owner`, `_raw_spin_*lock*`, and selected hash map functions.

Control flow: each kprobe handler records `PT_REGS_IP(ctx)`, looks up a counter, initializes or increments it, and may collect stack IDs depending on map usage.

State and persistence: BPF maps hold counts and stack trace data while attached.

Dependencies and integration: loaded by `spintest_user.c`, depends on kprobe multi support for wildcard sections and trace helper symbolization.

Risks: wildcard kprobe availability varies by kernel. Probing hot spinlock paths can add overhead. Symbol names differ with config/compiler.

Test signals: attach links for all available programs, run workload, and see nonzero counts symbolized by the user program.
