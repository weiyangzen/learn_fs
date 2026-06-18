# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_nl.c

## Purpose

`drbd_nl.c` is the DRBD generic-netlink administration and notification implementation. It translates `drbdsetup`-style netlink commands into resource, connection, volume, disk, network, role, resync, resize, and lifecycle operations, then emits synchronous replies and multicast state notifications. It is also a major integration point for persistent DRBD metadata because attach, detach, resize, role changes, invalidation, UUID rotation, fencing, and helper execution all update on-disk metadata, bitmaps, activity-log layout, and exported block-device state.

## Important APIs, Types, And Functions

- Generic-netlink entry points include `drbd_adm_new_resource`, `drbd_adm_new_minor`, `drbd_adm_attach`, `drbd_adm_connect`, `drbd_adm_set_role`, `drbd_adm_resize`, `drbd_adm_disk_opts`, `drbd_adm_net_opts`, `drbd_adm_disconnect`, `drbd_adm_detach`, `drbd_adm_down`, status dump callbacks, and initial-state dump callbacks. The command table comes from `drbd_genl_api.h` and `genl_magic_func.h`.
- `drbd_adm_prepare`, `drbd_pre_doit`, and `drbd_post_doit` allocate the reply skb, parse the config context, enforce `CAP_NET_ADMIN` for mutating commands, resolve minor/resource/connection objects, take krefs, and release references after command handling.
- `drbd_msg_put_info` and `drbd_msg_sprintf_info` attach human-readable failure text to the reply under `DRBD_NLA_CFG_REPLY`.
- `drbd_set_role` implements promotion/demotion policy, including pinging peers, outdating/fencing paths, forced promotion handling, UUID primary-bit changes, metadata sync, read-only disk toggling, and uevents.
- Disk configuration paths include `drbd_adm_attach`, `drbd_adm_disk_opts`, `drbd_adm_detach`, `drbd_determine_dev_size`, `drbd_new_dev_size`, `drbd_check_al_size`, `sanitize_disk_conf`, `open_backing_devices`, and `drbd_backing_dev_free`.
- Network paths include `drbd_adm_connect`, `drbd_adm_net_opts`, `drbd_adm_disconnect`, `check_net_options`, `_check_net_options`, `alloc_crypto`, `free_crypto`, and `conn_try_disconnect`.
- Resync and verification controls include `drbd_adm_invalidate`, `drbd_adm_invalidate_peer`, `drbd_adm_pause_sync`, `drbd_adm_resume_sync`, `drbd_adm_start_ov`, `drbd_adm_new_c_uuid`, and `resync_after_online_grow`.
- Dump/status functions include `drbd_adm_dump_resources`, `drbd_adm_dump_devices`, `drbd_adm_dump_connections`, `drbd_adm_dump_peer_devices`, `drbd_adm_get_status`, `drbd_adm_get_status_all`, `drbd_adm_get_timeout_type`, and helpers converting resource/device/connection/peer-device state and statistics into netlink attributes.
- Notification APIs include `drbd_bcast_event`, `notify_resource_state`, `notify_device_state`, `notify_connection_state`, `notify_peer_device_state`, `notify_helper`, and `drbd_adm_get_initial_state`.

## Control Flow

Generic-netlink `doit` commands first pass through `drbd_pre_doit`. The pre-hook uses `drbd_genl_cmd_flags` to decide whether a command must resolve a minor, resource, or connection. `drbd_adm_prepare` validates the config context, copies it into the reply, checks address lengths, resolves objects, checks over-specified requests, and stores the resulting `drbd_config_context` in `info->user_ptr[0]`. The command handler then performs its specific work and writes a DRBD return code into the reply header. `drbd_post_doit` sends the reply and drops any krefs.

Configuration-changing commands are serialized mainly through `resource->adm_mutex`, with finer-grained `resource->conf_update`, `connection->data.mutex`, `state_mutex`, RCU, and `req_lock` where needed. Several operations intentionally start or stop DRBD worker/receiver threads via `conn_reconfig_start` and `conn_reconfig_done` so configuration changes can interact safely with the sender workqueue and receiver lifecycle.

Attach is the most involved flow. It rejects already-configured disks, clears stale detach/error flags, allocates a new backing-device object, parses disk attributes, checks protocol/fencing restrictions, opens backing and metadata devices, reads the metadata superblock, sanitizes disk settings, creates resync/activity-log structures, suspends IO, enters `D_ATTACHING`, transfers ownership of the new backing configuration to `device->ldev`, sets queue limits, determines exported size, reads or initializes the bitmap, derives the initial disk state from metadata flags, handles connected negotiation, marks metadata dirty, syncs metadata, emits a block-device uevent, and unwinds to diskless state on failures after state transition.

Connect validates endpoint presence and uniqueness across all resources, parses network settings, checks protocol/two-primary/fencing/congestion invariants, allocates crypto transforms, installs `net_conf` under `conf_update`, copies local and peer addresses, emits create notifications for the connection and peer devices, resets counters, and requests `C_UNCONNECTED` so the receiver/connection state machine can proceed. Network option changes are similar but update an existing `net_conf`, restrict changes while older protocol handshakes are active, preserve checksum/verify transforms during active resync/verify, and send protocol/sync-param updates when connected.

