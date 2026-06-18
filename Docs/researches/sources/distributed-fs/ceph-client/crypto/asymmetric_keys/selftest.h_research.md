# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/selftest.h

Purpose: declares shared FIPS signature selftest helpers and provides configuration-dependent stubs for RSA and ECDSA vector tests.

Important APIs/types/functions: `fips_signature_selftest()` is the shared runner. `fips_signature_selftest_rsa()` and `fips_signature_selftest_ecdsa()` are declared when their configs are enabled, otherwise defined as empty `__init` inline functions.

Control flow: `selftest.c` can call both variant hooks unconditionally; the preprocessor selects real test functions or no-ops.

State and persistence: no runtime state. The header only controls linkage.

Dependencies and integration points: included by `selftest.c`, `selftest_rsa.c`, and `selftest_ecdsa.c`; depends on config symbols from asymmetric Kconfig.

Risks: prototypes must match variant definitions. Stubs prevent link failures but can also make an expected test silently absent if config is wrong.

Test signals: build with every combination of `CONFIG_FIPS_SIGNATURE_SELFTEST_RSA` and `CONFIG_FIPS_SIGNATURE_SELFTEST_ECDSA`.
