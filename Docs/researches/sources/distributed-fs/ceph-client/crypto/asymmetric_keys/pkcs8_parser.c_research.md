# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/pkcs8_parser.c

Purpose: parses unencrypted PKCS#8 private key blobs, currently accepting RSA, and instantiates them as asymmetric public-key subtype keys with private-key material.

Important APIs/types/functions: `struct pkcs8_parse_context` tracks the public key object, source base, last OID, algorithm OID, and key bytes. ASN.1 callbacks `pkcs8_note_OID()`, `pkcs8_note_version()`, `pkcs8_note_algo()`, and `pkcs8_note_key()` validate and collect fields. `pkcs8_parse()` decodes the blob and duplicates the private key bytes. `pkcs8_key_preparse()` fills asymmetric key payload slots and parser metadata. `pkcs8_key_parser` registers with the asymmetric parser list.

Control flow: key preparse calls `pkcs8_parse()`, which allocates `struct public_key`, decodes ASN.1 with `pkcs8_decoder`, rejects non-version-0 and non-RSA algorithms, copies the private key, marks it private, then returns it for payload installation. Module init registers the parser as `"pkcs8"`.

State and persistence: private key bytes are stored in `public_key->key` and freed by public-key subtype destruction. No key IDs or auth signature are generated. Key persistence follows kernel keyring lifetime and permissions.

Dependencies and integration points: depends on generated `pkcs8.asn1.h`, asymmetric parser registration, public-key subtype, OID registry, and keyring preparse conventions.

Risks: only unencrypted RSA PKCS#8 is supported; unsupported algorithms return `-ENOPKG`. Private key material must stay within sensitive-free paths. Lack of key IDs means lookup by ID does not work for these keys unless descriptions are supplied externally.

Test signals: valid RSA PKCS#8 import, non-zero version rejection, unsupported algorithm OID, malformed ASN.1, private signing/decryption operations through keyctl, and sensitive cleanup on destroy.
