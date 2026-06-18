## sources/distributed-fs/openafs/src/log/tokens.c

Purpose: Implements the `tokens` command, printing rxkad tokens held by the cache manager and their expiration status.

Important APIs and functions: `main` uses `ktc_ListTokensEx`, `ktc_GetTokenEx`, `token_extractRxkad`, and `token_FreeSet`.

Control flow: Rejects any argument except help-style usage by printing `Usage: tokens [-help]`. It prints a heading, then iterates token entries by cell number. For each cell, it fetches token data, extracts an rxkad token and client principal, formats user identity from name and instance, prints cell and expiration state, then frees the token set. End of list prints `--End of list--`.

State and persistence: Read-only with respect to token state. Allocated `cellName` strings are freed each iteration.

Dependencies and integration: Uses auth, ktc, token, rx/xdr, and component version infrastructure. Built as both `tokens` and `tokens.krb`, though source behavior is not separately conditional here.

Risks: Uses `strcpy`/`strcat` into `UserName` sized for expected ktc principal fields. Only rxkad tokens are printed; other token types in the set are ignored. Any argument prints usage and exits success, which may mask invalid usage.

Test signals: No tokens, expired token, normal user principal, empty principal, `AFS ID` and `Unix UID` display branches, token extraction failure, and multiple-cell iteration.
