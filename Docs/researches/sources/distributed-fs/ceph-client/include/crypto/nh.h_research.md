# sources/distributed-fs/ceph-client/include/crypto/nh.h

Purpose: declares constants and the primitive function for the NH universal hash used by constructions such as Adiantum.

Important APIs, types, and flow: macros define pair stride, message unit, number of passes, hash output bytes, maximum message/key words, and byte sizes. `nh()` hashes a message with a u32 key into a u8 output buffer.

State and persistence: stateless; caller supplies key, message, and output buffers. No persistence exists.

Dependencies and integration: depends on Linux integer types. It is integrated by higher-level wide-block or MAC constructions that provide padding, key scheduling, and domain separation.

Risks and test signals: `nh()` is not a standalone MAC and requires correct caller-side keying and length handling. Signals include NH known-answer vectors, boundary lengths up to `NH_MESSAGE_BYTES`, endian cross-tests, and architecture generic/optimized parity.
