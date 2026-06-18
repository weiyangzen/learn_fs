# sources/distributed-fs/ceph-client/crypto/rsa.c

Purpose: implements the generic MPI-backed raw RSA akcipher algorithm and registers the RSA padding/signature templates.

Important APIs, types, and functions: `struct rsa_mpi_key` stores MPI values for `n`, `e`, `d`, CRT primes/exponents, and `qinv`. `rsa_enc()` and `rsa_dec()` implement akcipher request operations. `_rsa_enc()` performs RSAEP; `_rsa_dec_crt()` performs CRT RSADP. Key setup functions parse BER keys through `rsa_parse_pub_key()` and `rsa_parse_priv_key()`. `rsa_init()` registers `rsa`, `pkcs1pad`, and `pkcs1` templates.

Control flow: public-key setup frees any old key, parses ASN.1, reads `e` and `n` into MPIs, validates modulus length, and applies FIPS exponent checks when enabled. Private-key setup similarly loads CRT parameters. Encryption reads the source MPI from SG, checks `1 < m < n - 1`, computes `m^e mod n`, and writes the result. Decryption validates ciphertext and computes CRT recombination: `m1`, `m2`, `h`, and `m`.

State and persistence: RSA key MPIs persist in the akcipher tfm context until replaced or freed by `rsa_exit_tfm()`. No key is persisted outside memory.

Dependencies and integration points: depends on the MPI library, FIPS state, akcipher internals, RSA ASN.1 helper functions, and external templates declared in internal RSA headers.

Risks: raw RSA is only a primitive; callers generally need padding or signature templates. CRT private operations are sensitive and should be reviewed for side-channel properties inherited from MPI. FIPS rules reject small keys and enforce exponent constraints. `rsa_max_size()` assumes `n` is set; callers should set keys first.

Test signals: public/private key parsing, key length policy with FIPS on/off, exponent policy, raw RSA test vectors, CRT recombination correctness, invalid payload bounds, template registration rollback, and integration with `pkcs1pad` and `pkcs1`.
