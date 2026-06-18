# File Research: sources/block-storage/kvdo/vdo/murmurhash3.c

## Purpose
Kernel implementation of MurmurHash3 x64 128-bit hashing, adapted for VDO/UDS use and exported as a symbol.

## Key Functions
- `murmurhash3_128`: computes a 128-bit hash from key bytes, length, and seed.
- `rotl64`, `getblock64`, `putblock64`, `fmix64`: internal helpers for rotation, endian-aware block access, and final avalanche mixing.

## Behavior
Processes 16-byte blocks into two 64-bit hash lanes, handles remaining tail bytes through fallthrough switch cases, finalizes with length mixing and `fmix64`, then writes two 64-bit output words in endian-correct form.

## Integration Notes
Includes `<linux/murmurhash3.h>` and exports `murmurhash3_128` with `EXPORT_SYMBOL`. Endianness is resolved at compile time for little- and big-endian systems.
