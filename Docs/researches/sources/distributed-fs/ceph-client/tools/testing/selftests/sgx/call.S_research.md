# sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/call.S

## Purpose
Provides `sgx_enter_enclave`, an assembly wrapper around the vDSO `__vdso_sgx_enter_enclave` entry point that preserves callee-saved registers for unclobbered-call tests.

## Important APIs, types, and functions
Exports global symbol `sgx_enter_enclave`. It references `vdso_sgx_enter_enclave` through RIP-relative addressing and follows the x86_64 calling convention plus the SGX vDSO extra stack arguments.

## Control flow
The wrapper pushes `r15`, `r14`, `r13`, `r12`, and `rbx`, prepares two stack slots expected by the vDSO call path, calls the function pointer, then restores stack and registers before returning.

## State and persistence
No persistent state. Runtime state is the user register frame and stack frame around the vDSO call.

## Dependencies and integration points
Linked into `test_sgx` and used by `ENCL_CALL(..., clobbered=false)` in `main.c`. Requires `main.c` to resolve `vdso_sgx_enter_enclave`.

## Risks
Any ABI mismatch with the vDSO prototype or stack layout can corrupt register state or mis-enter the enclave. The wrapper is x86_64-specific.

## Test signals
The `unclobbered_vdso` tests verify this path by entering the enclave, writing a magic value, reading it back, and expecting clean `EEXIT`.
