# sources/distributed-fs/lustre-release/lustre/mdt/mdt_hsm_cdt_client.c

## Purpose
This file is the coordinator-facing implementation of client HSM action registration and action lookup. It validates `hsm_action_list` requests, detects redundant or cancel-target requests in the persistent llog, enforces user/group/other HSM permission masks, checks current file HSM state, records needed actions, and exposes an optimized restore-running query.

## Important APIs, Types, And Functions
`mdt_hsm_add_actions()` is the main entry for registering a HAL. `hsm_find_compatible()` and `hsm_find_compatible_cb()` scan existing llog records to fill cookies for duplicate or cancel requests. `hsm_action_is_needed()` suppresses no-op archive/restore/remove requests unless forced. `hal_is_sane()` validates basic HAL shape. `hsm_action_permission()` applies read-only and coordinator request-mask policy. `mdt_hsm_register_hal()` records each needed action, handles archive-id defaults, and takes restore handles. `mdt_hsm_restore_is_running()` checks the restore hash. `mdt_hsm_get_action()` reports the active action/status/extent for a FID and enriches started actions with in-memory progress totals.

## Control Flow
`mdt_hsm_add_actions()` rejects stopped/stopping coordinator state, validates the HAL, scans for compatible llog records where needed, and delegates per-item processing. `mdt_hsm_register_hal()` initializes data FID defaults, skips redundant non-cancel requests and cancel-without-target requests, fetches HSM metadata, applies permission checks, tests if the action is needed and compatible, derives archive id from the request, file HSM metadata, or coordinator default, takes an exclusive restore handle for whole-file restores, then appends an action llog record. If any restore was recorded and `CDT_NONBLOCKING_RESTORE` is set, it returns `-ENODATA` after recording to signal the nonblocking path while still waking the coordinator.

## State And Persistence
New requests are persisted only by `mdt_agent_record_add()`. Restore exclusion state is in `coordinator::cdt_restore_hash` through `cdt_restore_handle_add()` and is queried by `mdt_hsm_restore_is_running()`. Existing request compatibility is derived from the llog, while progress detail in `mdt_hsm_get_action()` is read from the active request table.

## Dependencies And Integration Points
The file depends on MDT object lookup and HSM xattr fetch via `mdt_hsm_get_md_hsm()`, action compatibility rules via `mdt_hsm_is_action_compat()`, llog scanning/addition from `mdt_hsm_cdt_actions.c`, active request lookup from `mdt_hsm_cdt_requests.c`, coordinator reference/event handling, capability checks, and `mdt_rdonly()` for non-restore write restrictions.

## Risks
This path must align permission masks with the `HSMA_*` enum values; mismatches can authorize or deny the wrong action. Restore requests only support whole-file extents here and reject nonzero offsets. Cancel-by-FID depends on llog search of waiting/started records and ignores explicit-cookie cancels. Admin exceptions allow remove/cancel even when the Lustre object is missing, so caller capability checks are security-sensitive. The function mutates HAL cookies/archive ids during compatibility processing, which callers must treat as in/out state.

## Test Signals
Useful tests include duplicate archive/restore suppression, cancel by FID and by cookie, forced actions, permission masks for owner/group/other users, read-only MDT behavior, restore lock exclusion including the LU-9266/LU-15132 race paths, nonblocking restore `-ENODATA`, and `mdt_hsm_get_action()` progress reporting for started requests.
