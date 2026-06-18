# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/pkcs7_trust.c

Purpose: validates that a verified PKCS#7 signature chain intersects a trusted keyring, returning policy-aware trust results after cryptographic verification has linked internal chains.

Important APIs/types/functions: `pkcs7_validate_trust_one()` walks a signed info's signer chain, searches the trust keyring with `find_asymmetric_key()`, verifies the relevant signature with the trusted key, and caches verified certificates. `pkcs7_validate_trust()` iterates signed infos and prioritizes return codes across `-ENOKEY`, `-ENOPKG`, success, and hard failures.

Control flow: for each signer, the code walks from leaf signer to root, checking whether any certificate is already trusted. If no embedded certificate matches, it tries the root's authority IDs against trusted keys, then tries direct signed-info signer IDs. A matched key must verify either an embedded certificate signature or the signed-info signature. Success marks certificates from leaf to the trusted intersection as verified.

State and persistence: trust validation mutates in-memory `seen` and `verified` flags in embedded X.509 certificates and reads signed-info `unsupported_crypto`. No keyring state is modified.

Dependencies and integration points: depends on asymmetric key search, public-key signature verification, PKCS#7 internal structures, and caller-supplied trust keyrings such as builtin, secondary, or platform keyrings.

Risks: trust depends on correct key-id matching and verifying the trusted variant can validate the descendant signature. Cached `seen`/`verified` state must be reset appropriately before validation. Direct signed-info fallback is useful but security-sensitive.

Test signals: chains trusted at leaf, intermediate, and root; unknown self-signed roots; direct signer keys; unsupported crypto; signature failure with matched trusted key; multi-signer messages where one chain succeeds.
