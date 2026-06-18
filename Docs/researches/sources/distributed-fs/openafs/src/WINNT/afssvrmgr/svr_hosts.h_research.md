# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_hosts.h

Purpose: Declares the server host-list editor entry point.

Important APIs/types: `Server_Hosts(LPIDENT)` opens a per-server property sheet for host list management.

Control flow/state: Implementation owns private host-list and add-host packet types.

Dependencies/integration: Invoked from server command/menu handlers.

Risks/test signals: Callers should pass a server identity; the implementation does not validate identity type before using server name.
