# sources/distributed-fs/ceph-client/fs/lockd/svcproc.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/svcproc.c` implements the NLM version 1 and version 3 server procedure handlers and procedure tables. It decodes legacy lockd arguments, resolves hosts and files, invokes the shared server lock/share implementation, handles async response procedures, status casting, statd notifications, and exports `nlmsvc_version1` and `nlmsvc_version3`. The source was read as a complete 838-line file for this report.

## Important APIs, Types, and Functions

Core helpers include `cast_status`, `nlmsvc_retrieve_args`, `__nlmsvc_proc_test`, `__nlmsvc_proc_lock`, `__nlmsvc_proc_cancel`, `__nlmsvc_proc_unlock`, `__nlmsvc_proc_granted`, and `nlmsvc_callback`. Important procedure functions include `nlmsvc_proc_null`, TEST, LOCK, CANCEL, UNLOCK, GRANTED, TEST_MSG, LOCK_MSG, CANCEL_MSG, UNLOCK_MSG, GRANTED_MSG, SHARE, UNSHARE, NM_LOCK, FREE_ALL, SM_NOTIFY, GRANTED_RES, and `nlmsvc_proc_unused`. Important data includes `nlmsvc_procedures[24]`, `union nlmsvc_xdrstore`, `nlm1svc_call_counters`, `nlm3svc_call_counters`, `nlmsvc_version1`, and `nlmsvc_version3`.

## Control Flow

The central dispatcher in `svc.c` decodes into `struct nlm_args`, `struct nlm_res`, or `struct nlm_reboot` based on `nlmsvc_procedures[]`. `nlmsvc_retrieve_args` verifies nfsd callback binding, resolves an `nlm_host`, optionally monitors it through NSM, looks up an `nlm_file`, and initializes the embedded VFS `file_lock`. Each procedure performs grace checks, calls the corresponding shared operation, casts internal statuses to legacy protocol statuses, and releases lock-owner/host/file references. `_MSG` variants allocate an async `nlm_rqst` and send a reply procedure before returning a void RPC response.

## State and Persistence Behavior

This file owns no durable state. It uses per-RPC argument/result storage and transient host/file/call references. Shared state is maintained by the host cache, `svcsubs.c` file table, `svclock.c` blocked locks, and `svcshare.c` share lists. Per-CPU call counters persist while the module is loaded.

## Dependencies and Integration Points

It depends on hand-written NLM XDR functions from `xdr.c`/`xdr.h`, host lookup and NSM monitoring, `nlmsvc_lock_operations`, VFS lock helpers, shared lock/share/free-resource helpers, and SUNRPC async reply support. Version objects are consumed by the program table in `svc.c`.

## Risks and Edge Cases

Status translation differs with `CONFIG_LOCKD_V4`: internal stale-fh and failed statuses are collapsed for v1/v3, while v4-aware builds preserve more codes when possible. Reference release paths are repetitive and must stay balanced. FREE_ALL passes `filp == NULL` to retrieve only the host. Legacy `_RES` procedures mostly decode void or results and ignore content except GRANTED_RES. The private SM_NOTIFY path must remain privileged-only.

## Test Signals

Run NLMv1 and NLMv3 TEST/LOCK/CANCEL/UNLOCK/GRANTED plus SHARE/UNSHARE/NM_LOCK/FREE_ALL. Exercise `_MSG` procedures and callback response generation. Verify status casting for stale handles, deadlocks, failed opens, and drop-reply. Test grace and reclaim behavior. Send statd notifications from privileged and unprivileged sources. Confirm per-version procedure counts and XDR storage sizes through build and RPC smoke tests.
