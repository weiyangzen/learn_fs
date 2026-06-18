# sources/distributed-fs/ceph-client/tools/testing/ktest/examples/bootconfigs/verify-functiongraph.sh

Purpose: verifies a bootconfig scenario that enables function-graph tracing bounded by kprobe triggers.

Important APIs, types, and functions: helper functions match the boottrace verifier. Assertions check `tracing_on`, `current_tracer`, kprobe start/end event enables and triggers, and `kprobe_events` entries targeting `pci_proc_init`.

Control flow: changes to tracefs, defines helpers, checks that tracing starts off with `function_graph`, that a start kprobe has `traceon`, that an end return probe has `traceoff`, and exits 0 on success or 1 on first mismatch.

State and persistence: read-only verification of tracefs state.

Dependencies and integration points: requires tracefs, kprobe events, function_graph tracer, and a bootconfig that created `start_event` and `end_event`.

Risks: string and regex expectations are tightly coupled to tracefs output formatting and symbol naming. It assumes `/sys/kernel/tracing` exists.

Test signals: successful exit confirms the expected boot-time function graph setup is active and bounded by kprobe triggers.
