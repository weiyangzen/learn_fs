<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/purgatory/purgatory.c -->
# sources/distributed-fs/ceph-client/arch/s390/purgatory/purgatory.c

Purpose: This freestanding C file verifies the SHA-256 digest of the loaded kexec image regions before the s390 purgatory transfers control to the next kernel.

Important APIs/types/functions: The sole function is `verify_sha256_digest(void)`. It uses `struct kexec_sha_region`, `struct sha256_ctx`, `purgatory_sha_regions`, `purgatory_sha256_digest`, and SHA-256 helpers.

Control flow: The function initializes SHA-256 state, iterates over all fixed-size purgatory SHA regions, hashes each region's `start`/`len`, finalizes into a local digest, compares it with the expected digest, and returns `0` for match or `1` for mismatch.

State and persistence: It owns only stack state. It reads the purgatory SHA region table, the loaded memory regions, and the expected digest prepared by kexec image setup.

Dependencies and integration points: It depends on freestanding SHA-256 code, minimal string/memcmp support, Linux kexec structure definitions, and the assembly entry in `head.S`.

Risks and test signals: The fixed array iteration includes all slots, so unused entries must have safe zero length/start data. Digest mismatch behavior is enforced by assembly, which either returns or enters disabled wait. Tests include digest success/failure, empty/unused segments, and kexec/kdump image mutation before execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/purgatory/purgatory.c -->
