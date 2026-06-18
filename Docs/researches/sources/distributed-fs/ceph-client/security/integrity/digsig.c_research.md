# sources/distributed-fs/ceph-client/security/integrity/digsig.c

Purpose: manages integrity keyrings and dispatches IMA/EVM/module digital signature verification.

Important APIs, types, and functions: static state includes `keyring[INTEGRITY_KEYRING_MAX]` and `keyring_name[]`. Public functions are `integrity_digsig_verify()`, `integrity_modsig_verify()`, `integrity_init_keyring()`, `integrity_load_x509()`, and `integrity_load_cert()`. Internal helpers are `integrity_keyring_from_id()`, `__integrity_init_keyring()`, and `integrity_add_key()`.

Control flow: verification resolves a keyring ID, examines signature version byte, and dispatches to legacy `digsig_verify()`, `asymmetric_verify()`, or `asymmetric_verify_v3()`. Keyring initialization chooses permissions/restrictions based on keyring type and trusted keyring config, sets platform/machine trust hooks, and may load module certs. Certificate loading reads DER files or accepts built-in buffers and inserts asymmetric keys.

State and persistence: keyring pointers persist globally. Loaded certificates persist in kernel keyrings. Keyring restrictions may prevent later user key insertion.

Dependencies and integration: integrates with key retention service, system trusted keyrings, IMA module signatures, platform/machine trusted key setup, kernel file reading, and asymmetric signature code.

Risks and test signals: wrong keyring restrictions can admit untrusted keys or block boot-time trust anchors. Signature version dispatch must reject short/unknown formats. Test signals include keyring allocation, trusted restriction enforcement, v1/v2/v3 signature verification, module signature verification, X.509 load success/failure, and blacklist interactions through asymmetric code.
