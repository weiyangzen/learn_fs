## sources/distributed-fs/openafs/src/kauth/test/test_interim_ktc.c

Purpose: `test_interim_ktc.c` validates token cache behavior across interim and kernel KTC implementations, including special client-name parsing, auth2-style pioctl compatibility, token forgetting, remote-cell tokens, and real AFS access checks.

Important APIs and functions: printing helpers display principals and tokens. `CheckUnixUID` and `CheckAFSId` verify how `ktc_SetToken`/`ktc_GetToken` preserve or translate client identities based on names like `AFS ID <n>`. `CheckAuth2` manually constructs old Auth2 pioctl buffers with kvno 999 and verifies KTC interpretation. `ListCellsCmd` scans cache-manager cell configuration via `VIOCGETCELL`. ACL helpers copied from `fs` parse and rewrite directory ACL strings. `TryAuthenticating` calls `ka_UserAuthenticate` and validates token times and Vice IDs. `CheckAFSTickets` creates a test directory/file, adjusts ACLs, switches PAGs, authenticates test users, forgets tokens, and verifies access changes.

Control flow: `main` parses tester/local/remote-cell arguments, initializes error tables and cell config, optionally prints an existing token, finds an unused cell token slot, runs pathological `ktc_SetToken` cases, tests AFS ID and Unix UID identity encoding, tests Auth2 token compatibility, frees the unused cell, and then runs filesystem-backed AFS ticket checks in a new PAG.

State and persistence: heavily mutates local token cache/PAG state, creates and removes `./tester_dir/touch`, and changes ACLs on the test directory. It may authenticate to a remote cell if credentials are provided.

Dependencies and integration points: depends on cache-manager pioctls, KA user authentication, KTC APIs, protection server name/CPS lookup, AFS filesystem access, ACL rights constants, and configured test users/Vice IDs.

Risks: requires a writable AFS working directory and valid test accounts. It manipulates ACLs and token state, so failed cleanup can leave local artifacts. Several helper functions use unsafe string concatenation/formatting patterns and old implicit-int declarations.

Test signals: intended success prints `All OK`; the makefile documents prerequisites in detail and includes this in `runtest` with local and optional remote tester settings.
