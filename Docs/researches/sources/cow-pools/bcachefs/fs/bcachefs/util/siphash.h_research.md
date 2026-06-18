# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/siphash.h

This header declares the SipHash API and convenience macros.

Constants:
- Block length: 8 bytes.
- Key length: 16 bytes.
- Digest length: 8 bytes.

Types:
- `SIPHASH_CTX`:
  - four 64-bit state words
  - 8-byte partial block buffer
  - byte count
- `SIPHASH_KEY`:
  - two little-endian 64-bit key halves

API:
- `SipHash_Init()`
- `SipHash_Update()`
- `SipHash_End()`
- `SipHash_Final()`
- `SipHash()`

Convenience macros:
- SipHash-2-4:
  - `SipHash24_Init`
  - `SipHash24_Update`
  - `SipHash24_End`
  - `SipHash24_Final`
  - `SipHash24`
- SipHash-4-8:
  - `SipHash48_Init`
  - `SipHash48_Update`
  - `SipHash48_End`
  - `SipHash48_Final`
  - `SipHash48`

Research notes:
- License is BSD-3-Clause, unlike the GPL/LGPL bcachefs utility files around it.
- The API exposes round counts through generic functions and safer named macros for common variants.
