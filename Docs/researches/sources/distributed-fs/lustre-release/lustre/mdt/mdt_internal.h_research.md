# sources/distributed-fs/lustre-release/lustre/mdt/mdt_internal.h

## Purpose
This is the central private MDT header. It defines the core MDT device, object, request-thread, HSM coordinator, HSM request, agent, restore-handle, lock, and directory restriper data structures, plus internal prototypes and inline helpers shared across MDT implementation files.

## Important APIs, Types, And Functions
Major types include `mdt_file_data`, `coordinator`, `mdt_device`, `mdt_object`, `mdt_lock_handle`, `mdt_reint_record`, `mdt_thread_info`, `cdt_req_progress`, `cdt_agent_req`, `hsm_agent`, `cdt_restore_handle`, `hsm_mem_req_rec`, and `hsm_scan_request`. Important inline helpers include `cdt_mdt_state2str()`, `mdt_th_info()`, `hsr_get_archive_id()`, object get/put/FID conversion helpers, layout interpretation helpers for DoM/FLR/overstriping, `agent_req_in_final_state()`, `mdt_rdonly()`, `mdt_check_resent()`, `is_identity_get_disabled()`, `mdt_fid_lock()/unlock()`, `mdt_hsm_cdt_event()`, `mdt_changelog_allow()`, `mdt_check_enc()`, and `mdt_dom_check_for_discard()`.

## Control Flow
The header does not implement request handlers directly, but it defines the call graph contracts: request handlers obtain `mdt_thread_info` from the `lu_env`, operate on `mdt_device` and `mdt_object`, use lock handles for LDLM/PDO/cross-MDT locks, unpack requests into `mdt_reint_record`, and call lower `md_object`/`dt_object` operations. HSM coordinator paths use `coordinator` state, agent lists, request lists, cookie hash, restore hash, and event signaling. IO paths use the exported DoM/BRW/fallocate/punch/glimpse prototypes.

## State And Persistence
`mdt_device` aggregates persistent-target attachments, namespace, bottom DT device, identity caches, root squash, quota connection, coordinator, and tunables. `mdt_object` contains per-object runtime state such as write/open/lease counts, locks, DoM semaphore, layout/SOM state, and restripe linkage. `coordinator` contains runtime HSM state, but its requests are mirrored in the HSM action llog through implementation files. `mdt_thread_info` is per-thread scratch state and must be initialized/reset carefully because parts are explicitly not initialized.

## Dependencies And Integration Points
The header ties MDT code to Lustre OBD, LU, MD, DT, LDLM, FLD, quota, nodemap, request capsule, HSM, lprocfs, and encryption subsystems. It is included by all files in this subset and exports their public internal symbols to the rest of MDT. Compatibility conditionals and connection-flag helpers make it a boundary between wire protocol features and server behavior.

## Risks
The lock order for HSM coordinator locks is documented here (`cdt_agent_lock`, `cdt_counter_lock`, `cdt_request_lock`) and violations can deadlock. `mdt_thread_info` has fields that are intentionally uninitialized, so handlers must only read initialized members for their phase. Inline helpers often assume non-null exports, devices, or request bodies and rely on upstream validation. Structure fields define concurrency boundaries; changing them requires auditing locking, replay, recovery, and on-wire compatibility.

## Test Signals
Compile-time coverage is important because this header is broad. Runtime signals include request replay/reconstruction, HSM coordinator state transitions, DoM IO, encryption-aware/unaware access, changelog RBAC checks, DNE/striped-directory feature negotiation, resource-id checks, and old-client compatibility paths. Static analysis should flag lock-order misuse and unchecked assumptions around `mti_pill`, `mti_exp`, and optional reply fields.
