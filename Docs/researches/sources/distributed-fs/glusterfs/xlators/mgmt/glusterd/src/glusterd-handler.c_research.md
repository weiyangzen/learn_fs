# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-handler.c

## Purpose
`glusterd-handler.c` is the main RPC entrypoint table and request-normalization layer for GlusterD management traffic. It receives peer-management RPCs, cluster operation RPCs, and CLI RPCs; decodes XDR payloads into Gluster dictionaries or typed request structures; performs local guard checks; then either injects events into the friend or operation state machines, starts a synchronous management transaction, or sends an immediate CLI/RPC response.

The file deliberately keeps much of the real operation logic outside itself. Volume create/start/stop/delete, brick operations, rebalance, quota, snapshot, bitrot, geo-replication, and mgmt-v3 phase handlers are implemented in sibling files, while this file wires them into RPC actors and handles shared behavior such as big-lock serialization, peer RPC creation, probe/deprobe responses, volume/peer listing, mountbroker RPCs, and daemon state export.

## Important APIs, Types, And Functions
The outer concurrency helpers are `glusterd_big_locked_handler()` and `glusterd_big_locked_notify()`. They acquire `glusterd_conf_t.big_lock` before invoking an RPC actor or RPC client notify callback. Nearly every handler exported in the actor tables is a thin locked wrapper around an internal `__glusterd_handle_*()` function.

Cluster transaction entrypoints include `glusterd_op_txn_begin()`, `glusterd_op_begin()`, `__glusterd_handle_cluster_lock()`, `__glusterd_handle_stage_op()`, `__glusterd_handle_commit_op()`, and `__glusterd_handle_cluster_unlock()`. They exchange `gd1_mgmt_*` RPC structures, create `glusterd_req_ctx_t` or `glusterd_op_lock_ctx_t`, track `transaction_id` values, use `glusterd_set_txn_opinfo()`, and inject `GD_OP_EVENT_*` events into `glusterd_op_sm`.

Peer lifecycle handlers include `__glusterd_handle_cli_probe()`, `glusterd_probe_begin()`, `__glusterd_handle_probe_query()`, `glusterd_handle_friend_req()`, `__glusterd_handle_incoming_friend_req()`, `__glusterd_handle_cli_deprobe()`, `glusterd_deprobe_begin()`, `glusterd_handle_unfriend_req()`, `__glusterd_handle_incoming_unfriend_req()`, `__glusterd_handle_friend_update()`, `glusterd_friend_add()`, `glusterd_friend_add_from_peerinfo()`, `glusterd_friend_remove()`, `glusterd_peer_hostname_update()`, `glusterd_friend_rpc_create()`, and `glusterd_peer_rpc_notify()`. These operate on `glusterd_peerinfo_t`, `glusterd_peerctx_t`, `glusterd_friend_sm_event_t`, `glusterd_friend_req_ctx_t`, and `glusterd_probe_ctx_t`.

CLI-facing operation handlers include `__glusterd_handle_set_volume()`, `__glusterd_handle_reset_volume()`, `__glusterd_handle_sync_volume()`, `__glusterd_handle_ganesha_cmd()`, `__glusterd_handle_cli_profile_volume()`, `__glusterd_handle_status_volume()`, `__glusterd_handle_cli_clearlocks_volume()`, `__glusterd_handle_barrier()`, and `__glusterd_handle_get_vol_opt()`. Most decode a `gf_cli_req`, unserialize its `dict`, validate required keys, and call `glusterd_op_begin_synctask()` or, for older profile-volume paths, `glusterd_op_begin()`.

Read/query handlers include `glusterd_list_friends()`, `glusterd_get_volumes()`, `glusterd_add_volume_detail_to_dict()`, `__glusterd_handle_cli_list_volume()`, `__glusterd_handle_cli_uuid_get()`, `__glusterd_handle_cli_uuid_reset()`, `__glusterd_handle_getwd()`, `__glusterd_handle_fsm_log()`, `glusterd_get_volume_opts()`, and `glusterd_get_state()`.

Response helpers include `glusterd_op_lock_send_resp()`, `glusterd_op_unlock_send_resp()`, `glusterd_op_mgmt_v3_lock_send_resp()`, `glusterd_op_mgmt_v3_unlock_send_resp()`, `glusterd_op_stage_send_resp()`, `glusterd_op_commit_send_resp()`, `glusterd_xfer_friend_add_resp()`, `glusterd_xfer_friend_remove_resp()`, `glusterd_xfer_cli_probe_resp()`, `glusterd_xfer_cli_deprobe_resp()`, and `glusterd_fsm_log_send_resp()`.

