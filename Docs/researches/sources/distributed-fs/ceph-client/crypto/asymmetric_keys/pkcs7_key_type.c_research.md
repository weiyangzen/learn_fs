# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/pkcs7_key_type.c

Purpose: defines a testing key type that accepts a PKCS#7-wrapped user payload only after the PKCS#7 signature validates against trusted system keys, then exposes the unwrapped user payload.

Important APIs/types/functions: module parameter `usage` selects the `enum key_being_used_for` verification usage. `pkcs7_view_content()` temporarily substitutes PKCS#7 content data into the preparse payload and delegates to `user_preparse()`. `pkcs7_preparse()` invokes `verify_pkcs7_signature()` with `VERIFY_USE_SECONDARY_KEYRING`. `key_type_pkcs7` reuses user key instantiate, revoke, destroy, describe, and read operations.

Control flow: adding a `pkcs7_test` key runs `pkcs7_preparse()`, validates the configured usage, verifies the wrapper, and calls back into `pkcs7_view_content()` to parse the inner payload as a user key. Module init registers the test key type.

State and persistence: persistent key payload is the unwrapped user payload in the keyring. The module parameter controls runtime verification policy. No file persistence exists.

Dependencies and integration points: depends on keyrings, user key type helpers, `linux/verification.h`, and the PKCS#7 verification stack.

Risks: this is explicitly test infrastructure; the writable module parameter changes verification semantics. Temporarily mutating `prep->data` and `prep->datalen` must restore them on all paths.

Test signals: adding valid and invalid wrapped keys, each allowed `usage` value, invalid usage rejection, secondary keyring trust failures, and successful readback of only the inner payload.
