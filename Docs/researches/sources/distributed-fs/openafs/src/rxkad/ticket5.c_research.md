# sources/distributed-fs/openafs/src/rxkad/ticket5.c

Purpose: Implements Kerberos v5 ticket decoding/creation support for rxkad while deriving an rxkad-compatible 8-byte DES session key.

Important APIs/functions: `tkt_DecodeTicket5` decodes full v5 tickets or encrypted-part-only tickets, obtains service keys by kvno/enctype, decrypts enc-parts, converts v5 principals into rxkad v4-style name/instance/cell, validates flags/times, and derives the rxkad session key. `tkt_MakeTicket5` creates encrypted-part-only tickets. `tkt_DeriveDesKey` maps DES keys directly or derives DES keys from other enctypes. Internal helpers verify DES CRC/MD4/MD5 checksums, decrypt DES enc-parts, compress 3DES parity bits, and run SP800-108-style HMAC-MD5 derivation.

Control flow and state: The file includes renamed Heimdal DER and generated ASN.1 code directly. Decode chooses native DES decrypt for DES enctypes or hcrypto krb5 decrypt for other valid enctypes via `get_key_enctype`. Principal conversion applies service mapping and optional dot rejection. All decoded ASN.1 structures and crypto contexts are cleaned before return.

Dependencies and integration: Depends on hcrypto MD4/MD5/DES/HMAC, krb5 crypto APIs, `v5gen-rewrite.h`, `v5gen.h`, `der.h`, bundled `v5der.c`, generated `v5gen.c`, and rfc3961 constants. Called by `rxkad_server.c`.

Risks: Large stack buffers are bounded by `MAXKRB5TICKETLEN`. Dot-check disabling is configurable and security-sensitive. Non-DES keys are intentionally collapsed to DES-strength rxkad keys for protocol compatibility.

Test signals: Server-side v5 ticket acceptance is covered when stress or integration tests use v5 tokens; direct unit coverage is not visible in this subset.
