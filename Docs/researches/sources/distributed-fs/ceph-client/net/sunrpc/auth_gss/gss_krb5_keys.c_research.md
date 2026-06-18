# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_keys.c

## Purpose
`gss_krb5_keys.c` implements Kerberos key derivation primitives for supported RPCSEC_GSS Kerberos enctypes. It covers RFC 3961 n-fold and DK, RFC 3962 AES random-to-key behavior, RFC 6803 Camellia CMAC feedback KDF, and RFC 8009 AES-SHA2 HMAC KDF.

## Important APIs, Types, and Functions
KUnit-visible/exported `krb5_nfold()` implements RFC 3961 n-fold. `krb5_DK()` derives raw key material by repeated encryption of a folded constant. `krb5_random_to_key_v2()` validates and copies AES random bits to a protocol key. `krb5_derive_key_v2()` composes DK plus random-to-key for RFC 3962. `krb5_cmac_Ki()` and `krb5_kdf_feedback_cmac()` implement SP800-108 feedback mode for Camellia. `krb5_hmac_K1()` and `krb5_kdf_hmac_sha2()` implement the single-block HMAC-SHA2 KDF used by RFC 8009.

## Control Flow
Kerberos context import calls `krb5_derive_key()` for each usage and seed. For AES-SHA1, derivation folds the usage constant to the cipher block size, encrypts blocks until enough bytes are available, then copies into the output key. For Camellia, the code allocates a keyed shash, iteratively computes `K(i)` from previous output, counter, constant, separator, and output bit length, concatenates blocks, and truncates. For AES-SHA2, it computes `K1 = HMAC(key, 1 | label | 0 | k)` and truncates to the requested key length.

## State and Persistence
The file owns only temporary derivation buffers and crypto transforms. Temporary raw key material, step values, and K1 buffers are released with `kfree_sensitive()`. Output keys are caller-owned `xdr_netobj`s whose length is preselected by the enctype descriptor.

## Dependencies and Integration Points
It depends on the kernel crypto API (`sync_skcipher`, `shash`), `linux/lcm.h`, Kerberos constants and enctype descriptors, and `krb5_encrypt()` from the crypto file. It feeds key material into `gss_krb5_mech.c`, which allocates per-direction encryption and checksum transforms.

## Risks and Edge Cases
Incorrect length handling would break protocol compatibility. `krb5_random_to_key_v2()` permits only 16- or 32-byte AES-style keys and rejects mismatches. The Camellia implementation notes it does not handle partial-block key sizes, acceptable for current supported enctypes but a risk if new profiles are added. Allocation failures return negative errno and must abort context import.

## Test Signals
`gss_krb5_test.c` validates n-fold against RFC 3961, Camellia Kc/Ke/Ki against RFC 6803, and AES-SHA2 Kc/Ke/Ki against RFC 8009. Tests skip unavailable enctypes via `gss_krb5_lookup_enctype()`.
