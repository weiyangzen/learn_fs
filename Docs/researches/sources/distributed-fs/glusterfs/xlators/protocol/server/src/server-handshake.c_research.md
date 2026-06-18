# sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-handshake.c

## Purpose

`server-handshake.c` implements protocol/server handshake RPC procedures: getspec, setvolume, ping, and lock-version negotiation. The central responsibility is `SETVOLUME`, which binds a transport to a GlusterFS client object, validates the requested subvolume, authenticates the client, initializes inode tables, and performs the first lookup required before FOP processing can begin.

## Important APIs, types, and functions

`server_getspec()` optionally serves a volfile from `conf->volfile_dir`, rejects `../` in volid, reads `<volid>.vol`, and replies with `gf_getspec_rsp`. `server_setvolume()` decodes `gf_setvolume_req`, unserializes client parameters, validates `remote-subvolume`, finds the target xlator, checks graph cleanup and parent-up state, checks child-up status, validates process UUID and volume ID, creates or retrieves the `client_t`, sets login credentials and SSL name in params, checks FOP/MGMT versions, stores opversion, authenticates with `gf_authenticate()`, stores client options, binds `client->bound_xl`, creates an inode table if needed, sends server process UUID, dummy lock version, and transport pointer, then performs `server_first_lookup()`. `server_first_lookup()` does root lookup and, for subdir mounts, walks each path component through `do_path_lookup()` and stores `subdir_gfid`/`subdir_inode`. `server_ping()` replies success. `server_set_lk_version()` echoes the requested lock version. `gluster_handshake_prog` registers the actors.

## Control flow

A client connects at the RPC layer, then calls `SETVOLUME`. The server copies base options, locates the target brick xlator, rejects requests while the graph is not ready or cleanup is starting, populates a reply dict with child/volume/process metadata, authenticates, and only then allows the transport's `xl_private` to point at the client. On success, first lookup validates backend reachability and subdir-mount existence. The response is serialized into `gf_setvolume_rsp` and sent through `server_first_lookup_done()`.

## State and persistence behavior

Handshake mutates transport state (`req->trans->xl_private`, `clnt_options`), client state (`client_name`, `bound_xl`, `opversion`, subdir fields), peerinfo max op version in `conf->xprt_list`, and bound xlator inode table allocation. State is process-memory only but forms the active session identity for all future FOPs.

## Dependencies and integration points

This file depends on generated handshake XDR, dict serialization, auth modules, `auth_set_username_passwd()`, client table APIs, syncop lookup, inode APIs, graph locks, events, and server reply submission. It integrates with protocol/client `client_handshake()` and with all FOP handling because FOPs require a bound/authenticated client.

## Risks and test signals

High-risk areas include error-path cleanup, setting `xl_private` only for valid clients, subdir mount path walking, volume-ID mismatch, graph cleanup races, and authentication config copying. `gf_compare_client_version()` is currently a stub returning success, so version mismatch protection is incomplete. Tests should cover malformed XDR, missing `remote-subvolume`, missing child-up, wrong volume ID, auth reject, auth accept, missing auth modules, cleanup-starting races, subdir mount success/failure, getspec path traversal rejection, and lock-version/ping compatibility.
