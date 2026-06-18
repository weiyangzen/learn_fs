# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/vgetrandom.c

## Purpose
Provides the PowerPC C wrapper that exposes generic vDSO getrandom logic to the assembly vDSO entry point.

## Important APIs, Types, And Functions
Defines `__c_kernel_getrandom(void *buffer, size_t len, unsigned int flags, void *opaque_state, size_t opaque_len)`, returning `ssize_t` from `__cvdso_getrandom`.

## Control Flow
The assembly wrapper calls this C helper with user arguments. The helper directly delegates to the generic vDSO getrandom implementation, which decides whether it can satisfy the request in userspace or must fall back.

## State And Persistence
No local state. The generic helper may read vvar random state and update caller-provided opaque state and output buffer.

## Dependencies And Integration Points
Depends on the generic getrandom implementation included by the vDSO Makefile and on `getrandom.S` for ABI framing and error conversion. The ChaCha20 primitive is supplied by `vgetrandom-chacha.S`.

## Risks And Edge Cases
This file is intentionally thin, so most risk is in included generic code and assembly ABI glue. The signature must remain exactly matched to the assembly caller and generic helper expectations.

## Test Signals
vDSO getrandom selftests for flags, buffer lengths, opaque-state sizes, fallback behavior, and 32-bit/64-bit ABI execution cover this file.
