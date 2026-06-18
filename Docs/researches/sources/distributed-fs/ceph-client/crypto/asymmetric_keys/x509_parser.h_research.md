# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/x509_parser.h

Purpose: defines the internal X.509 certificate representation and parser/public-key helper declarations shared by X.509 parser, public-key instantiation, PKCS#7 verification, and selftests.

Important APIs/types/functions: `struct x509_certificate` stores links, signer pointer, public key, signature, SHA-256 TBS hash, issuer/subject strings, issuer+serial ID, SKID, validity times, raw TBS/signature/serial/issuer/subject/SKID pointers and sizes, index, and verification flags. Declarations include `x509_free_certificate()`, `x509_cert_parse()`, `x509_decode_time()`, `x509_get_sig_params()`, and `x509_check_for_self_signed()`.

Control flow: parser code fills this structure, public-key preparse transfers selected fields into key payloads, and PKCS#7 verification/trust code uses signer, seen, verified, self-signed, unsupported, and blacklisted flags.

State and persistence: state is per parsed certificate. Ownership transfers are explicit in `x509_public_key.c`; otherwise `x509_free_certificate()` frees allocated members.

Dependencies and integration points: includes cleanup helpers, time types, public-key structures, asymmetric key IDs, and SHA-256 size constants.

Risks: mixed borrowed raw pointers and owned allocations require disciplined lifetime handling. Verification flags are reused across chain verification passes and must be reset where needed.

Test signals: parser/preparse ownership transfer, PKCS#7 embedded cert chain verification, blacklist hashing, and cleanup leak tests.