The file exports the RPC programs `gd_svc_mgmt_prog`, `gd_svc_peer_prog`, `gd_svc_cli_prog`, and `gd_svc_cli_trusted_progs`. Their actor arrays bind wire opcodes such as `GLUSTERD_MGMT_STAGE_OP`, `GLUSTERD_FRIEND_ADD`, and `GLUSTER_CLI_SET_VOLUME` to the handlers in this file or to sibling-module handlers.

## Control Flow
The dominant request flow is decode, validate, delegate, respond. Handlers first call `xdr_to_generic()` against the expected request type. Requests carrying a dictionary call `dict_new()` and `dict_unserialize()`; many set `dict->extra_stdfree` to transfer ownership of the XDR-allocated buffer into the dictionary. The handler then checks required keys such as `volname`, `hostname`, `port`, `flags`, `cmd`, `key`, or `value1`. On early failure, it either sets `req->rpc_err = GARBAGE_ARGS` for malformed XDR or sends a CLI response with an operation-specific error string.

Cluster operations follow a two- or three-phase state-machine flow. The originator calls `glusterd_op_txn_begin()`, which generates and stores a transaction ID in the dictionary, sets the originator UUID, optionally acquires a management v3 volume lock with `glusterd_mgmt_v3_lock()`, initializes transaction opinfo, and injects either `GD_OP_EVENT_START_LOCK` or `GD_OP_EVENT_ALL_ACC`. Peers receive lock, stage, commit, and unlock RPCs through `__glusterd_handle_cluster_lock()`, `__glusterd_handle_stage_op()`, `__glusterd_handle_commit_op()`, and `__glusterd_handle_cluster_unlock()`. Stage and commit requests rebuild `glusterd_req_ctx_t` from the serialized dictionary and inject `GD_OP_EVENT_STAGE_OP` or `GD_OP_EVENT_COMMIT_OP`.

Peer probe begins from the CLI in `__glusterd_handle_cli_probe()`. The handler rejects local/self probes, duplicate befriended peers, and quorum failures before calling `glusterd_probe_begin()`. That function either creates a new `glusterd_peerinfo_t` plus outbound RPC, waits for connection completion, or injects a `GD_FRIEND_EVENT_NEW_NAME` event for a renamed connected peer. The remote side receives `GLUSTERD_PROBE_QUERY` in `__glusterd_handle_probe_query()`, detects same UUID and another-cluster cases, may add the probing node in `GD_FRIEND_STATE_PROBE_RCVD`, then responds.

Friend add/remove RPCs are converted into friend state-machine events. `glusterd_handle_friend_req()` validates the peer, unserializes volume metadata with a whitelist of suffixes into `ctx->vols` and `ctx->peer_ver`, then injects `GD_FRIEND_EVENT_RCVD_FRIEND_REQ`. `glusterd_handle_unfriend_req()` injects `GD_FRIEND_EVENT_RCVD_REMOVE_FRIEND`. CLI detach uses `__glusterd_handle_cli_deprobe()` to resolve the peer UUID, reject localhost, require peer connectivity unless forced, reject partial brick ownership for live volumes or snapshots, check server quorum, and call `glusterd_deprobe_begin()` to inject `GD_FRIEND_EVENT_INIT_REMOVE_FRIEND` and mark the peer as detaching.

CLI volume-setting operations are mostly transaction front doors. Set, reset, sync, ganesha, status, clear-locks, and barrier validate command dictionaries and then call `glusterd_op_begin_synctask()`. Profile-volume uses the older op state machine when `op_version < GD_OP_VERSION_6_0`, otherwise it starts the mgmt-v3 all-phases flow with a brick-op phase. Immediate read commands build response dictionaries locally: friend list iterates `priv->peers`, get-volume formats one or next volume, list-volume returns names only, get-volume-option resolves defaults and global options, and get-state writes a state file then returns its path in the dictionary.

RPC notifications update runtime state. `glusterd_peer_rpc_notify()` handles peer connect by marking the peer connected, updating generation, emitting events, and starting the version handshake. On disconnect, it releases any management v3 locks held by that peer on all volumes, updates quorum contribution, and removes a default-state probe peer if the connection failed. `glusterd_brick_rpc_notify()` maps brick IDs to `glusterd_brickinfo_t`, marks bricks started/stopped, emits brick events, stops bricks with pending snapshots, and removes stale portmap entries after abrupt disconnects.

