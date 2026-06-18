# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/siphash.c

This file implements SipHash with configurable compression/finalization rounds. It is BSD-3-Clause licensed and derived from OpenBSD/FreeBSD lineage.

Core functions:
- `SipHash_Rounds()` executes SipRound for a requested number of rounds.
- `SipHash_CRounds()` mixes one 8-byte little-endian message block.
- `SipHash_Init()` initializes state from a 128-bit key and fixed SipHash constants.
- `SipHash_Update()` streams arbitrary-length input:
  - tracks buffered bytes
  - completes partial blocks
  - processes full 8-byte blocks
  - stores trailing bytes
- `SipHash_Final()` writes little-endian 64-bit digest.
- `SipHash_End()` pads the final block with total byte count, runs finalization, zeroes context, and returns digest.
- `SipHash()` is the one-shot helper.

Important behavior:
- Uses unaligned little-endian loads for message blocks.
- The context is cleared on `SipHash_End()`.
- Round counts are caller-selected, enabling SipHash-2-4 and SipHash-4-8 through macros in the header.

Research notes:
- This is standalone cryptographic/hash utility code rather than bcachefs-specific logic.
- The implementation returns a 64-bit keyed PRF suitable for short inputs.
