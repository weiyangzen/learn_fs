# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_crypto.c

## Purpose
`gss_krb5_crypto.c` implements Kerberos 5 cryptographic helpers used by RPCSEC_GSS wrap/MIC paths. It handles confounder generation, checksum/HMAC calculation over `xdr_buf`, CBC plus ciphertext stealing encryption/decryption, RFC 3962/6803 checksum-then-encrypt payloads, and RFC 8009 encrypt-then-MAC payloads.

## Important APIs, Types, and Functions
Public/internal exports include `krb5_make_confounder()`, `krb5_encrypt()`, `gss_krb5_checksum()`, `xdr_extend_head()`, `krb5_cbc_cts_encrypt()`, `krb5_cbc_cts_decrypt()`, `gss_krb5_aes_encrypt()`, `gss_krb5_aes_decrypt()`, `krb5_etm_checksum()`, `krb5_etm_encrypt()`, and `krb5_etm_decrypt()`. Descriptor types `encryptor_desc` and `decryptor_desc` accumulate up to four scatterlist fragments while processing an XDR buffer.

## Control Flow
MIC calculation initializes a keyed ahash, processes the XDR body first, optionally appends the token header, finalizes the digest, and truncates to the enctype checksum length. CBC-CTS encryption processes all but the last two blocks with CBC across scatter/gather fragments, then handles the remainder in a temporary contiguous buffer through the CTS transform. Decryption mirrors this. AES-SHA1/Camellia wrap inserts a confounder after the token header, copies the plaintext header into the trailer, computes HMAC over plaintext, encrypts, and appends the HMAC. RFC 8009 wrap inserts the confounder, encrypts first, then computes HMAC over zero IV plus ciphertext before appending it. Decrypt paths select initiator or acceptor keys based on direction, verify HMAC, decrypt as appropriate, and return head/tail skip sizes for unwrap trimming.

## State and Persistence
The file does not persist state outside caller-provided `krb5_ctx`, crypto transforms, and `xdr_buf` mutation. Sensitive temporary key or digest material is freed with `kfree_sensitive()` where applicable. `xdr_extend_head()` mutates head iovec length and total buffer length in place.

## Dependencies and Integration Points
It depends on the kernel crypto API (`skcipher`, `ahash`, `shash` indirectly through callers), XDR buffer iteration, scatterlists, pages, highmem/pagemap helpers, random bytes, and Kerberos enctype metadata from `gss_krb5_internal.h`. It is called from `gss_krb5_wrap_v2()`/`unwrap_v2()` and MIC seal/unseal code.

## Risks and Edge Cases
Buffer layout is the main risk: page-cache plaintext pages must not be encrypted in place, so send paths swap in scratch pages for output while reading real pages for HMAC. The scatterlist fragment limit is enforced with `BUG_ON(desc->fragno > 3)`. `xdr_extend_head()` assumes sufficient RPC auth slack and uses `BUG_ON` if a shift exceeds `RPC_MAX_AUTH_SIZE`. HMAC comparisons use `crypto_memneq()` to avoid timing leaks. RFC 8009 validates integrity before decrypting, reducing exposure to malformed ciphertext compared with older enctypes.

## Test Signals
KUnit exports cover `gss_krb5_checksum()`, CBC-CTS encrypt/decrypt, and `krb5_etm_checksum()`. `gss_krb5_test.c` validates RFC 3962 encryption vectors, RFC 6803 checksum/encryption vectors, RFC 8009 checksum/encryption vectors, and encrypt/decrypt round trips across all compiled enctypes.
