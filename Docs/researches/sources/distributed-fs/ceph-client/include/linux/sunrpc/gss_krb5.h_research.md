# sources/distributed-fs/ceph-client/include/linux/sunrpc/gss_krb5.h

Purpose: defines Kerberos-specific constants, token identifiers, checksum/encryption type values, and key usage numbers used by the SUNRPC GSS Kerberos mechanism.

Important APIs and types: size constants include `GSS_KRB5_MAX_KEYLEN`, `GSS_KRB5_MAX_CKSUM_LEN`, `GSS_KRB5_MAX_BLOCKSIZE`, and `GSS_KRB5_TOK_HDR_LEN`. Token constants cover legacy and RFC 4121 MIC/WRAP/initial/response identifiers and flags. `enum sgn_alg` and `enum seal_alg` define older signing/sealing algorithms. Checksum types include HMAC SHA1/SHA2 AES, CMAC Camellia, and RC4-HMAC values. Encryption types include DES, 3DES, AES CTS HMAC SHA1/SHA2, ARCFOUR, Camellia, and unknown. Key usage constants distinguish seal/sign/sequence and initiator/acceptor directions.

Control flow: Kerberos mechanism code parses tokens, selects checksum and encryption algorithms, derives keys using usage constants, and validates/creates MIC or wrap tokens.

State and persistence: no state is stored here; keys and contexts live in mechanism implementation structures.

Dependencies and integration points: depends on kernel crypto skcipher APIs, RPCSEC_GSS client context definitions, and GSS status constants.

Risks and test signals: risks include wrong enctype/checksum mapping, deprecated algorithm handling, direction-specific key usage mistakes, and export-policy-sensitive crypto changes. Test with Kerberos krb5/krb5i/krb5p mounts, AES-SHA1/SHA2 enctypes, token replay, and bad checksum/wrap vectors.
