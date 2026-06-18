# sources/distributed-fs/ceph-client/tools/testing/ktest/examples/bootconfigs/verify-tracing.sh

Purpose: verifies a general tracing bootconfig setup, including global tracer options, event enables, kprobe instances, and kernel sysctls.

Important APIs, types, and functions: same helper assertion functions as the other bootconfig verifiers. Checks `function_graph`, `event-fork`, `sym-addr`, `stacktrace`, buffer size, snapshot, trace clock, initcall/task/sched/kprobe events, instance `bar` kprobe events, instance `foo` state, and proc sysctls `ftrace_dump_on_oops` and `traceoff_on_warning`.

Control flow: changes to tracefs and performs exact/partial/contains assertions in sequence, exiting 1 on failure and 0 on success.

State and persistence: reads tracefs and procfs only.

Dependencies and integration points: requires tracing bootconfig support, tracefs, kprobes, function_graph tracer, snapshots, and the expected proc sysctl state.

Risks: exact-value checks can fail due to kernel output changes even when semantics are equivalent. Hard-coded buffer sizes and clocks assume the example bootconfig and architecture behavior.

Test signals: exit 0 means the tracing bootconfig applied expected global and instance-specific tracing state.
