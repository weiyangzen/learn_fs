# sources/distributed-fs/ceph-client/crypto/rsassa-pkcs1.c

Purpose: implements the `pkcs1(rsa,hash)` signature template for RSASSA-PKCS1-v1_5 signing and verification through the crypto `sig` API.

Important APIs, types, and functions: static `hash_prefix_*` arrays encode ASN.1 DigestInfo prefixes for MD5, SHA-1, RIPEMD-160, SHA-2, and SHA-3 variants. `rsassa_pkcs1_find_hash_prefix()` resolves the template hash name. `rsassa_pkcs1_sign()` and `rsassa_pkcs1_verify()` implement EMSA-PKCS1-v1_5 encoding and checking. Key setup delegates to `rsa_set_key()`.

Control flow: instance creation accepts only child `rsa` and a known hash prefix, then registers names like `pkcs1(rsa,sha256)`. Signing validates key size, output length, digest length, and encoded length, builds `0x01 FF...00 || prefix || digest` in the destination buffer, and uses RSA private operation via child decrypt. Verification checks signature length and digest length, runs RSA public operation, validates leading zero, block type, minimum FF padding, zero separator, hash prefix, and digest equality.

State and persistence: per-instance state stores the selected hash prefix and child spawn. Per-tfm state stores child RSA tfm and key size. Verification allocates a temporary child request and buffer, freed with `kfree_sensitive`.

Dependencies and integration points: registered by `rsa.c` as `rsassa_pkcs1_tmpl`; depends on akcipher, sig, hash names, scatterlists, and RSA helpers.

Risks: PKCS#1 v1.5 signatures are deterministic and legacy but still widely used. The `none` prefix supports legacy protocols and disables digest length validation, which must be used only by protocols that already define the hashed input. Prefix tables must match RFC OIDs exactly.

Test signals: sign/verify for every supported hash prefix, digest-length rejection, malformed padding rejection, leading-zero normalization, unsupported hash template rejection, public/private key setup, and interoperability with known RSA PKCS#1 v1.5 vectors.