## State And Persistence Behavior
Most persistent cluster state is reached through `glusterd_conf_t *priv = THIS->private`. The file reads and mutates `priv->peers`, `priv->volumes`, `priv->snapshots`, `priv->opts`, `priv->uuid`, `priv->global_txn_id`, service status fields, `priv->generation`, `priv->mgmt_v3_lock_timeout`, and `priv->pmap`. Peer and volume lists are accessed under the big lock and often under `RCU_READ_LOCK`.

Peer persistence is explicit. `glusterd_friend_add()` and `glusterd_friend_add_from_peerinfo()` add peerinfo objects to `conf->peers`, call `glusterd_store_peerinfo()`, and then create an RPC connection unless running in restore mode. `glusterd_peer_hostname_update()` stores updated peerinfo when requested. `glusterd_friend_remove()` cleans volume state associated with the peer and calls `glusterd_peerinfo_cleanup()`, which removes the peer from memory and persistent storage through utilities outside this file.

Operation transaction state is in dictionaries and the op-sm transaction table. `glusterd_op_txn_begin()` adds `transaction_id` and originator UUID to the request dictionary and stores `glusterd_op_info_t` with the request, operation, context dictionary, lock state, and skip-locking behavior. Stage handlers create opinfo lazily for operations that skip the lock phase.

Filesystem side effects are concentrated in UUID reset, mountbroker, unmount, get-state, and brick disconnect paths. `__glusterd_handle_cli_uuid_reset()` calls `glusterd_uuid_generate_save()` only when there are no volumes and no trusted pool peers. `__glusterd_handle_mount()` delegates to `glusterd_do_mount()` while temporarily releasing `big_lock`. `__glusterd_handle_umount()` validates that the target is under the configured mountbroker hive, runs lazy or external umount, then removes the mount directory and symlink. `glusterd_get_state()` creates an output file under the requested `odir` or `/var/run/gluster/` and writes global, peer, volume, brick, snapshot, geo-replication, service, and misc state.

Response dictionaries and XDR buffers are manually owned. Common patterns are `dict_allocate_and_serialize()` followed by `GF_FREE(rsp.dict.dict_val)`, or assigning XDR buffers to `dict->extra_stdfree` so `dict_unref()` frees them. Several handlers intentionally return zero after sending an error response to prevent duplicate replies.

## Dependencies
This file depends heavily on GlusterFS base APIs: `dict_t`, `data_t`, `uuid_t`, `rpcsvc_request_t`, `rpc_clnt_t`, `rpcsvc_actor_t`, `rpcsvc_program`, `xlator_t`, `synclock`, `GF_CALLOC/GF_FREE`, XDR encoders/decoders, logging/event APIs, and list/RCU primitives.

Its GlusterD-local dependencies include `glusterd-op-sm.h`, `glusterd-utils.h`, `glusterd-mgmt.h`, `glusterd-server-quorum.h`, `glusterd-store.h`, `glusterd-locks.h`, `glusterd-snapshot-utils.h`, `glusterd-geo-rep.h`, `glusterd-mountbroker.h`, `glusterd-syncop.h`, and the generated protocol types. These provide peer lookup, volume lookup, transaction storage, state-machine event injection, quorum checks, peer storage, brick operations, mountbroker implementation, snapshot lookups, geo-replication status, and RPC response helpers.

Sibling modules are part of the same integration surface. The CLI actor table references handlers from volume ops, brick ops, rebalance, replace-brick, log ops, quota, geo-replication, snapshot, bitrot, and management-v3 modules. The file also calls brick RPC syncops through `gd_brick_prog` when `glusterd_get_state()` requests detailed client status.

External process and OS dependencies appear in mount/unmount and state collection. The code uses `runner_t` and `_PATH_UMOUNT`, `gf_umount_lazy()`, `dirname()`, `realpath()`, `sys_rmdir()`, `sys_unlink()`, `sys_statvfs()`, `sys_opendir()`, and stdio `fopen()/fprintf()/fclose()`.

## Integration Points
`gd_svc_mgmt_prog` exposes management lock, unlock, stage, and commit RPCs to trusted peers. It is marked `.synctask = _gf_true`.

`gd_svc_peer_prog` exposes peer discovery and trusted-pool maintenance RPCs: probe query, friend add, friend remove, and friend update. It is marked `.synctask = _gf_false`, reflecting friend-state-machine style asynchronous progression.

