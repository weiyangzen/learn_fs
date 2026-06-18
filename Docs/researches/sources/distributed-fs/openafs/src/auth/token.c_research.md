# sources/distributed-fs/openafs/src/auth/token.c

## Purpose
Implements helpers for OpenAFS unified XDR token containers used by newer token pioctls and fallback conversion to/from old rxkad `ktc_token` structures.

## Important APIs, Types, and Functions
Public helpers include `token_findByType`, `token_importRxkadViceId`, `token_setRxkadViceId`, `token_extractRxkad`, `token_buildTokenJar`, `token_addToken`, `token_replaceToken`, `token_SetsEquivalent`, `token_setPag`, `token_freeToken`, `token_freeTokenContents`, `token_FreeSet`, and `token_FreeSetContents`. Static helpers decode, encode, compare, and append opaque token entries.

## Control Flow
Token unions are XDR-encoded into opaque byte arrays before being inserted into a `ktc_setTokenData` jar. Lookups peek at the encoded enum to locate a token type, decode the selected entry, and verify it. Rxkad import/export maps kvno, session key, times, ticket bytes, flags, cell, and ViceId-compatible lifetime parity.

## State and Persistence
All state is heap-owned token set data. There is no disk persistence. Sensitive key/ticket buffers are zeroed before XDR/free paths release them.

## Dependencies and Integration Points
Uses generated XDR routines for `ktc_tokenUnion` and `ktc_setTokenData`, `rxkad` token structures, `xdr_alloc`, and `ktc.h` prototypes. `ktc.c` and `ktc_nt.c` use it for Ex APIs and pioctl fallback.

## Risks and Test Signals
`token_buildTokenJar` does not handle NULL `cellname` safely with `strdup`. `token_FreeSet` frees contents and nulls the pointer but does not free the set allocation, which appears leak-prone. Equivalence compares decoded token semantics for known types and raw bytes otherwise. Tests should cover malformed opaque data, multiple same-type entries, replacement, ViceId parity, oversize tickets, sensitive zeroization, and ownership/free behavior.