Disconnect requests `C_DISCONNECTING` and has recovery branches for peer-required outdating, failed concurrent state changes, and forced disconnect. On success it stops the receiver thread and forces or confirms `C_STANDALONE`. The resource-level `down` command composes demote, disconnect, detach, delete-minor, and delete-resource operations under the resource admin mutex.

Dump callbacks run outside the normal generic-netlink lock, so the file avoids the generated global attribute parser in those paths and uses direct `nla_find` helpers. Iteration state is held in `netlink_callback->args`; resources are protected with RCU and occasional krefs, and each dump emits one object per callback invocation to handle multi-part netlink replies.

## State And Persistence Behavior

The file mutates the core DRBD state machine through `drbd_request_state`, `_drbd_request_state`, `_drbd_set_state`, `conn_request_state`, and related helpers. It coordinates role, disk, peer disk, connection, suspension, sync, and verification state. Many changes are guarded by `adm_mutex`, `state_mutex`, or `req_lock` to avoid conflicting with receiver, sender, or state-engine activity.

Persistent metadata updates are central. Role changes toggle the primary bit in `UI_CURRENT` and call `drbd_md_sync`. Attach reads metadata, checks flags such as `MDF_CONSISTENT`, `MDF_WAS_UP_TO_DATE`, `MDF_FULL_SYNC`, `MDF_PRIMARY_IND`, `MDF_CONNECTED_IND`, and `MDF_PEER_OUT_DATED`, writes bitmaps when full sync is needed, updates `MDF_AL_DISABLED`, and marks metadata dirty. Resize may move metadata offsets, rewrite the activity log and bitmap, update `la_size_sect`, and set full-sync or no-resync behavior. `new-current-uuid` rotates current/bitmap/history UUIDs and can clear the bitmap or skip initial sync when protocol support and just-created UUID state allow it.

Block-device state is also persisted or externally visible through queue-limit updates, exported capacity changes, `set_disk_ro`, `kobject_uevent`, `bd_link_disk_holder`, and `bd_unlink_disk_holder`. RCU-published `disk_conf`, `net_conf`, and resource options are replaced atomically and old copies are released with RCU-aware freeing.

## Dependencies And Integration Points

The file depends on DRBD internals from `drbd_int.h`, protocol constants from `drbd_protocol.h`, request logic from `drbd_req.h`, and state-change notification helpers from `drbd_state_change.h`. It uses generated generic-netlink policy/serializer code from Linux DRBD headers such as `drbd_genl_api.h`, `genl_magic_func.h`, and generated `*_from_attrs` / `*_to_skb` helpers.

Kernel integration includes generic netlink, RCU, krefs, idr iteration, mutexes/spinlocks, block-device open/claim/holder APIs, queue-limit stacking APIs, kernel crypto shash transforms, usermode helper execution, kthreads, timers, wait queues, proc-visible counters, and capability checks. It also integrates with DRBD worker and receiver threads, sender workqueues, bitmap IO, activity-log LRU caches, metadata IO buffers, connection feature negotiation, and multicast event consumers.

## Risks

- Lifetime and locking are delicate. Dump callbacks intentionally run without the generic-netlink lock, so iterator revalidation, RCU coverage, and kref handling are essential to avoid use-after-free or skipped objects.
- Attach/resize error paths cross a point of no return where ownership of backing devices and caches moves to `device->ldev`; regressions can leak block-device references, leave holder links behind, or leave a device stuck in `D_ATTACHING`/diskless transitions.
- Metadata layout changes suspend IO and rewrite AL/bitmap state. A missed lock, early resume, or failed restore could corrupt metadata or produce incorrect resync decisions.
- Policy checks for two primaries, fencing, protocol A, discard-my-data, and older protocol versions protect split-brain and data-loss scenarios; loosening them would be high risk.
- Usermode helpers are synchronous and can freeze configuration progress. Return-code interpretation from fencing helpers directly affects outdating and IO resumption.
- Queue-limit negotiation combines local backend limits, peer DRBD/protocol limits, and negotiated feature flags. Incorrect max bio, discard, write-same, or zeroes limits can surface as failed lower-level IO or data divergence.
- Sensitive configuration is hidden based on `CAP_SYS_ADMIN`; notification paths deliberately exclude sensitive data because any listener may subscribe.

## Test Signals

Useful test signals include generic-netlink admin command coverage for create/delete resource, create/delete minor, attach/detach, connect/disconnect, primary/secondary, resize, disk/net option changes, invalidate/invalidate-peer, pause/resume sync, start verify, new-current-uuid, status, dumps, and initial-state streaming. Integration tests should verify expected DRBD return codes and info strings for missing context, invalid minor/volume, duplicate endpoints, unsupported protocol changes, missing disk, busy AL, forced promotion, and impossible discard/fencing combinations.

State-machine tests should exercise attach failure before and after `D_ATTACHING`, forced detach, `drbd_adm_down` sequencing, reconnect/disconnect races, full-sync bitmap creation, skip-initial-sync UUID flow, online grow resync direction, and fencing helper return codes. Observability tests should compare status/dump output against live resource/device/connection state and verify create/destroy/change notification ordering, `NOTIFY_CONTINUES`, and initial-state termination events. Persistence tests should inspect metadata flags, UUID rotation, bitmap writes, AL layout changes, exported capacity, queue limits, and disk read-only state after each administrative operation.
