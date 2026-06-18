# sources/distributed-fs/openafs/src/auth/ktc.h

## Purpose
Private auth header for ticket cache and token helper entry points shared across Unix/Windows `ktc` implementations and token conversion code.

## Important APIs, Types, and Functions
Declares ticket-file name helpers (`ktc_tkt_string`, `ktc_tkt_string_uid`, `ktc_set_tkt_string`), `ktc_OldPioctl`, token jar functions (`token_buildTokenJar`, `token_addToken`, `token_replaceToken`, `token_SetsEquivalent`, `token_setPag`, free helpers), and rxkad import/extract helpers.

## Control Flow
The header itself has no control flow; it describes the call surface used when `ktc_SetTokenEx` and `ktc_GetTokenEx` need to convert between unified XDR tokens and old rxkad `struct ktc_token`.

## State and Persistence
State is owned by implementations: ticket string storage in `ktc.c`, token set allocations in `token.c`, and pioctl/kernel cache state in platform `ktc` files.

## Dependencies and Integration Points
Forward-declares `ktc_setTokenData`, `ktc_tokenUnion`, `ktc_token`, and `ktc_principal`, allowing implementation files to share prototypes without exposing full generated XDR details here.

## Risks and Test Signals
Ownership is important: token-set and token-union outputs returned by these helpers must be freed with the matching free functions. Tests should verify callers do not mix `free`, `xdr_free`, and token helper ownership incorrectly.
