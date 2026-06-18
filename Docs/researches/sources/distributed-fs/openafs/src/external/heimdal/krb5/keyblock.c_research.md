# sources/distributed-fs/openafs/src/external/heimdal/krb5/keyblock.c

Purpose: manages `krb5_keyblock` initialization, copying, access, and secure-ish cleanup.

Important APIs/types/functions: `krb5_keyblock_zero()`, `krb5_free_keyblock_contents()`, `krb5_free_keyblock()`, `krb5_copy_keyblock_contents()`, `krb5_copy_keyblock()`, `krb5_keyblock_get_enctype()`, and `krb5_keyblock_init()`.

Control flow: initialization verifies requested key size with `krb5_enctype_keysize()`, copies caller bytes into a new `krb5_data`, and sets keytype. Freeing wipes key bytes with `memset()`, frees the data, and resets keytype to `KRB5_ENCTYPE_NULL`. Copying delegates content copying to generated ASN.1 copy helpers.

State and persistence behavior: no global state. Key bytes are heap-owned by the keyblock and remain until explicit free. Free content wipes current bytes before release.

Dependencies and integration points: used by crypto initialization, random key generation, derived-key caching, and external callers constructing keys. Depends on `krb5_data_*`, `copy_EncryptionKey()`, and enctype metadata from `crypto.c`.

Risks: wiping via `memset()` may be optimized out by some compilers unless the broader build guarantees secure memset behavior. `krb5_keyblock_init()` returns `KRB5_PROG_ETYPE_NOSUPP` for bad size, which conflates size and unsupported-type errors.

Test signals: correct size enforcement per enctype, copy independence, free zeroing behavior under instrumentation, and null-safe free calls.
