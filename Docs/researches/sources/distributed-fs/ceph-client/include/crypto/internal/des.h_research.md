# sources/distributed-fs/ceph-client/include/crypto/internal/des.h

Purpose: centralizes DES and 3DES-EDE key verification rules for skcipher and AEAD implementations.

Important APIs, types, and flow: `crypto_des_verify_key()` expands a DES key with `des_expand_key()`, maps weak-key rejection to `-EINVAL` when `CRYPTO_TFM_REQ_FORBID_WEAK_KEYS` is set, and zeroizes the temporary context. `des3_ede_verify_key()` rejects collapsed 3DES keys where adjacent keys are equal, and in FIPS mode also rejects all-equal keying; wrapper helpers adapt those checks to skcipher and AEAD transforms while validating AEAD key sizes.

State and persistence: only stack-local temporary key material is used and explicitly cleared. FIPS behavior reads global `fips_enabled`.

Dependencies and integration: depends on DES constants/expansion, crypto transform flags, AEAD/skcipher transform accessors, and Linux FIPS mode. DES-family implementations should call these helpers from setkey paths.

Risks and test signals: failure to call these helpers can admit weak or FIPS-forbidden keys; wrong error mapping can break callers that distinguish weak-key permission. Signals include DES/3DES weak-key vectors, FIPS-mode key rejection tests, AEAD key-length tests, and memory-sanitizer checks for zeroized temporary key schedules.
