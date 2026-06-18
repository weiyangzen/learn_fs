<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/modify_return.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/modify_return.c

Purpose: tests BPF modify-return attachment behavior and interaction between input return values, side effects, and final return codes.

Important APIs and functions: `run_test()` loads `modify_return`, sets BSS/input state, attaches programs, triggers the target function path, and checks packed side-effect/return fields using `LOWER()` and `UPPER()` helpers. `test_modify_return()` runs several input/expected combinations.

Control flow: each scenario loads a fresh skeleton, attaches modify-return/fentry/fexit style programs, invokes the target, validates side effect and returned value, and destroys.

State and persistence: state is skeleton BSS/data counters and return code fields. No persistent resources remain.

Dependencies and integration: depends on `modify_return.skel.h`, trampoline/modify-return kernel support, and stable target behavior.

Risks and test signals: expected side-effect count and signed return value are signals. Risks include attach support differences and target return packing changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/modify_return.c -->
