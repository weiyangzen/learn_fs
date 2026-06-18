## sources/distributed-fs/openafs/src/kauth/test/test_rxkad_free.c

Purpose: `test_rxkad_free.c` stress-tests rxkad object/connection cleanup while repeatedly obtaining admin tokens and making KA RPCs, or while repeatedly calling the higher-level user authentication path.

Important APIs and control flow: `Main` parses iteration count, verbose output, host-usage reporting, rate limiting, reap waiting, do-auth mode, admin credentials, cell, and explicit servers. In normal mode it derives the admin key with `ka_StringToKey`, loops obtaining an admin token via `ka_GetAdminToken`, opens a maintenance ubik connection with `ka_AuthServerConn`, optionally prints connection/security-object details, calls `KAM_GetEntry`, records server usage from ubik RPC connections, and destroys the ubik client. In `-doauth` mode it calls `ka_UserAuthenticateLife` instead. It monitors `sbrk(0)` memory usage over time, finalizes Rx, prints rxkad stats, optionally waits for connection reap, and asserts object/destroy counters match.

State and persistence: writes local token state when `-doauth` is used. Otherwise it creates and destroys rxkad/ubik client objects in memory. It does not persist files.

Dependencies and integration points: requires live KA services, valid admin credentials, rx/rxkad stats globals, ubik, command parser, and optional server list parsing.

Risks: memory-leak detection uses `sbrk`, which is allocator/platform-sensitive. Counter names in the final check include `rxkad_stats_clientObjects`, which may depend on macro/global definitions outside this file. Host-usage reporting is incompatible with `-doauth`. Rate and reap timing affect results.

Test signals: the makefile runs this twice in `runtest`, once normal and once with `-doauth`, both with `-waitforreap`. Success prints stats and exits 0; failures include unmatched rxkad destruction counts or increasing high-water memory.
