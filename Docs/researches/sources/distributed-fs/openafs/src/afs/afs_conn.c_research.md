# sources/distributed-fs/openafs/src/afs/afs_conn.c

Purpose: Manages RX client connections from the cache manager to fileservers and VL servers. It selects server addresses, pools connections per server-address/user/port, chooses security objects, handles token changes, and releases/destroys connection vectors.

Important APIs and functions: `afs_Conn` selects a fileserver for a FID's volume. `afs_ConnBySA`, `afs_ConnByHost`, and `afs_ConnByMHosts` create or reuse connections by address, host, or host array. `afs_PutConn` releases a selected connection and RX reference. `afs_ReleaseConns`, `afs_ReleaseConnsUser`, and `ForceNewConnections` tear down or force recreation. Internals include `find_preferred_connection`, `release_conns_user_server`, `release_conns_vector`, and `afs_pickSecurityObject`.

Control flow: `afs_Conn` obtains the volume, chooses the best non-down server address by volume status and server rank while respecting request skip lists, obtains the calling user, and delegates to `afs_ConnBySA`. `afs_ConnBySA` searches existing vectors under `afs_xconn`, creates a vector if allowed, selects a low-utilization slot, handles bad-token downgrade to unauthenticated connections, recreates RX connections when `forceConnectFS` is set, sets hard/idle dead times, configures NAT ping on one filesystem connection, and returns an extra RX ref. `afs_PutConn` decrements both connection and vector refs and drops the RX ref.

State and persistence: Volatile state includes `srvAddr->conns`, `sa_conn_vector` lists, per-slot `afs_conn` refs and RX ids, NAT ping owner, `forceConnectFS`, user token states, `cryptall`, `VNOSERVERS`, and locks `afs_xconn`/`afs_xinterface`. No durable state is stored.

Dependencies and integration points: Integrates with volume/server/cell selection, user/token management, RX and rxkad security classes, server activation/down logic, request retry analysis, replicated volume handling, and NAT keepalive behavior. `afs_Analyze` calls `afs_PutConn` and `ForceNewConnections`.

Risks: Reference-count correctness is critical; imbalance panics in `afs_PutConn`, while vector release skips referenced vectors. Security-object choice mutates `user->viceId` and token-bad handling clears `UHasTokens`. The service-number selection for VL versus fileserver is a historical port comparison. GLOCK drops around RX operations require careful caller context.

Test signals: Connection reuse under `RX_MAXCALLS`, vector creation per user/port/replication flag, server selection with down/busy/offline/skipped hosts, authenticated and unauthenticated security object creation, token expiry forcing new null connections, NAT ping reassignment after destruction, VL hard-dead-time configuration, release while refs are live, user connection release, and `ForceNewConnections` recreation on next use.
