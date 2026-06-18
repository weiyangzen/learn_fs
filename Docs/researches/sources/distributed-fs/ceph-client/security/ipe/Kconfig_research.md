# sources/distributed-fs/ceph-client/security/ipe/Kconfig

Purpose: Defines build-time configuration for the Integrity Policy Enforcement LSM and its optional trust providers/tests.

Important APIs/types/functions: `SECURITY_IPE` enables the LSM and selects crypto, PKCS#7, system verification, securityfs, audit, and optional dm-verity/fs-verity provider symbols. Other options include `IPE_BOOT_POLICY`, secondary/platform keyring policy signature verification, dm-verity root hash/signature properties, fs-verity digest/builtin signature properties, and `SECURITY_IPE_KUNIT_TEST`.

Control flow: Kconfig dependency/select relationships determine which LSM blob fields, property evaluators, integrity hooks, and parser tests compile.

State and persistence: No runtime state; `IPE_BOOT_POLICY` embeds an initial policy into generated source.

Dependencies and integration: Ties IPE to LSM, securityfs, audit, auditable syscalls, cryptographic verification, dm-verity, fs-verity, trusted keyrings, and KUnit.

Risks and test signals: Build matrix risk is high because property code is config-gated. Test signals are allmodconfig/allyesconfig/minimal builds and KUnit parser coverage with each provider combination.
