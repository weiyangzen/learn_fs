# sources/distributed-fs/ceph-client/security/integrity/evm/Kconfig

Purpose: defines Extended Verification Module configuration for protecting file security xattrs with HMACs or signatures.

Important APIs, types, and functions: symbols include `EVM`, `EVM_ATTR_FSUUID`, `EVM_EXTRA_SMACK_XATTRS`, `EVM_ADD_XATTRS`, `EVM_LOAD_X509`, and `EVM_X509_PATH`.

Control flow: enabling `EVM` selects key, encrypted-key, HMAC, SHA1, hash-info, and security path dependencies. Optional symbols alter HMAC material, allow runtime protected-xattr extension, and load an X.509 cert into `.evm`.

State and persistence: no direct runtime state, but options affect persistent EVM labels: changing FSUUID or extra xattr participation requires relabeling existing filesystems.

Dependencies and integration: integrates with integrity keyrings, encrypted keys, crypto, security xattrs, Smack, and securityfs.

Risks and test signals: HMAC input changes are backward-incompatible with existing labels. Test signals are config builds and EVM validation across FSUUID, Smack extra xattrs, runtime xattr list, and X.509 load configurations.
