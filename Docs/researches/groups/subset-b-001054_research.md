# Research Group: subset-b-001054

This grouped report covers four DRBD administration, observability, logging, and wire-protocol files. Each file section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_nl.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_nl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_polymorph_printk.h -->
# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_polymorph_printk.h

## Purpose

`drbd_polymorph_printk.h` provides type-directed DRBD logging macros. Callers can pass a `drbd_device`, `drbd_peer_device`, `drbd_resource`, or `drbd_connection` pointer to one macro family and get a consistent log prefix that includes the relevant resource, volume, and minor context. The header also wraps dynamic debug support and provides DRBD assertion helpers.

## Important APIs, Types, And Functions

- `drbd_printk(level, obj, fmt, ...)` is the central polymorphic logging macro. It uses compile-time type selection to choose the right prefix preparation, format string, and argument list.
- `dynamic_drbd_dbg(obj, fmt, ...)` mirrors `drbd_printk` for dynamic debug.
- Convenience macros `drbd_emerg`, `drbd_alert`, `drbd_crit`, `drbd_err`, `drbd_warn`, `drbd_notice`, and `drbd_info` bind standard kernel log levels.
- `drbd_ratelimit` provides a static ratelimit state for repeated warnings.
- `D_ASSERT(x, exp)` logs a failed assertion without changing control flow.
- `expect(x, exp)` evaluates an expression, logs a ratelimited assertion failure if false, and returns the boolean result.
- `drbd_printk_with_wrong_object_type` and `drbd_dyn_dbg_with_wrong_object_type` are intentionally undefined/extern error targets for unsupported object types.

## Control Flow

Each supported DRBD object type has four helper macros: prep, format, args, and unprep. For a device or peer device, the prep block derives the backing `drbd_device` and `drbd_resource`, and the format includes `drbd resource/volume drbdminor`. For a resource or connection, the prefix is resource-oriented.

`drbd_printk` nests `__builtin_choose_expr` calls. Each branch first supplies a compile-time `__builtin_types_compatible_p` condition, then a statement expression that prepares context and calls `printk`. Because the choice is compile-time, unsupported object types fall through to the wrong-type symbol. Dynamic debug follows the same pattern but creates dynamic-debug metadata, checks `DYNAMIC_DEBUG_BRANCH`, and calls `__dynamic_pr_debug` only when enabled.

When `CONFIG_DYNAMIC_DEBUG` is absent, the header provides stub definitions that preserve compile-time references while making dynamic debug branches false and avoiding runtime output.

## State And Persistence Behavior

The header does not own persistent state. Its only local state is the static ratelimit state created inside `drbd_ratelimit`. Logging reads object fields such as `resource->name`, `device->vnr`, and `device->minor`, so call sites must pass live objects and hold whatever references or locks make those fields safe in context. Assertion helpers do not halt execution or mutate DRBD state.

## Dependencies And Integration Points

This header relies on GCC-style builtins and statement expressions, Linux `printk` log levels, dynamic debug macros, ratelimit APIs, and DRBD core structures. It is included by DRBD internals to standardize diagnostic output across resource-, connection-, device-, and peer-device-oriented code.

## Risks

- The polymorphism is compile-time macro machinery, so type qualifiers and pointer type mismatches matter. Passing a wrapper, void pointer, or stale pointer will either fail compilation through the wrong-type target or log invalid context.
- The prefix helpers dereference object relationships without NULL checks. Callers must not use these macros before object linkage is established or after teardown begins.
- Stubbed dynamic debug support must remain compatible with kernel dynamic-debug macro signatures; drift in upstream dynamic-debug APIs can break builds.
- `D_ASSERT` and `expect` are diagnostics, not enforcement. Code paths that require hard failure must not rely on them for safety.

## Test Signals

Build coverage is the primary signal: calls with each supported object pointer type should compile, and unsupported types should fail. Runtime tests can validate emitted prefixes for devices, peer devices, resources, and connections. Dynamic-debug builds should confirm disabled debug sites are quiet and enabled sites include the same contextual prefix. Ratelimit behavior can be observed by repeated `expect` failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_polymorph_printk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_proc.c -->
# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_proc.c

## Purpose

`drbd_proc.c` renders the legacy `/proc/drbd` status view using `seq_file`. It reports module/protocol version information, per-minor connection/role/disk state, IO counters, pending counters, write-ordering mode, out-of-sync amount, optional synchronization or verification progress, and optional lower-level cache statistics. This is an observability file; it does not configure DRBD.

## Important APIs, Types, And Functions

