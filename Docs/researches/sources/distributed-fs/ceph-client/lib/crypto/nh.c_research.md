# sources/distributed-fs/ceph-client/lib/crypto/nh.c

## Purpose
Implements the NH almost-universal hash function variant used by Adiantum. It is a keyed universal hash, not a standalone cryptographic hash.

## Important APIs, Types, and Functions
- Exports `nh(const u32 *key, const u8 *message, size_t message_len, __le64 hash[NH_NUM_PASSES])`.
- Optional static `nh_arch()` override comes from `$(SRCARCH)/nh.h` under `CONFIG_CRYPTO_LIB_NH_ARCH`.
- Assumes `NH_PAIR_STRIDE == 2` and `NH_NUM_PASSES == 4`.

## Control Flow and State
`nh()` first lets an architecture implementation consume the request. The generic path initializes four 64-bit sums, processes each 16-byte `NH_MESSAGE_UNIT`, loads four little-endian message words, adds pass-specific key words, multiplies paired sums, advances key and message pointers, and writes four little-endian 64-bit outputs. No persistent state exists.

## Dependencies and Integration Points
Used by Adiantum-related crypto code. Depends on `<crypto/nh.h>`, unaligned little-endian loads, and optional architecture dispatch.

## Risks and Test Signals
The generic loop assumes `message_len` is a multiple of `NH_MESSAGE_UNIT`; callers must pad or constrain input. The key schedule length must match message length. Tests should include Adiantum/NH known vectors, architecture-vs-generic equivalence, zero and multi-unit messages, and rejection or caller-side handling of non-multiple lengths.
