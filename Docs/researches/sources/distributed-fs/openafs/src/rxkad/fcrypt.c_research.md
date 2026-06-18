# sources/distributed-fs/openafs/src/rxkad/fcrypt.c

Purpose: Implements the rxkad private "fcrypt" block cipher used for rxkad packet sealing and challenge-response encryption. It supplies key scheduling plus ECB and CBC operations over 8-byte blocks, using static S-boxes from `sboxes.h`.

Important APIs: `fc_keysched` compresses the 8-byte `ktc_encryptionKey` by dropping DES parity bits and rotating the resulting 56-bit state into a 16-round `fc_KeySchedule`. `fc_ecb_encrypt` encrypts or decrypts one 8-byte block using a Feistel-like pair of 32-bit halves, S-box substitution, and 5-bit rotation. `fc_cbc_encrypt` chains ECB blocks with an 8-byte IV and updates the caller-provided IV so scatter/gather callers can continue CBC across segments.

Control flow and state: The file is stateless except for optional `TCRYPT` global `ROUNDS`; normal builds use 16 rounds. `fc_ecb_encrypt` switches on encrypt/decrypt, walks the schedule forward for encryption and backward for decryption, and stores output in network byte order. `fc_cbc_encrypt` pads only the final encryption block with zeroes and never pads on decrypt; it mutates the IV argument after every block.

Dependencies and integration: Used by `rxkad_client.c`, `rxkad_common.c`, `rxkad_server.c`, packet crypto in `crypt_conn.c`, and test programs. It depends on OpenAFS endian wrappers, `rxkad.h`, `rxkad_stats.h`, and `sboxes.h`.

Risks: This is legacy cryptography, not modern DES/AES. The CBC IV mutation is intentional but easy to misuse if callers reuse IV storage unexpectedly. The code assumes 8-byte aligned logical blocks and copies fixed 8-byte chunks even for the final padded encrypt block.

Test signals: `tcrypt.c` and `test/fc_test.c` directly exercise ECB/CBC round trips, known vectors, and avalanche behavior; stress tests indirectly exercise packet sealing.
