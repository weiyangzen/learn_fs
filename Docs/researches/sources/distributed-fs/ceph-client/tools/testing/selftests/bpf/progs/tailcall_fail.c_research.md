<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_fail.c

Purpose: Negative verifier tests for tail calls in forbidden critical regions or with live references.

Important APIs/types/functions: Defines private spin lock, `jmp_table`, and optional tc programs annotated with failures for spin lock, RCU lock, preempt-disable, and reference leak cases.

Control flow: Each program enters a forbidden state then attempts `bpf_tail_call_static`; one allocates an object and tail-calls before dropping it.

State and persistence: No successful runtime state expected; the private lock and prog-array exist only for verifier setup.

Dependencies and integration: Depends on verifier lock/RCU/preempt/reference-state checks.

Risks: Accepting any program would allow tail calls to escape cleanup/critical-section constraints.

Test signals: Expected signals are exact annotated verifier messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_fail.c -->
