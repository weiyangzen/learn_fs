<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_value_or_null.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_value_or_null.c

## Purpose
This verifier test suite validates nullable map value pointer identity, null-check propagation, and rejection of arithmetic or unsafe access on `PTR_TO_MAP_VALUE_OR_NULL` values.

## Important APIs, Types, and Functions
It defines both `map_hash_48b` and `map_hash_8b`. Programs use `bpf_map_lookup_elem` and, in one state-frequency test, `bpf_ktime_get_ns`. Annotations declare success/failure outcomes across tc, socket, and cgroup/skb program types.

## Control Flow
The first test copies a lookup result to another register, null-checks one copy, and writes through the other to prove shared ID propagation. Several tests mutate the copied nullable pointer using add, bitwise AND, or shift before the null check and expect rejection. Other tests perform multiple lookup calls to show that a null check on one result does not validate an older independent result. Later cases test bounded map index logic from an else branch, branch prediction over contradictory null checks, and `regsafe()` behavior when two nullable map values may or may not share an ID.

## State and Persistence
Map values can be written, but persistent state is not the goal. The relevant state is verifier ID equivalence for nullable pointers, branch-derived nullability, and state merging under `BPF_F_TEST_STATE_FREQ`.

## Dependencies and Integration Points
The file integrates with the verifier harness through `bpf_misc.h` annotations and uses multiple program types to exercise type-specific verifier paths.

## Risks
Verifier ID propagation and state pruning behavior are complex and can change as verifier precision improves. Log messages and state-frequency behavior are particularly sensitive.

## Test Signals
Expected success for shared checked lookup copies, failure for arithmetic on nullable pointers, failure for stale unchecked lookup access, and failure in the `check_ids()`/`regsafe()` scenario are the core signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_value_or_null.c -->
