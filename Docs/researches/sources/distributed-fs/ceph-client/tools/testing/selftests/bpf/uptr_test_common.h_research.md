<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/uptr_test_common.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/uptr_test_common.h

## Purpose
`uptr_test_common.h` defines shared BTF-visible data structures for tests of user pointers (`__uptr`) and kernel pointers (`__kptr`) in BPF map values.

## Important APIs, Types, And Functions
- Constants `MAGIC_VALUE` and `PAGE_SIZE` support validation and large-object sizing.
- Under `__BPF__`, dummy pointer globals force or suppress specific forward BTF type generation behavior.
- For non-BPF builds, `__uptr` and `__kptr` are empty macros to keep user-space compilation valid.
- Structures include `user_data`, `nested_udata`, `value_type`, `value_lock_type`, `large_data`, `large_uptr`, `empty_data`, `empty_uptr`, and `kstruct_uptr`.

## Control Flow
The header defines types only. BPF programs use these types in maps and helper calls; user space allocates or inspects compatible data.

## State And Persistence
No storage persists except dummy BPF globals under `__BPF__` and map values in consuming tests.

## Dependencies And Integration Points
It integrates BPF-side C compilation, BTF type emission, map value layout, spin locks, cgroup kptr/uptr tests, and user-space validation code elsewhere.

## Risks And Edge Cases
The empty `struct empty_data` and one-page `large_data` are intentional edge cases for verifier/BTF handling. Layout and annotations are the core test ABI; changing them invalidates expected verifier behavior.

## Test Signals
Consumers should observe correct verifier acceptance/rejection and expected data reads/writes through uptr/kptr fields, including nested, locked, large, empty, and kernel-struct pointer cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/uptr_test_common.h -->
