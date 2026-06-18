# sources/distributed-fs/coda/coda-src/auth2/clog.c

Purpose: User login tool that obtains Coda auth tokens from auth2 or a file, sends them to Venus, and optionally verifies local token round-trip.

Important APIs/functions: `printusage` and `main`. It uses `U_GetAuthServers`, `U_Authenticate`, `U_SetLocalTokens`, `U_GetLocalTokens`, `WriteTokenToFile`, and `ReadTokenFromFile`.

Control flow: Parses flags for quiet/test modes, host override, token input/output files, run-as user, and username/realm. It derives username from effective UID when omitted, reads realm config, initializes RPC, obtains or reads tokens, optionally writes them to a file, sends them to Venus, and in test mode fetches and compares tokens.

State and persistence: Writes optional token files and updates Venus token state. Reads `venus.conf`/`auth2.conf`, realm data, and optional input token file.

Dependencies and integration: Uses `auser`, `avenus`, `tokenfile`, RPC2/LWP, Coda config, and realm parsing. It is the main end-user bridge between auth2 and Venus.

Risks and test signals: `-as` calls `setuid` after `getpwnam` without reporting failure. Token files are sensitive and file-mode handling is in `tokenfile.c` outside this subset. Non-tty stdin disables interactive password prompts. Test mode compares exact token structs and prints byte-order-converted values.
