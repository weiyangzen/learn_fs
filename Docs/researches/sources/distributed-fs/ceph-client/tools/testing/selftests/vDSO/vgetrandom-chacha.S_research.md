<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vgetrandom-chacha.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vgetrandom-chacha.S

## Purpose
Assembly dispatcher that includes the architecture-specific vgetrandom ChaCha implementation for the chacha selftest.

## Important APIs, Types, and Functions
__ASSEMBLY__ and conditional #include of arch/*/vgetrandom-chacha.S.

## Control Flow
At assembly preprocessing time, selects the arch implementation for arm64, loongarch, powerpc, riscv64, s390x, or x86_64; unsupported architectures compile without a strong implementation, leaving the weak skip path.

## State and Persistence
No runtime state in this wrapper.

## Dependencies and Integration Points
Depends on source-tree relative arch assembly paths and architecture predefines.

## Risks and Edge Cases
Path drift or unsupported architecture causes missing implementation and skipped chacha test.

## Test Signals
Build/link of vdso_test_chacha plus runtime comparison validates inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/vgetrandom-chacha.S -->
