# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/x509_cert_parser.c

Purpose: parses X.509 certificates into internal certificate, public-key, signature, identity, validity, and extension state for asymmetric key instantiation and PKCS#7 chain verification.

Important APIs/types/functions: `struct x509_parse_context` tracks current certificate, OIDs, raw data base, public-key parameters, key bytes, AKID fields, and name fragments. `x509_cert_parse()` drives generated ASN.1 decoders and finalizes IDs/signature params/self-signed checks. `x509_free_certificate()` frees parsed certificates. Callback functions record OIDs, algorithms, signature bits, serial, issuer/subject names, public key parameters/data, extensions, validity times, and authority key IDs. `x509_decode_time()` validates UTCTime/GeneralizedTime and converts to `time64_t`.

Control flow: decode callbacks collect raw TBS bytes, issuer/subject, serial, public key algorithm and key bytes, signature algorithm/hash, extension flags, SKID and AKID. Finalization duplicates public key material, generates issuer+serial ID, computes signature digest parameters via `x509_get_sig_params()`, and checks self-signedness when applicable.

State and persistence: parsed certificate state is heap-owned and linked by callers. Many raw fields point into the original certificate blob, so lifetime is tied to the blob held by key preparse or PKCS#7 message. Public key bytes and generated IDs are allocated and freed by `x509_free_certificate()` or transferred to key payloads.

Dependencies and integration points: depends on generated X.509 ASN.1 decoders, OID registry, public key structures, asymmetric key ID helpers, extension flag definitions, and `x509_public_key.c`.

Risks: ASN.1 bounds and ownership are security-critical. Time parsing deliberately rejects some encodings and dates before 1970. Extension parsing must correctly interpret keyUsage/basicConstraints for keyring restrictions. Unsupported algorithms return `-ENOPKG` and can prune verification chains.

Test signals: RSA/ECDSA/ECRDSA/ML-DSA certs, SKID/AKID variants, issuer+serial IDs, self-signed certs, malformed BIT STRING metadata, invalid time encodings, keyUsage/basicConstraints extension combinations, and unsupported curve/OID handling.
