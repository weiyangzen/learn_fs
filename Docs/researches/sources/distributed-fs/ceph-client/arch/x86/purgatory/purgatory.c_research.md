<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/purgatory/purgatory.c -->
# sources/distributed-fs/ceph-client/arch/x86/purgatory/purgatory.c

## Purpose
Verifies the SHA-256 digest of kexec image segments before transferring control to the next kernel.

## Important APIs, Types, And Functions
`purgatory_sha256_digest` and `purgatory_sha_regions` are patched by the kexec loader. `verify_sha256_digest()` computes SHA-256 over each listed region. `purgatory()` loops forever if verification fails. `warn()` is a stub for freestanding code.

## Control Flow
At purgatory runtime, the code hashes every nonzero region, compares against the expected digest, and returns only on success. On mismatch it spins, preventing execution of a corrupted image.

## State And Persistence
Digest and region arrays are in the `.kexec-purgatory` section and patched per kexec image. No OS services are available.

## Dependencies And Integration Points
Uses freestanding SHA-256 and string/memcmp support built into purgatory. Integrated with kexec file loading and relocation.

## Risks And Edge Cases
No logging is available because `warn()` is empty. Region list termination and digest patching must be exact. A false mismatch hangs the kexec transition.

## Test Signals
Successful kexec with valid image, deliberate digest-corruption tests that halt, and correct SHA region patching validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/purgatory/purgatory.c -->