- `struct proc_dir_entry *drbd_proc` is the procfs entry handle exported for DRBD proc registration elsewhere.
- `drbd_seq_show(struct seq_file *seq, void *v)` is the main seq_file show callback.
- `drbd_get_syncer_progress` computes total sync/verify work, remaining bitmap bits, and per-mille completion.
- `drbd_syncer_progress` formats the progress bar, percentage, remaining/total amount, estimated finish time, recent and average speed, desired sync rate, stalled marker, and optional sector-position detail.
- `seq_printf_with_thousands_grouping` formats kB/sec speeds with comma grouping.

## Control Flow

`drbd_seq_show` prints a header with `REL_VERSION`, generic-netlink API version, supported protocol range, and build tag. It then takes `rcu_read_lock` and iterates `drbd_devices` by minor through `idr_for_each_entry`. It inserts blank lines for gaps in minor numbering.

For an unconfigured device in `C_STANDALONE`, `D_DISKLESS`, secondary state, it prints `cs:Unconfigured`. Otherwise it snapshots `device->state`, derives the connection-state string, reads the first peer connection's network configuration via RCU to determine protocol letter, and emits the classic `/proc/drbd` line with role, disk states, protocol, suspension flags, congestion reason, AL suspension marker, network/disk counters, pending counters, epoch count, write ordering, and out-of-sync kB.

If the connection state is sync source, sync target, verify source, or verify target, `drbd_syncer_progress` appends detailed progress. Optional details are gated by `drbd_proc_details`: level 1 prints resync/activity-log cache stats and detailed sector position; level 2 adds blocked-on-activity-log count.

## State And Persistence Behavior

This file does not persist or mutate DRBD state. It reads live counters, bitmap weights, local-device metadata availability, activity-log suspension flags, sync marks, verify positions, and connection configuration. Some values are inherently approximate because they race with live replication, resync, verification, and state changes; the code explicitly clamps impossible progress values when state changes race with `rs_total` resets.

The progress calculations use bitmap units (`BM_BLOCK_SIZE`) and convert to kB or MB for display. Rolling speed estimates are based on `rs_mark_left`, `rs_mark_time`, `rs_last_mark`, `rs_start`, and `rs_paused`. Stalled detection is based on an older sync mark exceeding 180 seconds.

## Dependencies And Integration Points

The file integrates with procfs and `seq_file`, DRBD global device idr state, RCU-protected network configuration, DRBD bitmap helpers, local-device reference helpers (`get_ldev_if_state`, `put_ldev`), activity-log/resync cache stats, DRBD state-string helpers, and global tunable `drbd_proc_details`. It is a compatibility/status interface for users and scripts that still consume `/proc/drbd`, complementing the generic-netlink status APIs in `drbd_nl.c`.

## Risks

- Output is a live, unlocked status snapshot. Multi-field consistency is best-effort; scripts must tolerate races and transient combinations.
- `first_peer_device(device)` is assumed valid in configured paths. Object lifetime and device initialization order must preserve that assumption.
- Progress arithmetic intentionally avoids overflow on 32-bit systems. Changes to bitmap sizing, sync mark units, or per-mille math need careful type review.
- The legacy text format is likely consumed by external tools. Cosmetic changes can be compatibility regressions.
- `drbd_proc_details` increases detail and can expose lower-level internal counters; changes should consider output volume and locking.

## Test Signals

Tests should read `/proc/drbd` across unconfigured, standalone, connected, primary/secondary, diskless, syncing, verifying, and paused-sync states. Golden-output checks should cover the version header, minor gaps, protocol letters, suspension flags, write-ordering characters, counter scaling, and out-of-sync units. Resync/verify tests should validate progress bounds, stalled marker behavior, desired sync rate display, and optional detail output at `drbd_proc_details` levels 1 and 2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_protocol.h -->
# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_protocol.h

## Purpose

`drbd_protocol.h` defines the DRBD on-wire protocol command numbers, feature flags, packet headers, and packed payload structures used by the replication data and metadata sockets. It is a compatibility-critical contract between DRBD peers and between protocol-version-specific send/receive code paths.

## Important APIs, Types, And Functions

