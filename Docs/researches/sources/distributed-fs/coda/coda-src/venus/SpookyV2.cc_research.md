# sources/distributed-fs/coda/coda-src/venus/SpookyV2.cc

## Purpose
This file implements Bob Jenkins' SpookyHash V2 non-cryptographic hash for one-shot and incremental 128-bit hashing. Venus uses it in this subset to derive stable 9P qid path values from Venus Fids.

## Important APIs, Types, and Functions
`SpookyHash::Short()` handles messages shorter than the long-buffer threshold using 32-byte chunks and tail mixing. `Hash128()` chooses the short path for small inputs, otherwise mixes 96-byte blocks and finalizes a padded partial block. `Init()`, `Update()`, and `Final()` implement streaming hashing using `m_state`, `m_data`, `m_length`, and `m_remainder`.

## Control Flow
Short inputs go through `ShortMix` and `ShortEnd`; long inputs initialize twelve 64-bit lanes, repeatedly call `Mix`, pad the final block with the remainder length, and call `End`. Streaming updates stash short fragments until enough data exists, then mix full blocks and retain the tail for `Final`.

## State and Persistence Behavior
The hash object keeps only transient hash state. It does not persist data. Its output affects externally visible 9P qid identity; changing the implementation would change client inode identity expectations.

## Dependencies and Integration Points
It depends on `SpookyV2.h` and `memory.h`. In this tree, `9pfs.cc` uses `Hash64` for qid paths.

## Risks and Test Signals
Risks include endian differences, unaligned-read assumptions, tail handling regressions, and accidental use for security-sensitive hashing. Tests should compare one-shot and streaming results across fragment boundaries, zero-length input, lengths around 15/16/32/96/192 bytes, and known SpookyHash V2 vectors on the supported architecture.