`gd_svc_cli_prog` is the privileged CLI program. It maps many `GLUSTER_CLI_*` opcodes to handlers in this file and sibling files. This table is the effective command surface for peer probe/detach, volume set/reset/sync/status, get-state, mountbroker, and numerous volume/brick/snapshot operations.

`gd_svc_cli_trusted_progs` is a constrained CLI program for trusted/read-only use. It allows listing friends, UUID get, get/list volume, getwd, status, and mount/umount. The comment calls out mount/umount as required by geo-replication despite not being read-only.

The friend and op state machines are the core internal integration points. This file rarely applies cluster mutations directly after decode; instead it injects `GD_FRIEND_EVENT_*` or `GD_OP_EVENT_*` events, then invokes `glusterd_friend_sm()` and `glusterd_op_sm()` when immediate progression is appropriate. Cases that wait on connection establishment intentionally defer state-machine execution.

## Risks
The file is memory-ownership sensitive. XDR allocates nested buffers, dictionaries may take ownership through `extra_stdfree`, and many response paths free serialized buffers manually. Any change in a handler's early-return path can introduce leaks, double frees, or use-after-free of a request dictionary that has been passed to a transaction or CLI response helper.

Locking is subtle. The big lock serializes most handlers, but some operations intentionally release it around mount and unmount work. Peer and volume lists are also protected with RCU read sections. In `__glusterd_handle_cluster_unlock()`, the code appears to call `RCU_READ_LOCK` twice around the peer lookup where an unlock would be expected; this deserves special review because it can leave RCU state unbalanced on paths through that function.

Peer detach safety is complex. The handler allows forced detach to bypass connectivity and quorum checks, but it still blocks partial brick ownership in live volumes and snapshots. Bugs in `glusterd_friend_contains_vol_bricks()` or the snapshot-brick scan would risk either unsafe detach or overly conservative refusal.

Probe and peer RPC lifetimes are race-prone. The comments around adding peerinfo before `glusterd_friend_rpc_create()` document prior races where RPC callbacks could free a peer before it was added. The generation number in `glusterd_peerctx_t` is a guard against stale notifications; changes to peerinfo cleanup or RPC recreation need to preserve that discipline.

Request validation is uneven because handlers rely on command-specific dictionary keys. Missing keys usually produce an error response, but malformed combinations can flow deeper into operation code if the handler only validates the first few keys. `dict_get_*()` failures and `dict_unserialize()` failures are therefore important negative-test targets.

Get-state has broad read and write side effects. It opens caller-selected output paths after only checking that the directory exists, writes many fields while holding the big lock, and optionally performs brick RPC syncops for client details. It can fail due to filesystem permissions, missing brick paths, snapshot state conversion, geo-replication status collection, or brick RPC errors.

RPC notify paths affect cluster availability state. Peer disconnect releases management locks on every volume and can trigger quorum actions; brick disconnect removes portmap registrations and may mark every brick in a multiplexed process stopped. Stale or duplicate events must remain harmless.

## Test Signals
Peer-management tests should exercise CLI probe success, self-probe rejection, duplicate peer handling, same-UUID rejection, another-cluster rejection, failed probe cleanup, friend update add/update/delete, detach rejection for local peer, detach rejection when a peer hosts a subset of bricks, snapshot-brick detach rejection, forced detach behavior, and server-quorum failure responses.

Operation transaction tests should verify generated `transaction_id` propagation, originator UUID propagation, local lock acquisition and unlock on failure, stage/commit handling from unknown peers, skipped-locking operations without a `volname`, and correct error replies for malformed XDR or missing dictionary keys.

CLI query tests should cover `peer status/list`, `pool list`, `volume list`, `volume get`, `volume get all`, global option reads, max/op-version reads, uuid get/reset constraints, FSM log output, and getwd. The response dictionaries should include expected counts, names, UUIDs, volume IDs, brick entries, option counts, and error codes such as `EG_NOVOL`.

Mountbroker and get-state tests should assert path validation, big-lock release tolerance, lazy and normal unmount cleanup, default and explicit get-state output paths, `GF_CLI_GET_STATE_VOLOPTS`, `GF_CLI_GET_STATE_DETAIL`, local-brick disk statistics, and failure responses when output directories are missing.

RPC notification tests or fault-injection coverage should simulate peer connect/disconnect/destroy, handshake failure during probe, duplicate disconnects, stale brick RPC disconnects, multiplexed brick disconnect, snapshot-pending brick connect, and abrupt brick process exit requiring portmap cleanup.
