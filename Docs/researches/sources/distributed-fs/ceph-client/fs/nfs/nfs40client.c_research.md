# sources/distributed-fs/ceph-client/fs/nfs/nfs40client.c

## Purpose
`nfs40client.c` implements NFSv4.0 client initialization, shutdown, callback-path recovery, and server trunking discovery. It handles the NFSv4.0 client ID confirmation model and callback identifier swapping when two transports are discovered to reach the same server.

## Important APIs, Types, And Functions
`nfs40_init_client()` allocates and initializes a transport slot table for NFSv4.0. `nfs40_shutdown_client()` tears it down. `nfs40_handle_cb_pathdown()` marks the lease expired and returns all delegations after `NFS4ERR_CB_PATH_DOWN`; `nfs4_schedule_path_down_recovery()` also schedules the state manager. `nfs40_discover_server_trunking()` sends `SETCLIENTID`, stores the returned clientid/confirm verifier, and delegates to `nfs40_walk_client_list()` to find an existing matching client. `nfs4_swap_callback_idents()` updates per-net callback IDR ownership if the kept client should inherit the callback ident learned by the dropped client.

## Control Flow And Integration Points
Trunking discovery uses the per-net `nfs_client_list` and `cb_ident_idr` from `netns.h`. `nfs40_walk_client_list()` walks existing clients, uses `nfs4_match_client()` for owner/address matching, performs `SETCLIENTID_CONFIRM` against candidates, and on success returns a referenced existing client, swaps callback identifiers, updates `cl_confirm`, and marks the client ready. Timeout or restart cases schedule callback path recovery.

## State And Persistence Behavior
Persistent state affected includes `cl_slot_tbl`, `cl_clientid`, `cl_confirm`, `cl_cb_ident`, `cl_state`, delegation state, per-net callback IDR entries, and client refcounts. Discovery deliberately treats the newly allocated client as the last list item and may return a different existing client.

## Dependencies
Dependencies include NFSv4 session/slot helpers, callback service state, delegation expiration, per-network namespace state, state manager scheduling, SETCLIENTID/CONFIRM procedures, and client refcount/list locking.

## Risks And Edge Cases
Callback identifier swaps must be protected by `nfs_client_lock` and keep IDR entries consistent. Confirm verifiers are used to avoid false trunking matches when servers coincidentally return the same clientid-like data. Reference handling around `prev`, `pos`, and `result` is subtle. If callback path changes inadvertently, recovery must be scheduled to avoid stale delegation behavior.

## Test Signals
Test NFSv4.0 mounts, multi-address trunking discovery, callback channel changes, delegation return after `CB_PATH_DOWN`, slot table allocation failure, server reboot during trunking discovery, and list/refcount validation with lockdep/KASAN.
