# sources/distributed-fs/lustre-release/lustre/mdt/mdt_hsm_cdt_actions.c

## Purpose
This file owns persistent HSM coordinator action logging and the debugfs view over that log. The coordinator stores HSM actions as `HSM_AGENT_REC` records in the `LLOG_AGENT_ORIG_CTXT` catalog so requests survive coordinator restarts and can be replayed/scanned later. It also manages request cookie allocation by deriving the last cookie from the existing llog when needed.

## Important APIs, Types, And Functions
`dump_llog_agent_req_rec()` formats one `llog_agent_req_rec` for HSM debug logging. `cdt_llog_process()` is the shared wrapper around `llog_cat_process()` for action-log scans. `mdt_agent_record_add()` allocates and appends a new persistent action record with status `ARS_WAITING`, archive id, flags, timestamps, and a stable cookie. Internally, `hsm_last_cookie_cb()` and `cdt_update_last_cookie()` reverse-scan the llog to initialize `coordinator::cdt_last_cookie`. The `agent_action_iterator` plus `mdt_hsm_actions_debugfs_*()` sequence operations implement `mdt_hsm_actions_fops`.

## Control Flow
Callers submit an `hsm_action_item` through `mdt_agent_record_add()`. The function builds a variable-size `llog_agent_req_rec`, gets the agent-origin llog context, initializes `cdt_last_cookie` if it is zero, assigns a new cookie except for explicit cancel records, and appends the record with `llog_cat_add()`. Debugfs iteration opens a seq file, allocates an iterator and `lu_env`, gets the llog context on each start, then repeatedly calls `llog_cat_process()` from the saved catalog/index cursor until the seq buffer fills or EOF is reached.

## State And Persistence
The durable state is the HSM action llog. Each record persists request status, archive id, original request flags, create/change timestamps, cookie, FID/data FID, extent, gid, and inline HAI data. `cdt_last_cookie` is in-memory but recoverable by reverse llog scan. Debugfs iterator state tracks the last shown catalog and record index to avoid restarting from the beginning on every seq callback.

## Dependencies And Integration Points
This code depends on Lustre llog APIs, MDT device naming helpers, `struct coordinator`, HSM action definitions, and debugfs/seq_file. It is called by HSM client registration paths, last-unlink HSM remove policy, coordinator scan code, and agent dispatch/update code. `mdt_internal.h` exports its APIs to the broader MDT/HSM subsystem.

## Risks
Missing or invalid `LLOG_AGENT_ORIG_CTXT` returns `-ENOENT`, which prevents new durable HSM requests and hides actions from debugfs. Cookie correctness depends on the reverse scan skipping cancel records and finding the newest non-cancel record; corrupted or out-of-order logs can affect duplicate detection. Debugfs iteration relies on llog catalog/index cursor bookkeeping and can skip or repeat records if llog mutation races are mishandled. Allocation sizes depend on `hai_len`, so malformed HAI lengths would be dangerous if upstream validation regresses.

## Test Signals
Useful signals are HSM archive/restore/remove/cancel tests that verify llog replay across MDT or coordinator restart, cancel records retaining target cookies, debugfs `hsm/actions` showing expected statuses and cookies, and last-cookie monotonicity after restart. Fault-injection coverage should include missing llog context, allocation failures, and llog add/process failures.
