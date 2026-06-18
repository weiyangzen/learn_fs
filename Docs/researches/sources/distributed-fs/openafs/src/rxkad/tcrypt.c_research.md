# sources/distributed-fs/openafs/src/rxkad/tcrypt.c

Purpose: Standalone diagnostic and timing program for the fcrypt primitive.

Important APIs/functions: `print_msg` prints 8-byte-aligned buffers and a simple checksum. `compare` counts changed bits between two 64-bit blocks. `main` supports timing ECB encryption, timing key scheduling, CBC round-trip testing, and avalanche testing across data/key bit flips.

Control flow and state: In normal mode it iterates even round counts, optionally changing global `ROUNDS` under `TCRYPT`, encrypts a fixed block under key `abcdefgh`, flips every data and effective key bit, and reports average/minimum bit differences. CBC mode constructs a 40-byte message, encrypts/decrypts it, and compares output.

Dependencies and integration: Includes `fcrypt.h` and defines a local `ktc_encryptionKey` for standalone compilation. It also includes component version metadata.

Risks: Old K&R-style function definitions and some suspicious CBC IV local usage reflect its diagnostic nature. It is not a production test harness and mostly reports rather than asserts.

Test signals: Useful manual signal for cipher reversibility, avalanche quality, and rough performance.
