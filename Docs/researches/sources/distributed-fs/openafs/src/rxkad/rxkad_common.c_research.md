# sources/distributed-fs/openafs/src/rxkad/rxkad_common.c

Purpose: Shared rxkad implementation for initialization, stats aggregation, endpoint derivation, packet prepare/check, object lifetime, connection lifetime, and level conversion.

Important APIs: `rxkad_Init` initializes pthread-only stats and random mutex state. `rxkad_SetupEndpoint` serializes epoch, masked CID, and security index. `rxkad_DeriveXORInfo` encrypts endpoint data to derive per-connection checksum material. `rxkad_CksumChallengeResponse` hashes v2 challenge responses with the endpoint checksum field zeroed. `rxkad_SetLevel` sets Rx security header/trailer sizes. `rxkad_NewConnection`, `rxkad_DestroyConnection`, `rxkad_PreparePacket`, `rxkad_CheckPacket`, `rxkad_GetStats`, `rxkad_StringToLevel`, and `rxkad_LevelToString` implement the shared security-class operations.

Control flow and state: Client connections derive `preSeq` immediately from the session key and endpoint. Server connections allocate empty state and become usable after authentication. `rxkad_PreparePacket` always sets a packet checksum, seals sequence/call-number/length into the first word for auth/crypt levels, rounds packet length, and encrypts either the first block or the whole packet. `rxkad_CheckPacket` verifies optional checksum, decrypts, validates the sealed sequence/call-number value, and restores the real data size.

Dependencies and integration: Central glue between Rx calls/packets, fcrypt, private structures, stats macros, and packet crypto functions from `crypt_conn.c`.

Risks: Packet data layout is tightly coupled to Rx header/trailer sizes. Expiration checks happen per packet. Checksum adoption uses `cksumSeen`, so compatibility with old clients is stateful.

Test signals: Stress call tests and hijack tests directly exercise sealed call-number checks, checksum downgrade prevention, and connection expiration/authentication behavior.
