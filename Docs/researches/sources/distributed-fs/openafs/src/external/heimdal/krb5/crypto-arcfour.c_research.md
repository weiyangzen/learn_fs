# sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-arcfour.c

Purpose: implements the Kerberos RC4-HMAC/ARCFOUR enctype and HMAC-MD5 checksum variant used for Windows compatibility.

Important APIs/types/functions: `keytype_arcfour` declares the RC4 key type with EVP RC4 scheduling. `_krb5_HMAC_MD5_checksum()` computes the draft RC4-HMAC checksum. `_krb5_checksum_hmac_md5` exports the checksum descriptor. `ARCFOUR_subencrypt()` and `ARCFOUR_subdecrypt()` implement checksum, confounder/data encryption, and integrity verification. `_krb5_usage2arcfour()` remaps selected Kerberos key usages. `ARCFOUR_encrypt()` dispatches encrypt/decrypt, `ARCFOUR_prf()` implements a SHA1-HMAC based PRF, and `_krb5_enctype_arcfour_hmac_md5` exports the enctype.

Control flow: encryption derives K1 from usage, copies it to K2, computes HMAC over confounder plus plaintext into the first 16 bytes, derives K3 from that checksum, and RC4-encrypts the remaining bytes. Decryption derives K3 from the received checksum, decrypts, recomputes the HMAC, and uses `ct_memcmp()` for integrity.

State and persistence behavior: no module-global mutable state beyond descriptors. Temporary HMAC keys are stack buffers and are zeroed before return in the subencrypt/subdecrypt paths.

Dependencies and integration points: uses generic `_krb5_internal_hmac()`, `_krb5_find_checksum()`, EVP MD5/SHA1/RC4, `ct_memcmp()`, and special-mode dispatch in `crypto.c` through the `F_SPECIAL` flag.

Risks: RC4 and MD5 are legacy algorithms. The code assumes ciphertext length includes a 16-byte checksum and does not independently guard every underflow at the algorithm boundary, relying on `crypto.c` size checks. Several internal HMAC failures call `krb5_abortx()`. Usage remapping is compatibility-critical.

Test signals: RC4-HMAC known-answer vectors, bad checksum rejection, usage remap cases for AS-REP, seal/sign/seq, and encryption/decryption with minimum legal lengths.
