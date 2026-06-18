# sources/distributed-fs/ceph-client/include/crypto/streebog.h

Purpose: defines Streebog/GOST R 34.11-2012 digest constants and state structures.

Important APIs, types, and flow: constants define 256-bit and 512-bit digest sizes and 64-byte block size. `struct streebog_uint512` stores 512-bit values as 64 bytes; `struct streebog_state` tracks hash state, checksum/sigma state, byte count, and partial block buffer.

State and persistence: caller-owned hash state only; no persistence.

Dependencies and integration: consumed by Streebog hash implementations under the crypto API or direct helper code.

Risks and test signals: risks include byte-order handling in 512-bit counters/checksums and finalization differences between 256/512 variants. Signals include GOST known-answer vectors, split-update tests, empty-message tests, and export/import state checks if wrapped by shash.
