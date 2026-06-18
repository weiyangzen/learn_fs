<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_value.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_value.c

## Purpose
This verifier suite tests map value pointer handling: use of cleared call registers, unaligned loads/stores under `BPF_F_ANY_ALIGNMENT`, and preservation of adjusted map value pointers across stack spilling.

## Important APIs, Types, and Functions
It defines `struct test_val { unsigned int index; int foo[MAX_ENTRIES]; }` and `map_hash_48b`, a hash map whose value is that structure. All programs use `bpf_map_lookup_elem`; test annotations from `bpf_misc.h` declare expected privileged and unprivileged outcomes.

## Control Flow
Each naked socket program initializes a stack key, looks up `map_hash_48b`, null-checks the returned value pointer, and then performs the operation under test. Cases store a cleared call register back into a map value, perform deliberately unaligned 64-bit accesses around adjusted map value offsets, and spill/reload an adjusted pointer to verify that verifier bounds and pointer identity are retained.

## State and Persistence
Runtime writes target map value memory, but persistence is incidental to verifier validation. The important state is verifier knowledge of map value bounds, pointer adjustment, stack spill metadata, and whether a pointer may be leaked to unprivileged code.

## Dependencies and Integration Points
The file integrates with libbpf skeleton-style map declarations and BPF verifier selftests. `offsetof(struct test_val, foo)` is passed as an immediate to validate adjusted access within the map value.

## Risks
Unaligned access behavior depends on `BPF_F_ANY_ALIGNMENT` and architecture/verifier policy. Unprivileged expectations include pointer leak diagnostics, so verifier error wording changes can affect tests.

## Test Signals
Signals include success for privileged unaligned/preserved pointer cases, `R1 !read_ok` for storing an unreadable cleared call register, and unprivileged pointer leak rejections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_value.c -->
