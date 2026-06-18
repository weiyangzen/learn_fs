## sources/distributed-fs/openafs/src/rxkad/bg-fcrypt.c

### Purpose
`bg-fcrypt.c` implements the rxkad fcrypt block cipher/key schedule and Rx packet encryption/decryption using CBC mode over packet fragments.

### Important APIs, Types, And Functions
Public functions are `fc_keysched`, `fc_ecb_encrypt`, `fc_cbc_encrypt`, `rxkad_EncryptPacket`, and `rxkad_DecryptPacket`. Static inline helpers implement 16-round Feistel ECB encrypt/decrypt and CBC encrypt/decrypt. Large static S-box tables define the round function.

### Control Flow
`fc_keysched()` compresses parity bits from an 8-byte key into 56 bits, emits 16 rotated 32-bit round schedules, and records stats. ECB applies the Feistel rounds forward or reverse. CBC XORs with IV, encrypts/decrypts blockwise, updates IV, and copies eight-byte blocks. Packet encryption zeroes part of the rxkad security header, then walks `wirevec` fragments from index 1, encrypting in place; decryption reverses that walk.

### State, Persistence, And Dependencies
Persistent static state is only S-box constants. Runtime state is caller-provided schedules, IV copies, packet buffers, and rxkad stats counters. Kernel and user builds use different includes and endian helpers.

### Integration Points
rxkad client/server/common code calls these packet crypto functions for encrypted security levels. The Makefile builds `fcrypt.c` normally; this file also contains a standalone `TEST` harness with known vectors and performance timing.

### Risks
Comments note intentional over-read/over-write assumptions for partial CBC blocks, relying on packet layout. Endianness and schedule compatibility are critical; schedules are not interchangeable with other implementations. Legacy fcrypt is weak by modern standards but required for rxkad compatibility.

### Test Signals
Use the built-in known vectors under `TEST`, packet encrypt/decrypt round trips across fragmented packets and partial lengths, endian-platform tests, stats increments, and kernel/user build coverage.
