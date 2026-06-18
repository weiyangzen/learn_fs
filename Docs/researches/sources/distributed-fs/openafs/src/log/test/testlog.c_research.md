## sources/distributed-fs/openafs/src/log/test/testlog.c

Purpose: Legacy interactive test for authenticating to an AFS cell, setting local tokens in the cache manager, and restoring original tokens.

Important APIs and functions: Uses `U_GetLocalTokens`, `U_CellGetLocalTokens`, `GetLocalCellName`, `U_InitRPC`, `U_CellAuthenticate`, `U_SetLocalTokens`, and `U_CellSetLocalTokens`.

Control flow: Captures existing non-cellular and cellular tokens, discovers local cell, parses optional `-x`, user, password, and `-c cellname` arguments, optionally looks up the local passwd entry, initializes RPC, prompts for password if absent, authenticates to the AuthServer, sets tokens through both non-cellular and cellular APIs, then iterates saved tokens and restores them.

State and persistence: Temporarily mutates cache manager token state, then attempts to restore original tokens. It also erases a password argument from `argv` after copying it.

Dependencies and integration: Built by `src/log/test/Makefile.in`. Uses old auth/comauth interfaces and local cell config globals.

Risks: Old C syntax, fixed-size buffers, and `strcpy` usage carry overflow risk. A bug in the `-c` comparison checks `argv[currArg]` instead of the following cell value, so local-cell detection is suspect. Restore is best-effort; failures can leave token state changed. Password handling is primitive.

Test signals: Controlled test with valid and invalid credentials, explicit remote cell, `-x`, password prompt and password argument paths, token restoration after failures, and no-existing-token startup.