- `enum drbd_packet` assigns stable command IDs for data packets, resync packets, barriers, bitmaps, authentication, state changes, pings/acks, online verify, checksum resync, compressed bitmap transfer, disconnect/state requests, trim/write-same/zeroes, handshake packets, and feature negotiation.
- Header structures `p_header80`, `p_header95`, and `p_header100` describe protocol-era packet headers. They differ in length width, volume field support, and padding/alignment.
- Data path payloads include `p_data`, `p_trim`, `p_wsame`, `p_block_ack`, `p_block_req`, and `p_block_desc`.
- Negotiation and control payloads include `p_connection_features`, `p_protocol`, `p_uuids`, `p_rs_uuid`, `p_sizes`, `p_state`, `p_req_state`, `p_req_state_reply`, and older `p_drbd06_param`.
- Resync parameter layouts include `p_rs_param`, `p_rs_param_89`, and `p_rs_param_95`, reflecting protocol-version evolution.
- Feature flags `DRBD_FF_TRIM`, `DRBD_FF_THIN_RESYNC`, `DRBD_FF_WSAME`, and `DRBD_FF_WZEROES` advertise optional wire capabilities.
- Data packet flags `DP_RW_SYNC`, `DP_MAY_SET_IN_SYNC`, `DP_FUA`, `DP_FLUSH`, `DP_DISCARD`, `DP_SEND_RECEIVE_ACK`, `DP_SEND_WRITE_ACK`, `DP_WSAME`, and `DP_ZEROES` encode block-layer semantics and protocol acknowledgement expectations.
- `enum drbd_conn_flags` defines connection flags sent in `p_protocol`, including discard-my-data and dry-run.
- `enum drbd_bitmap_code` defines compressed bitmap encoding values.
- `DRBD_SOCKET_BUFFER_SIZE` fixes bitmap packet sizing to 4096 bytes.

## Control Flow

This header has no executable control flow, but it controls runtime dispatch in receiver and sender code. Incoming packet command IDs select decode handlers, and negotiated protocol version/features determine which header and payload layout is valid. For example, older protocol 80 headers can only represent smaller payload lengths, protocol 95 supports larger packets, and protocol 100 includes a volume number. Optional queue limits in `p_sizes` are present only when the negotiated feature set includes `DRBD_FF_WSAME`.

Feature flags gate higher-level behavior in files such as `drbd_nl.c`: TRIM/discard support depends on `DRBD_FF_TRIM`, maximum discard sizing changes with `DRBD_FF_WSAME`, thin resync can use `P_RS_THIN_REQ`/`P_RS_DEALLOCATED`, and write-zeroes support depends on `DRBD_FF_WZEROES`. Resync parameter structures evolve by protocol version to add checksum algorithms and controller settings while preserving older layouts.

## State And Persistence Behavior

The structures represent transient wire state rather than local persistent metadata. However, many fields carry persistent or state-machine-significant values: UUID arrays, current/bitmap sync UUIDs, disk sizes, requested user size, current exported size, queue limits, role/disk/connection state, resync rates, protocol mode, after-split-brain policies, and authentication/integrity algorithm names. Mis-encoding these fields can cause persistent metadata divergence, incorrect resync decisions, or incompatible peer negotiation.

All packet structures are packed and use network byte order except documented local echo handles such as `block_id` and barrier fields. Alignment notes are explicit because payload offsets must stay long-aligned across 32-bit and 64-bit systems.

## Dependencies And Integration Points

The header depends on Linux fixed-width integer types, `SHARED_SECRET_MAX`, and DRBD constants from surrounding headers. It is consumed by DRBD sender, receiver, handshake, bitmap, resync, online-verify, request, and configuration code. It also informs queue-limit negotiation and discard/write-same/write-zeroes behavior in administrative code.

## Risks

- Command IDs, flags, structure layout, and field meanings are wire ABI. Changing them without a protocol version bump or feature flag would break interoperability.
- Packed structures and flexible arrays require careful size checks in send/receive code to avoid overreads, truncation, or alignment bugs.
- Some comments document overloaded feature semantics, especially `DRBD_FF_WSAME`; tests and code must treat those historical meanings consistently.
- The distinction between discard and write-zeroes is data-integrity sensitive on thin-provisioned storage. Incorrect `DP_DISCARD`/`DP_ZEROES` or feature negotiation can expose stale backend data or force unwanted allocation.
- Header choice by protocol version affects maximum packet sizes. Mismatches can corrupt stream parsing.

## Test Signals

Compatibility tests should connect peers across supported protocol versions and verify header selection, feature negotiation, max bio/discard/write-zeroes behavior, resync parameter exchange, UUID exchange, state-change requests/replies, authentication, compressed bitmap transfer, and online verify packets. Static/build tests should assert packed sizes and offsets for wire structs. Fuzz or negative tests should reject invalid lengths, unsupported optional commands, unknown bitmap encodings, and inconsistent feature/command combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_protocol.h -->
