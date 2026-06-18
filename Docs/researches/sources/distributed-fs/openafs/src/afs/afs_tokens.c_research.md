# sources/distributed-fs/openafs/src/afs/afs_tokens.c

## Purpose

`afs_tokens.c` implements the in-kernel token jar abstraction used to store, query, serialize, and securely free authentication tokens. It currently supports rxkad (`RX_SECIDX_KAD`) tokens and bridges between internal token storage and new-style pioctl token structures encoded with XDR.

## Important APIs, Types, and Functions

Core APIs include `afs_FindToken`, `afs_FreeTokens`, `afs_AddToken`, `afs_DiscardExpiredTokens`, `afs_HasUsableTokens`, `afs_HasValidTokens`, `afs_AddRxkadToken`, `afs_AddTokenFromPioctl`, `afs_ExtractTokensForPioctl`, `afs_free_ktc_tokenUnion`, and `afs_free_ktc_setTokenData`. Important internal helpers are `afs_FreeFirstToken`, `afs_IsTokenExpired`, `afs_IsTokenUsable`, `countValidTokens`, `afs_AddRxkadTokenFromPioctl`, `rxkad_extractTokenForPioctl`, and `extractPioctlToken`. Data structures include `struct tokenJar`, `union tokenUnion`, `struct rxkadToken`, `struct ClearToken`, `struct ktc_tokenUnion`, `struct ktc_setTokenData`, and `struct token_opaque`.

## Control Flow and State

Tokens are stored as a singly linked list. `afs_AddToken` allocates a zeroed jar node, sets its security type, pushes it onto the front, and returns the union payload. `afs_AddRxkadToken` allocates and copies the opaque rxkad ticket and copies the clear token. Lookups scan by security index and return the first matching token. Expiration is type-specific: rxkad tokens are expired when `EndTimestamp < now - NOTOKTIMEOUT`; unknown token types are considered non-expired but unusable. `afs_DiscardExpiredTokens` walks with a pointer-to-pointer so it can unlink and securely free expired nodes in place.

Pioctl import converts `struct ktc_tokenUnion` rxkad fields into a `ClearToken` and ticket copy. Export first counts valid tokens, allocates an XDR token array, converts each internal token to a pioctl token, computes its encoded length with `xdrlen_create`, allocates the opaque buffer, and XDR-encodes into it. Secure free wrappers zero keys, tickets, opaque encoded buffers, and top-level structures before delegating to XDR free routines.

## Dependencies and Integration Points

This file depends on `token.h`, XDR helpers, kernel allocation wrappers (`afs_osi_Alloc`, `osi_Alloc`, `xdr_alloc`), and rxkad token definitions. `afs_user.c` calls token functions to garbage collect expired credentials, determine whether users have usable tokens, free user token jars, and reset access state. Pioctl handlers call the import/export helpers for SetTokens/GetTokens style operations.

## Persistence and Side Effects

Token state is in-memory per user/PAG record. Ticket buffers and keys are sensitive; the file attempts to zero them before freeing, though comments acknowledge compilers may optimize dead stores. Adding tokens changes authentication behavior for future Rx connections; discarding/freeing tokens may cause user records and access caches to be treated as unauthenticated.

## Risks and Test Signals

Risks include incomplete secure clearing, XDR allocation/free mismatches, token count/export races if callers do not hold user locks, treating unknown token types as valid but unusable, and error cleanup leaks in partial export failure paths. Test signals include rxkad import/export round trips, expired-token discard, multiple-token jar ordering, unsupported token type rejection on import, allocation-failure cleanup in XDR export, and verification that user GC drops records once no usable tokens remain.
