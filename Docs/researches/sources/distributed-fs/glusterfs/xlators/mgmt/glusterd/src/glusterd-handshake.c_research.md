# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-handshake.c

## Purpose
`glusterd-handshake.c` implements the server-side Gluster handshake RPC program and the GlusterD management handshake used between peers. It serves client volfile requests, event notifications, volume and snapshot metadata queries, and peer operating-version negotiation. It also contains the older dump-version discovery path used before switching to the management handshake program.

## Important APIs, Types, And Functions
Key exported entry points include `server_getspec`, `server_event_notify`, `server_get_volume_info`, `server_get_snap_info`, `glusterd_mgmt_hndsk_versions`, `glusterd_mgmt_hndsk_versions_ack`, `glusterd_mgmt_handshake`, `glusterd_peer_dump_version`, and `glusterd_set_clnt_mgmt_program`. The file defines the local management handshake procedure enum `GD_MGMT_HNDSK_*`, the random management handshake program number/version, RPC service program tables for `gluster_handshake_prog`, `gluster_cli_getspec_prog`, and `glusterd_mgmt_hndsk_prog`, and client program descriptors for dump and management handshake callbacks.

`build_volfile_path()` is central to client mounting. It maps requested volume identifiers into volfile paths for regular volumes, trusted internal volfiles, snapshots, snapd, glusterd-managed services, self-heal daemon, rebalance, gfproxy, and client-per-brick volfiles. `glusterd_get_args_from_dict()` parses getspec xdata and records client min/max op versions plus an optional brick name. `_client_supports_volume()` rejects client volfile requests whose version range cannot support the target volume's `client_op_version`.

Snapshot support is embedded in `get_snap_volname_and_volinfo()`, `glusterd_create_missed_snap()`, and `glusterd_take_missing_brick_snapshots()`. These functions parse `/snaps/...` paths, resolve snapshot volume information, create missed brick snapshots, mount/start snap bricks, and persist updated missed-snapshot state.

## Control Flow
`__server_getspec()` decodes a `gf_getspec_req`, normalizes the requested volume key into `req->trans->peerinfo.volname`, parses xdata, checks client/volume op-version compatibility, chooses trusted or untrusted volfile path based on local address detection, builds a connected peer host list in response xdata, stats and reads the volfile, optionally creates missed snapshots for the requested brick, and replies with `gf_getspec_rsp`.

`__server_event_notify()` handles event notifications, currently dispatching `GF_EN_DEFRAG_STATUS` into `glusterd_defrag_event_notify_handle()` and suppressing a response for that asynchronous update. Unknown events are logged and surfaced through `gf_event()`.

The management handshake flow starts with `glusterd_peer_dump_version()`, which sends `GF_DUMP_DUMP` to a peer. `__glusterd_peer_dump_version_cbk()` inspects the returned program list. If the management handshake program is present, it calls `glusterd_mgmt_handshake()`. Otherwise, it falls back to program assignment only when the local op-version is compatible with old peers. `glusterd_mgmt_handshake()` sends `GD_MGMT_HNDSK_VERSIONS` with the local peer UUID. `__glusterd_mgmt_hndsk_version_cbk()` validates the peer's min/max/current op-version and sends a `GD_MGMT_HNDSK_VERSIONS_ACK` containing the local op-version. `__glusterd_mgmt_hndsk_version_ack_cbk()` installs peer RPC program pointers, emits child-up notification, and injects `GD_FRIEND_EVENT_CONNECTED` where appropriate.

On the server side, `__glusterd_mgmt_hndsk_versions()` authenticates the requester with `gd_validate_mgmt_hndsk_req()`, then replies with current, min, and max op-version. `__glusterd_mgmt_hndsk_versions_ack()` accepts the selected cluster op-version, validates that it is not beyond local support and does not reduce an existing-volume cluster, stores it in `conf->op_version`, and persists it with `glusterd_store_global_info()`.

## State And Persistence Behavior
The file mutates `req->trans->peerinfo` with volname and client op-version data, writes `conf->op_version`, updates peer program pointers (`mgmt`, `peer`, `mgmt_v3`), and can transition peer state through the friend state machine. It persists op-version changes through `glusterd_store_global_info()`, snapshot volinfo changes through `glusterd_store_volinfo()`, and missed snapshot lists through `glusterd_store_update_missed_snaps()`. Volfile serving reads generated volfiles from the GlusterD workdir and adds response xdata such as peer brick servers or service pidfiles.

## Dependencies And Integration Points
This file integrates with RPC/XDR (`xdr_to_generic`, `glusterd_submit_reply`, `glusterd_submit_request`), GlusterD volume and snapshot stores, service-volfile builders, peer management (`glusterd_peerinfo_find*` under RCU), the friend/op state machines, and transport address utilities. Its RPC program structs are registered by GlusterD initialization and consumed by clients, peers, CLI getspec, and internal daemons.

## Risks
Volfile path construction accepts many string formats and must avoid truncation, bad tokenization, and stale snapshot paths. Trusted volfile selection depends on local-address detection; mistakes can bypass auth policy for external clients or block internal services. Peer handshake validation mixes UUID and hostname matching for compatibility with older peers, so reinstall/reused hostname cases are sensitive. `conf->op_version` reduction is blocked when volumes exist, but any missed validation can create cluster incompatibility. The missed-snapshot creation path performs storage and brick-start side effects during mount/volfile serving, so failures need careful persistence and retry handling.

## Test Signals
Useful tests include getspec requests for normal, trusted, snapshot, service, rebalance, gfproxy, and client-per-brick volfile IDs; version-range rejection for incompatible clients; management handshake between compatible peers, incompatible peers, unknown peers, and peers with changed UUIDs; op-version ACK persistence and downgrade rejection when volumes exist; `GF_EN_DEFRAG_STATUS` event handling; volume UUID and snapshot-info queries; and missed-snapshot creation on brick reconnect with store updates.
