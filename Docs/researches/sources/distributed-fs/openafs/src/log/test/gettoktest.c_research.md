## sources/distributed-fs/openafs/src/log/test/gettoktest.c

Purpose: Legacy diagnostic program for the cellular Venus token interface.

Important APIs and functions: `main` calls `U_CellGetLocalTokens` first in non-cellular mode, then iterates cellular entries until `errno == EDOM`.

Control flow: Prints a header, calls `U_CellGetLocalTokens` with `useCellEntry=0`, reports returned Vice ID or error, then loops cell indexes from 0 up to 1000 while the end-of-list condition has not been reached. For each cellular token it prints Vice ID, cell id, and primary flag.

State and persistence: Read-only with respect to tokens. It prints current cache manager token state.

Dependencies and integration: Includes legacy headers `itc.h`, `r/xdr.h`, and `afs/comauth.h`. Built by `src/log/test/Makefile.in`.

Risks: K&R style `main` and explicit `extern int errno` reflect old C conventions. The upper bound of 1000 prevents infinite loops but is arbitrary. The file includes `sys/file.h` and legacy RPC headers that may be portability pain points.

Test signals: Run with no tokens, one token, multiple cellular tokens, end-of-list EDOM, and non-EDOM error conditions from cache manager calls.
