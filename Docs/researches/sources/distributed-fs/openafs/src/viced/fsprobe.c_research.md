# sources/distributed-fs/openafs/src/viced/fsprobe.c

Purpose: implements a minimal command-line probe that contacts an AFS fileserver and invokes `RXAFS_GetTime`, printing the server time or the RPC error. It is a simple connectivity/Rx smoke-test utility.

Important APIs/functions: `pxclient_Initialize` initializes Rx on local port 2115, creates a null-security Rx connection to the target server on port 7000 and service 1, and wraps it in a ubik client structure. `main` parses `fsprobe <serverHost>`, resolves numeric or DNS host input, initializes the client, and calls `RXAFS_GetTime` on `cstruct->conns[0]`. `GetArgs` tokenizes a space-delimited line into an argv-style array, though it is unused by `main`.

Control flow: command-line validation exits on missing host. Host parsing first tries `inet_addr`; if that returns `-1`, it falls back to `gethostbyname`. Initialization failures abort with diagnostics. The actual probe is one RPC; success prints seconds/useconds, failure prints the returned code.

State and persistence behavior: the utility uses process-global `cstruct`, `serverconns`, and `args`, but writes no persistent state. Rx and ubik client state live only for the process lifetime. Security is always null because `noAuth` is initialized to 1 and `pxclient_Initialize` ignores the `auth` parameter.

Dependencies and integration: includes generated AFS RPC interfaces from `afs/afsint.h`, Rx globals, and ubik client support. It talks to the fileserver service port directly, so it can validate that the server is reachable and responds to core AFS RPCs without involving normal cache-manager code. `AFS_component_version_number.c` embeds build version metadata.

Risks: `inet_addr` ambiguity means `255.255.255.255` is treated as invalid and sent to DNS fallback. The `auth` argument and `noAuth` comment conflict with behavior; authenticated probing is not implemented here. `ubik_ClientInit` is unusual for a single fileserver connection and may be unnecessary complexity. There is no cleanup path for Rx security objects/connections, which is acceptable for a short-lived tool but not reusable library code. Legacy `gethostbyname` limits IPv6 and thread-safety.

Test signals: smoke-test against a local test fileserver, invalid hostname, unreachable IP, and server returning an RPC error. Build warnings around unused globals/parameters and legacy resolver APIs are relevant. Packet/Rx logs can confirm the null-security call to port 7000 and service 1.
