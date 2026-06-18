<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gcd.h -->
# sources/distributed-fs/ceph-client/include/linux/gcd.h

Purpose: Declares the kernel greatest-common-divisor helper and a static key related to efficient find-first-set implementations.

Important APIs/types/functions: Exposes `DECLARE_STATIC_KEY_TRUE(efficient_ffs_key)` and `unsigned long gcd(unsigned long a, unsigned long b) __attribute_const__`.

Control flow: Callers invoke `gcd()` as a pure arithmetic helper. Implementation is elsewhere and may use the static key to select optimized bit operations.

State and persistence behavior: No persistent state. The static key is runtime patchable branch state.

Dependencies and integration points: Depends on compiler attributes and jump labels. Used anywhere kernel code needs an unsigned long GCD.

Risks: Inputs of zero must match implementation contract. Static-key behavior can vary by architecture feature detection.

Test signals: Kunit or simple arithmetic tests for zero, equal, coprime, powers of two, and large unsigned long values; build coverage with jump labels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gcd.h -->
