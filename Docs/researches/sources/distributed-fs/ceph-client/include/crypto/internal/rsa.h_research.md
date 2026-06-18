# sources/distributed-fs/ceph-client/include/crypto/internal/rsa.h

Purpose: declares RSA key parsing structures, setkey helper behavior, and RSA template symbols.

Important APIs, types, and flow: `struct rsa_key` stores pointers and sizes for modulus, exponents, CRT factors, and coefficient fields parsed from encoded keys. `rsa_parse_pub_key()` and `rsa_parse_priv_key()` decode public/private keys into that structure. `rsa_set_key()` selects public or private setkey on a child akcipher, queries the resulting modulus size with `crypto_akcipher_maxsize()`, rejects sizes above `PAGE_SIZE`, and publishes the key size. `rsa_pkcs1pad_tmpl` and `rsassa_pkcs1_tmpl` are template exports.

State and persistence: parsed key pointers refer to the caller's encoded key buffer; child transforms own parsed key state after setkey. No persistence exists.

Dependencies and integration: depends on `crypto/akcipher.h` and internal akcipher behavior. It integrates RSA base implementations with PKCS#1 encryption/signature templates.

Risks and test signals: risks include encoded key lifetime, oversized modulus rejection, incomplete CRT field validation, and public/private setkey mixups. Signals include DER key parse tests, RSA encrypt/decrypt/sign/verify vectors, oversized key rejection, invalid CRT fields, and template self-tests.
