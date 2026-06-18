# sources/distributed-fs/ceph-client/fs/dlm/recover.c

## Purpose
`recover.c` implements the core DLM recovery algorithms after membership changes: status barriers, new master discovery, process-lock reconstruction, LVB recovery, conversion repair, recovered-grant marking, and inactive resource cleanup.

## Important APIs, Types, And Functions
Important exports include `dlm_wait_function()`, `dlm_recover_status()`, `dlm_set_recover_status()`, `dlm_recover_members_wait()`, `dlm_recover_directory_wait()`, `dlm_recover_locks_wait()`, `dlm_recover_done_wait()`, `dlm_recover_masters()`, `dlm_recover_master_reply()`, `dlm_recover_locks()`, `dlm_recovered_lock()`, `dlm_recover_rsbs()`, and `dlm_clear_inactive()`.

Internally it uses recovery lists and an xarray (`ls_recover_list`, `ls_recover_xa`) to track outstanding lookup and lock-copy replies. Resource flags such as `RSB_NEW_MASTER`, `RSB_NEW_MASTER2`, `RSB_RECOVER_LVB_INVAL`, `RSB_RECOVER_CONVERT`, `RSB_VALNOTVALID`, and `RSB_RECOVER_GRANT` drive later stages.

## Control Flow
`dlm_wait_function()` waits for a predicate or recovery stop, with timer-based timeout handling for RCOM waits. Barrier helpers use the lowest node as an aggregator: low node polls every member and then sets an `_ALL` status bit; other nodes poll the low node for the aggregate bit.

Master recovery walks the root RSB list. If no directory mode is configured, `recover_master_static()` assigns master based on hash and purges all MSTCPY locks. Otherwise, resources whose old master left or whose directory lookup established a new master either become locally mastered or are inserted into `ls_recover_xa` and queried with `dlm_send_rcom_lookup()`. Replies call `dlm_recover_master_reply()` to set `res_master_nodeid`, `res_nodeid`, and new-master flags.

Lock recovery sends all local process-copy locks on remastered resources to the new master with `dlm_send_rcom_lock()`. The RSB stays on `ls_recover_list` until replies call `dlm_recovered_lock()` enough times to clear `res_recover_locks_count`.

Final RSB recovery fixes LVB validity and contents, resolves PR/CW conversion conflicts by downgrading incompatible converting grants to NL, and marks resources that may be able to grant waiters after recovery. Inactive resources collected on `ls_slow_inactive` are removed from the rhashtable and freed.

## State And Persistence
Recovery state is in-memory within `struct dlm_ls` and `struct dlm_rsb`: recovery status bits, waitqueues, lists, xarray ids, resource master fields, lock queue node ids/remids, LVB sequence/content, and flags. The recovered state persists for the lockspace lifetime.

## Dependencies And Integration Points
This file depends on rcom, directory hashing/lookup, lock queues, member lists, lowcomms close state, memory allocation for LVBs, and callback/AST behavior. It is orchestrated by `recoverd.c`.

## Risks
Incorrect wait predicates can hang recovery. Resource id tracking differs between list and xarray paths and must keep `ls_recover_list_count` consistent. LVB recovery is subtle: invalidating too often or choosing the wrong highest sequence changes user-visible lock value semantics. Recovery aborts must clear outstanding lists or references leak.

## Test Signals
Tests should cover failed master remapping, no-directory mode, RCOM lookup reply loss/timeout, lock-copy reply counting, recovery abort and restart, LVB selection among grant/convert queues, PR/CW conversion conflict repair, and inactive RSB cleanup.
