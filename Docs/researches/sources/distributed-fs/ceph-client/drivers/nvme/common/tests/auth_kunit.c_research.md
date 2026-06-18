# sources/distributed-fs/ceph-client/drivers/nvme/common/tests/auth_kunit.c

Purpose: Provides KUnit coverage for NVMe authentication TLS PSK derivation helper paths using fixed vectors for SHA-256, SHA-384, and SHA-512 behavior.

Important APIs and flow: `test_nvme_auth_derive_tls_psk()` builds deterministic `skey`, `c1`, and `c2`, calls `nvme_auth_generate_psk()`, validates the generated PSK, calls `nvme_auth_generate_digest()`, and then calls `nvme_auth_derive_tls_psk()` when a digest is expected. Individual test cases supply expected vectors for SHA-256 and SHA-384; SHA-512 expects digest generation to fail with `-EINVAL`.

State and persistence behavior: No persistent state. Per-test allocations for PSK, digest, and TLS PSK are registered with KUnit cleanup actions.

Dependencies and integration points: Depends on KUnit, SHA digest sizes, `linux/nvme-auth.h`, and the exported common auth helpers.

Risks and test signals: The tests primarily cover TLS PSK derivation and do not cover key parsing, DH KPP, or host handshake sequencing. They are useful regression signals for spec-vector changes, SHA-512 unsupported behavior, allocation cleanup, and digest formatting.
