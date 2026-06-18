# sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/main.h

## Purpose
Declares shared host-side SGX data structures and function prototypes used across enclave loading, measuring, building, signing, and entry.

## Important APIs, types, and functions
`struct encl_segment` records source pointer, enclave offset, size, VMA protections, SGX flags, and measurement participation. `struct encl` owns the SGX fd, mapped binary, source/enclave sizing, base address, segment table, SECS, and SIGSTRUCT. Prototypes expose `encl_delete()`, `encl_load()`, `encl_measure()`, `encl_build()`, `encl_get_entry()`, and `sgx_enter_enclave()`. It also exports the embedded signing key range.

## Control flow
This header has no runtime flow but defines the object passed from `load.c` to `sigstruct.c` and `main.c`.

## State and persistence
`struct encl` is the central in-memory state container for one test enclave lifetime.

## Dependencies and integration points
Includes SGX UAPI types through `defines.h`; integrates assembly symbols from `sign_key.S` and `call.S`.

## Risks
Struct fields mix file offsets, sizes, pointers, and enclave virtual addresses; wrong units or truncation would break SGX ioctls. `off_t encl_base` stores an address and therefore assumes sufficient width.

## Test signals
All SGX tests validate this contract indirectly through setup and cleanup behavior.
