# sources/distributed-fs/ceph-client/include/linux/purgatory.h

Purpose: declares global purgatory symbols used by kexec to verify loaded segments before jumping to a new kernel.

Important APIs and types: `struct kexec_sha_region` describes a memory range with start and length. `purgatory_sha_regions[KEXEC_SEGMENT_MAX]` and `purgatory_sha256_digest[SHA256_DIGEST_SIZE]` are externally visible symbols required for kexec symbol lookup and sparse checking.

Control flow: kexec code populates SHA regions and expected digest in the purgatory image; purgatory code computes/verifies the digest before transfer to the next kernel.

State and persistence: the arrays are part of the loaded purgatory/kexec image state for a pending kexec operation. They do not persist beyond boot transition.

Dependencies and integration points: depends on crypto SHA-256 constants and UAPI kexec segment limits. Integrates generic kexec loading with architecture purgatory code.

Risks and test signals: risks include symbol visibility changes breaking kexec relocation, wrong segment count/lengths, digest mismatch handling, and sparse/build drift in arch purgatory. Test kexec load/execute, corrupted segment detection, max segment counts, and architecture purgatory builds.
