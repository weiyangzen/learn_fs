<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_value_adj_spill.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_value_adj_spill.c

## Purpose
This file narrows verifier coverage to map value pointer spill/fill behavior, especially whether `PTR_TO_MAP_VALUE` and `PTR_TO_MAP_VALUE_OR_NULL` states survive stack storage and reload correctly.

## Important APIs, Types, and Functions
It uses the same `struct test_val` and one-entry hash map pattern as nearby value tests. The two naked socket programs call `bpf_map_lookup_elem` and then use stack slots to spill/reload the returned pointer.

## Control Flow
`is_preserved_across_register_spilling` null-checks the lookup result, writes through it, spills it to stack, reloads into `r3`, and writes through the reloaded pointer. `is_marked_on_register_spilling` spills the nullable result before the null check, then after checking `r0` reloads from the stack and dereferences the copied pointer.

## State and Persistence
Map writes are secondary. The tested state is the verifier's stack spill record and ID propagation for nullable map value pointers through a null check.

## Dependencies and Integration Points
The programs are BPF verifier selftests using libbpf map declarations and `bpf_misc.h` annotations. They are loaded as socket programs by the verifier harness.

## Risks
Verifier state-ID and nullability logic is subtle; future verifier improvements may accept or reject with different diagnostics. Unprivileged rejections are tied to pointer-leak protection.

## Test Signals
Expected privileged success and unprivileged pointer-leak failure signal correct spill/fill tracking and conservative unprivileged policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_value_adj_spill.c -->
