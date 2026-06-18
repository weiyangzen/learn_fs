# sources/distributed-fs/ceph-client/drivers/nvme/common/Kconfig

Purpose: Defines common NVMe support options for TLS PSK keyring, DH-HMAC-CHAP authentication helpers, and KUnit tests.

Important APIs and flow: `NVME_KEYRING` is a tristate selecting `KEYS`. `NVME_AUTH` is a tristate selecting crypto, DH, RFC7919 DH groups, and SHA libraries. `NVME_AUTH_KUNIT_TEST` depends on KUnit and NVMe auth, defaults with `KUNIT_ALL_TESTS`, and enables tests for common authentication code.

State and persistence behavior: No runtime state directly. These symbols determine whether authentication helpers, keyring code, and tests are compiled.

Dependencies and integration points: Selected by host auth and NVMe TCP TLS paths. The KUnit option builds `common/tests/auth_kunit.o`.

Risks and test signals: Config tests should cover built-in and module combinations, especially users that select keyring/auth indirectly from host options.
