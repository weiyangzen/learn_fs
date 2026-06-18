# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/pkcs7_parser.c

Purpose: parses PKCS#7/CMS signed-data blobs into in-memory `struct pkcs7_message` objects containing content metadata, embedded X.509 certificates, CRLs, and signer information.

Important APIs/types/functions: `struct pkcs7_parse_context` tracks the message under construction, current `SignedInfo`, certificate lists, raw issuer/serial/SKID fields, OIDs, and indexes. `pkcs7_parse_message()` drives `asn1_ber_decoder()`. `pkcs7_free_message()` frees certificates and signed infos. OID, version, content, certificate, signer, authenticated-attribute, serial, issuer, SKID, and signature callbacks fill `struct pkcs7_message` and `struct pkcs7_signed_info`.

Control flow: parsing allocates a message and first `SignedInfo`, decodes ASN.1, appends certificates through `x509_cert_parse()`, records encapsulated data or detached-data metadata, maps digest/signature OIDs to crypto algorithm strings, enforces authenticated attribute consistency, and appends completed signed-info records. Authenticated attributes must contain content type and message digest and cannot repeat supported attributes.

State and persistence: parsed state is heap memory owned by the returned `pkcs7_message`; embedded certificates link into `certs` and `crl`, signers link through `signed_infos`, and signature buffers/auth IDs are owned by each signed info. No state persists after `pkcs7_free_message()`.

Dependencies and integration points: depends on generated `pkcs7.asn1.h`, OID registry, public-key signature structures, X.509 parser, and later verification/trust code in `pkcs7_verify.c` and `pkcs7_trust.c`.

Risks: ASN.1 pointer/length bookkeeping is high risk because many fields point into the original blob while signatures are duplicated. Authattrs policy differs by usage and ML-DSA compatibility config. Signer ID construction must choose issuer+serial versus SKID correctly. Missing cleanup after late allocation failures can leak partially built structures.

Test signals: DER/BER PKCS#7 messages with attached and detached data, multiple signers, CMS version 3 SKID signers, Authenticode authenticated attributes, duplicate/missing authattrs rejection, unsupported OIDs, and malformed certificate lists.
