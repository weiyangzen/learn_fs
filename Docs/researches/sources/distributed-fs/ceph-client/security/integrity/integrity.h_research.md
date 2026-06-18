# sources/distributed-fs/ceph-client/security/integrity/integrity.h

Purpose: Central internal header for Linux integrity subsystems, defining xattr/signature data formats, keyring ids, certificate/signature loading APIs, asymmetric verification hooks, IMA/EVM X.509 loaders, audit helpers, and platform/machine keyring entry points.

Important APIs/types/functions: Defines `enum evm_ima_xattr_type`, `struct evm_ima_xattr_data`, `struct evm_xattr`, `struct ima_digest_data`, `struct ima_max_digest_data`, `struct signature_v2_hdr`, and `struct ima_file_id`. Declares `integrity_kernel_read()`, integrityfs init/fini, `integrity_digsig_verify()`, `integrity_modsig_verify()`, `integrity_init_keyring()`, `integrity_load_x509()`, `integrity_load_cert()`, `asymmetric_verify*()`, `ima_modsig_verify()`, `integrity_audit_*()`, and platform/machine keyring loaders with stubs for disabled configs.

Control flow: Header-only configuration selects real functions or no-op/-EOPNOTSUPP stubs based on build options, allowing IMA, EVM, and platform cert code to compile under many feature combinations.

State and persistence: Defines keyring numeric ids for EVM, IMA, platform, and machine keyrings. Data structures describe persistent xattr and signature wire formats.

Dependencies and integration: Bridges integrity, audit, keyrings, asymmetric crypto, secure boot, IMA appraisal, EVM, and platform certificate import.

Risks and test signals: Risks are ABI/layout drift in packed xattr/signature structures, stale stubs masking missing functionality, and keyring id mismatches. Tests should include structure offset/static assertions, disabled-config builds, signature verification, and xattr compatibility.
