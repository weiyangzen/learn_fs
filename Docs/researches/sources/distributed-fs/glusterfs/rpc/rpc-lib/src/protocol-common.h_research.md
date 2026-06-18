## sources/distributed-fs/glusterfs/rpc/rpc-lib/src/protocol-common.h

Purpose: defines shared GlusterFS RPC protocol numbers, procedure enumerations, and selected wire-facing helper types.

Important definitions: enumerations cover FOP procedures (`GFS3_OP_*`), handshake procedures, portmap procedures, aggregator procedures, callback procedures, CLI procedures, glusterd management/friend/brick procedures, management v3 procedures, probe responses, AFR self-heal operations, FD reopen status, and getspec flags. It defines `gf_gsync_status_t` with fixed-size status fields. Program/version constants include `GLUSTER_HNDSK_PROGRAM`, `GLUSTER_PMAP_PROGRAM`, `GLUSTER_CBK_PROGRAM`, `GLUSTER_FOP_PROGRAM`, `GLUSTER_FOP_VERSION`, `GLUSTER_FOP_VERSION_v2`, management program IDs, and CLI IDs.

Control flow: no runtime control flow. This header establishes numeric contracts compiled into clients, servers, XDR users, and management code.

State and persistence: no mutable state. Its numeric values are persistent protocol ABI and must remain stable across versions unless an explicit protocol version bump handles compatibility.

Dependencies and integration: included by RPC client/server code, protocol utilities, translators, generated XDR users, and management subsystems. `rpc-clnt.c` uses FOP procnums to treat lock operations specially in saved-frame queues.

Risks: changing enum order or program/version constants breaks wire compatibility. Comments call out intentionally unused values, such as `GF_PMAP_SIGNUP`, retained to preserve numbering. Fixed-size string arrays in `gf_gsync_status_t` require careful bounded writes by callers.

Test signals: wire compatibility tests, generated XDR compile tests, client/server interoperability tests across versions, and checks that new IDs append rather than renumber existing constants.
