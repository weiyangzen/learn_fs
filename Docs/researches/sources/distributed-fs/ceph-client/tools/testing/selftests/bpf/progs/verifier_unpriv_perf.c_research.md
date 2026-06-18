<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_unpriv_perf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_unpriv_perf.c

## Purpose
This small verifier test covers unprivileged pointer type consistency for perf-event context fields. It verifies that one load instruction cannot safely read from stack slots holding different pointer classes across branches.

## Important APIs, Types, and Functions
The single naked `SEC("perf_event")` program `fill_of_different_pointers_ldx` uses `struct bpf_perf_event_data` offsets, specifically `sample_period`, through `offsetof`. It depends on `bpf_misc.h` annotations and `linux/bpf.h`.

## Control Flow
The program conditionally stores either a frame-pointer-derived stack pointer or the perf-event context pointer into a common stack slot, reloads it, then reads a field as if it were a perf-event context. The test is annotated as verifier failure with `same insn cannot be used with different pointers`.

## State and Persistence
There is no persistent map or global state. The tested state is verifier tracking of a spilled stack slot whose possible values have incompatible pointer types.

## Dependencies and Integration Points
It integrates with the BPF verifier selftest harness and the perf-event program type. The test relies on kernel UAPI definitions for `struct bpf_perf_event_data`.

## Risks
The test is sensitive to exact verifier log wording and to any verifier enhancement that changes how merged pointer types are diagnosed. Because the code is inline assembly, instruction ordering must remain stable.

## Test Signals
Expected failure with the annotated message is the key signal. A load acceptance would indicate a regression in pointer provenance enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_unpriv_perf.c -->
