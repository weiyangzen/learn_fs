# sources/distributed-fs/ceph-client/include/crypto/null.h

Purpose: defines sizes for null crypto algorithms.

Important APIs, types, and flow: constants specify zero key size, one-byte block size, zero digest size, and zero IV size for null cipher/hash behavior.

State and persistence: no state.

Dependencies and integration: used by null algorithm implementations, crypto tests, and templates that need identity transforms.

Risks and test signals: risks are mostly callers assuming nonzero digest/IV/key sizes. Signals include null cipher/hash self-tests, template composition tests, and boundary tests for zero-length digest/key handling.
