<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/AuthMonitor.cc -->
# sources/distributed-fs/ceph/src/mon/AuthMonitor.cc

## Purpose
`AuthMonitor.cc` implements Ceph monitor authority for authentication state. It owns the Paxos-backed mutation path for CephX auth entries, rotating service keys, pending key promotion, global connection id allocation, bootstrap key creation, auth command handling, OSD key lifecycle helpers, auth handshake preprocessing, and auth map format upgrades.

## Important APIs, types, and functions
The main implementation is `AuthMonitor`, backed by `mon.key_server`, `pending_auth`, `max_global_id`, and `last_allocated_id`. Incremental mutation is funneled through `push_cephx_inc()`, `add_entity()`, `remove_entity()`, `process_used_pending_keys()`, and `increase_max_global_id()`. Paxos hooks are `create_initial()`, `update_from_paxos()`, `create_pending()`, `encode_pending()`, `encode_full()`, `get_trim_to()`, `preprocess_query()`, and `prepare_update()`.

Authentication flow is handled by `prep_auth()`, which selects an auth service handler, enforces CephX signature/version policy, assigns `peer_global_id`, drives `start_session()` or `handle_request()`, and triggers fast authentication completion. Command flow is split between read-only `preprocess_command()` for `auth export/get/list/print-key` and mutating `prepare_command()` for `auth add/import/get-or-create/fs authorize/caps/del/rotate/pending-key` operations. OSD provisioning calls use `validate_osd_new()`, `do_osd_new()`, `validate_osd_destroy()`, and `do_osd_destroy()`. Capability correctness is centralized in `valid_caps()`, `_check_and_encode_caps()`, `_merge_caps()`, and `_gen_wanted_caps()`. Upgrade helpers `_upgrade_format_to_dumpling()`, `_upgrade_format_to_luminous()`, and `_upgrade_format_to_mimic()` migrate stored cap/profile defaults.

## Control flow
On initial creation, the monitor clears secrets, seeds rotating keys, imports or creates bootstrap keyring entries, initializes `max_global_id`, and records auth format version 3. After each committed version, `update_from_paxos()` loads the latest full auth snapshot if available, then replays incremental records until `mon.key_server` reaches `get_last_committed()`. Version 1 cleanup removes the mkfs keyring once imported.

During normal operation, `tick()` and `on_active()` check whether the global-id allocation window is low, whether used pending keys need to be promoted, and whether rotating CephX keys need renewal. Leaders append incrementals and propose; peons send `MMonGlobalID` or `MMonUsedPendingKeys` requests to the leader and retry after proposals.

Auth handshakes enter through `preprocess_query()` or `prepare_update()`. Initial auth messages decode supported protocols and entity identity, filter CephX if required message features are absent, select cluster or service auth policy, allocate a global id, and run the selected service handler. If ids are exhausted, the request is waitlisted or forwarded to the leader until a new id range is committed.

Mutating commands validate JSON command maps, session presence, entity names, caps, supplied keyrings, and idempotency against both committed `key_server` state and uncommitted `pending_auth`. Successful mutations append CephX `AUTH_INC_ADD` or `AUTH_INC_DEL` incrementals and wait for the next commit before replying.

## State and persistence behavior
Auth state is Paxos persisted as versioned incrementals plus periodic full snapshots. Incrementals encode either `GLOBAL_ID` or CephX auth data; full snapshots encode `max_global_id` and the complete `KeyServer`. `encode_pending()` also recomputes `AUTH_BAD_CAPS` health checks by validating committed plus pending caps. Trimming keeps roughly twice `paxos_max_join_drift` versions on leaders.

`max_global_id` is committed cluster state, while `last_allocated_id`, `mon_num`, and `mon_rank` coordinate local id striping under `mon.auth_lock`. Pending key state lives inside `EntityAuth.pending_key` and is committed to `key` once clients report use after Quincy. Format upgrades are staged through normal pending incrementals, so upgrade effects are replicated like any other auth change.

## Dependencies and integration points
This file integrates with `PaxosService`, `MonitorDBStore`, `CephxKeyServer`, monitor sessions, `Messenger` connections, auth service handlers, `KeyRing`, MDS/OSD/MGR cap parsers, `ConfigMonitor` subscription refresh, OSD monitor provisioning workflows, MDS filesystem maps for `fs authorize`, and monitor feature/release gates. It sends and receives `MAuth`, `MAuthReply`, `MMonGlobalID`, `MMonUsedPendingKeys`, and `MMonCommand`.

## Risks and edge cases
Global-id exhaustion is sensitive because auth must sometimes become writable solely to allocate ids. `_assign_global_id()` depends on correct monitor rank/size setup and can return zero during rank changes. Pending-key code must avoid double-applying uncommitted entity updates; `auth get-or-create-pending` currently pushes the same incremental twice, which is worth test attention. `exists_and_matches_entity()` treats mismatched caps as errors for idempotent flows. Capability validation is configurable, so invalid non-mon caps may persist when full validation is disabled but later surface in health checks. Format upgrades use quorum feature gates and must remain rolling-upgrade safe.

## Test signals
Useful signals include mon bootstrap with and without mkfs keyring, auth command idempotency, malformed keyring import failure, cap parser errors and `AUTH_BAD_CAPS` health output, CephX signature/version rejection paths, global-id preallocation refill on leader and peon, OSD new/destroy key lifecycle, pending-key create/clear/commit/use promotion across Quincy gates, `fs authorize` cap merging, auth map full snapshot replay, and upgrade tests from format 0, 1, and 2 clusters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/AuthMonitor.cc -->
