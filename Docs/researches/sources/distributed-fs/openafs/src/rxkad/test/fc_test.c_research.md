# sources/distributed-fs/openafs/src/rxkad/test/fc_test.c

Purpose: Automated regression test for fcrypt block and CBC operations.

Important flow: Defines static input, expected encrypted output, and key bytes. `main` schedules the key, verifies ECB encryption against expected bytes, verifies ECB decryption back to cleartext, verifies CBC encryption against expected two-block output with an all-zero IV, and verifies CBC decryption back to cleartext.

Dependencies and integration: Uses TAP-style helpers from `tests/tap/basic.h`, OpenAFS config headers, `rx/rxkad.h`, `fcrypt.h`, and `rxkad_prototypes.h`.

State and persistence: No persistent state. Test-local IV arrays are reset for encrypt/decrypt checks.

Risks: The test has narrow vectors but is valuable because fcrypt interoperability depends on exact byte order and S-box behavior.

Test signals: Emits four planned TAP checks covering ECB encrypt, ECB decrypt, CBC encrypt, and CBC decrypt.
