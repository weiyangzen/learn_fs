# sources/distributed-fs/lustre-release/lustre/mdt/mdt_hsm_cdt_requests.c

## Purpose
This file owns the in-memory active HSM request table used by the coordinator after actions have been assigned to agents. It indexes requests by cookie, maintains request reference counts and per-action counters, tracks byte-progress intervals, handles completion statistics, and provides debugfs output for active requests.

## Important APIs, Types, And Functions
`cdt_request_cookie_hash_ops` defines the `cfs_hash` cookie index over `cdt_agent_req::car_cookie_hash`. `mdt_cdt_alloc_request()` and `mdt_cdt_free_request()` manage request memory and embedded copied llog records. `mdt_cdt_add_request()`, `mdt_cdt_find_request()`, `mdt_cdt_update_request()`, and `mdt_cdt_remove_request()` are the public active-request lifecycle. `hsm_update_work()` merges progress extents in an interval tree. The `mdt_hsm_active_requests_proc_*()` seq operations back `mdt_hsm_active_requests_fops`.

## Control Flow
Allocation copies a persistent `llog_agent_req_rec` into an `hsm_mem_req_rec`, initializes the interval tree, and starts the kref. Adding requires a non-cancel action, inserts into the cookie hash under `cdt_request_lock`, links it on `cdt_request_list`, takes the list reference, updates agent stats, and increments total/archive/restore/remove counters. Lookup uses the hash and returns a referenced request. Progress update finds by cookie, refreshes the change timestamp, merges reported extents for non-remove successful progress, and updates agent success/failure counters on completed progress. Removal deletes from hash and list, decrements action counters and request count, drops cancel references, wakes the coordinator when the active count becomes zero, and releases the list reference.

## State And Persistence
The active table is in-memory state protected by `cdt_request_lock`; the persistent copy remains in the llog and is modified elsewhere. Each request holds a copied record pointer, agent UUID, reference count, optional paired cancel request, and interval-tree progress state. Progress intervals are coalesced under `cdt_req_progress::crp_lock` and represented as total bytes moved.

## Dependencies And Integration Points
This code integrates with `cfs_hash`, kernel rb interval-tree helpers, HSM progress RPC handling, coordinator scan/dispatch, agent statistics, debugfs, and llog-memory record structures. `mdt_hsm_get_action()` reads `car_progress.crp_total`, and agent dispatch/removal paths rely on request count and wakeup behavior.

## Risks
Reference ownership is nontrivial: hash lookup, list insertion, cancel pairing, and debug/scan users must balance `mdt_cdt_get_request()`/`put`. Progress interval merging treats adjacent intervals as one range and must guard overflow when computing `offset + length - 1`. Removing a request with `car_cancel` drops multiple references tied to `mdt_hsm_add_hsr()` behavior. If request counters get out of sync with hash/list operations, coordinator throttling and debug output become misleading.

## Test Signals
Test active request add/find/remove under duplicate-cookie conditions, progress interval merging with overlapping/adjacent/sparse ranges, overflow rejection, completion success/failure stats, cancel-paired request removal, coordinator wakeup when the active list drains, and debugfs `active_requests` output while requests are concurrently updated.
