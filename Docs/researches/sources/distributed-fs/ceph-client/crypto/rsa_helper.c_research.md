# sources/distributed-fs/ceph-client/crypto/rsa_helper.c

Purpose: provides ASN.1 decoder callbacks and exported helper functions that extract raw RSA key components from BER-encoded public and private keys.

Important APIs and functions: callbacks `rsa_get_n()`, `rsa_get_e()`, `rsa_get_d()`, `rsa_get_p()`, `rsa_get_q()`, `rsa_get_dp()`, `rsa_get_dq()`, and `rsa_get_qinv()` populate `struct rsa_key` pointers and lengths. `rsa_parse_pub_key()` and `rsa_parse_priv_key()` invoke generated decoders `rsapubkey_decoder` and `rsaprivkey_decoder`.

Control flow: decoder callbacks validate non-null/nonempty fields and size relationships against the modulus size. `rsa_get_n()` additionally strips leading zeros for FIPS size checking and rejects effective modulus sizes below 2048 bits when FIPS is enabled. The parse functions do not copy key bytes; they store pointers into the original input buffer for later MPI parsing by callers.

State and persistence: no persistent state is owned here. Returned `struct rsa_key` fields borrow the caller's input buffer lifetime.

Dependencies and integration points: depends on generated ASN.1 headers `rsapubkey.asn1.h` and `rsaprivkey.asn1.h`, `asn1_ber_decoder()`, FIPS state, and `crypto/internal/rsa.h`. Used by `rsa.c` and any other RSA key consumers.

Risks: callers must keep the BER buffer alive until they copy or parse the referenced fields. Size validation mostly enforces structural bounds, not full mathematical key consistency. FIPS size checks account for leading zeros only for modulus field.

Test signals: valid public and private DER/BER keys, missing or zero-length components, components longer than modulus, leading-zero modulus in FIPS mode, too-small FIPS keys, and malformed ASN.1 decoder failures.
