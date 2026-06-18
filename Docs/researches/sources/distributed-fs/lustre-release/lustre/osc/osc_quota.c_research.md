# Research: sources/distributed-fs/lustre-release/lustre/osc/osc_quota.c

## Purpose
`osc_quota.c` implements the OSC-side quota signal cache and the OSC quotactl RPC path. It is not the quota authority. Instead, it records quota pressure returned by OST write replies and uses that cache to force subsequent I/O for affected quota IDs into synchronous/error-visible behavior. It also forwards quota control operations from the client-side OBD interface to the OST using PTLRPC capsules.

## Important APIs, Types, And Functions
The file exports `osc_quota_chkdq()`, `osc_quota_setdq()`, `osc_quota_setup()`, `osc_quota_cleanup()`, and `osc_quotactl()`. The main state is kept in `struct client_obd`: `cl_quota_exceeded_ids` is an xarray keyed by quota ID, storing a bitmask of quota types, `cl_quota_mutex` serializes cache updates, `cl_quota_last_xid` orders server reports, and `cl_root_squash` / `cl_root_prjquota` mirror OST flags.

`md_quota_flag()` maps `USRQUOTA`, `GRPQUOTA`, and `PRJQUOTA` to `OBD_MD_FL*QUOTA` valid bits. `fl_quota_flag()` maps the same quota types to `OBD_FL_NO_*QUOTA` flags in returned `obdo` state.

## Control Flow
`osc_quota_chkdq()` loops over `LL_MAXQUOTAS`, loads each caller-provided quota ID from the xarray, and returns `-EDQUOT` if the stored bitmask contains that quota type. Absence of an ID or absence of the relevant bit means the OSC can proceed without this local quota stop.

`osc_quota_setdq()` is called with the write reply XID, quota IDs, valid bits, and flags from the OST. It ignores replies without quota-valid bits and drops stale replies when a newer `cl_quota_last_xid` exists unless the server set `OBD_FL_NO_QUOTA_ALL`. Under `cl_quota_mutex`, it updates root squash flags, advances `cl_quota_last_xid`, then sets or clears per-type bits in `cl_quota_exceeded_ids`. A zero bitmask erases the xarray entry.

`osc_quotactl()` builds an `OST_QUOTACTL` request with `RQF_OST_QUOTACTL`, sizes the optional `RMF_OBD_QUOTA_ITER` server buffer only for `LUSTRE_Q_ITEROQUOTA`, copies the caller's `struct obd_quotactl` into the request, disables resend with `rq_no_resend`, waits synchronously, and copies back the server reply. Iteration replies allocate a `struct lquota_iter`, attach it to the caller-provided list pointer encoded in `qc_iter_list`, copy the iteration buffer, and zero returned iterator byte counts to indicate ownership transfer.

## State And Persistence
All state is volatile per-client memory. `osc_quota_setup()` initializes the mutex and xarray; `osc_quota_cleanup()` erases all xarray entries and destroys it. The xarray persists only for the OSC lifetime and is rebuilt from future OST replies after reconnect or remount. The file does not persist quota information to disk.

The XID ordering in `osc_quota_setdq()` is important because asynchronous OST replies can arrive out of order. The function still records some old negative quota reports to stay conservative, but it avoids allowing stale clears to remove a newer over-quota indication.

## Dependencies And Integration Points
The write-completion path in `osc_request.c` calls `osc_quota_setdq()` when an `OST_WRITE` reply carries quota valid bits. Higher-level OSC cache and write paths can call `osc_quota_chkdq()` before queuing work. `osc_quotactl()` depends on PTLRPC request allocation/packing, `req_capsule` field access, quota wire formats, and the `class_exp2cliimp()` import.

## Risks
The xarray key is only the numeric quota ID while the value encodes type bits. That is compact, but user/group/project IDs sharing the same integer share one xarray slot; bit handling must remain correct. `qc_iter_list` is passed through an integer field and cast back to a `struct list_head *`, so only trusted in-kernel callers should use that path. Stale reply handling is intentionally conservative, which can force synchronous behavior longer than strictly necessary after reordering.

## Test Signals
Useful tests are quota exhaustion and recovery cases covering user, group, and project quotas; out-of-order write reply simulation to verify stale clears do not remove newer over-quota state; `LUSTRE_Q_ITEROQUOTA` buffer handling; malformed or missing quotactl reply fields returning `-EPROTO`; and setup/cleanup leak checks for the xarray.
