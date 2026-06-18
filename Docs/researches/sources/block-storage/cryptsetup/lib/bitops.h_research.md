# File Research: sources/block-storage/cryptsetup/lib/bitops.h

## Purpose
Portable byte-order and bitmap helper header used across libcryptsetup code.

## Key Content
Includes platform endian headers where available, handles OpenBSD endian macro names, defines fallback `bswap_16/32/64`, host-to/from little/big endian conversion macros, `swab16/32/64`, and classic bitmap macros `setbit`, `clrbit`, `isset`, and `isclr`.

## Dependencies and Coupling
Used by parsers handling on-disk little-endian or big-endian metadata, including BITLK. Depends on build-time feature macros such as `HAVE_BYTESWAP_H`, `HAVE_ENDIAN_H`, `HAVE_SYS_ENDIAN_H`, and `WORDS_BIGENDIAN`.

## Invariants and Risks
The conversion macros are preprocessor-only and assume integer-like arguments. Fallback bitmap macros depend on `NBBY`/`CHAR_BIT` semantics and do not guard index bounds.
