# sources/distributed-fs/openafs/src/rxkad/rxkad_convert.h

Purpose: Provides inline pointer conversion helpers between rxkad `ktc_encryptionKey`, raw char buffers, and hcrypto `DES_cblock` types.

Important APIs: `ktc_to_cblock`, `ktc_to_charptr`, `ktc_to_cblockptr`, `charptr_to_cblock`, and `charptr_to_cblockptr` are all cast-only helpers.

Control flow and state: Header-only, no state. It intentionally centralizes casts needed by DES/hcrypto APIs.

Dependencies and integration: Used by ticket creation/decode and stress tests when calling DES key scheduling, random-key generation, PCBC/CBC encryption, and random generator setup.

Risks: The helpers assume identical 8-byte storage layout and correct alignment. They provide no validation and should not be used with arbitrary buffers shorter than 8 bytes.

Test signals: `ticket.c`, `ticket5.c`, and `stress_c.c` compile-time and runtime paths exercise the conversions.
