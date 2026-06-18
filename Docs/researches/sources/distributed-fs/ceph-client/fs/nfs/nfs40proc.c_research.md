# sources/distributed-fs/ceph-client/fs/nfs/nfs40proc.c

## Purpose
`nfs40proc.c` defines NFSv4.0 minor-version operations for sequence slot handling, lease renewal, migration recovery, lock-owner release, and state recovery policy. It exports `nfs_v4_0_minor_ops` for the common NFSv4 client core.

## Important APIs, Types, And Functions
Key helpers are `nfs40_call_sync_prepare()` and `nfs40_call_sync_done()` for sequence setup/completion, `nfs40_sequence_free_slot()` and `nfs40_sequence_done()` for slot return, `nfs40_open_expired()` for expired open recovery without delegation recovery, `nfs4_proc_async_renew()` and `nfs4_proc_renew()` for lease renewal, `_nfs40_proc_get_locations()` and `_nfs40_proc_fsid_present()` for migration/lease-moved recovery, and `nfs4_release_lockowner()` with its async call ops.

Static operation tables include `nfs40_call_sync_ops`, `nfs40_sequence_slot_ops`, reboot and no-grace recovery ops, state renewal ops, migration recovery ops, and the exported `nfs_v4_0_minor_ops`.

## Control Flow And Integration Points
NFSv4.0 compound calls use sequence setup and slot freeing even though v4.0 sequencing differs from v4.1 sessions. Async renew allocates `nfs4_renewdata`, holds a client ref, calls RENEW with timeout, updates or schedules recovery based on status, and reschedules renewal on release if the client remains referenced. Migration recovery compounds append RENEW to signal the server and refresh leases. Lock-owner release initializes a sequence, sends `RELEASE_LOCKOWNER`, handles lease-related errors, and frees lock state on release.

## State And Persistence Behavior
The file mutates slot table state, NFSv4 state flags, lease timestamps, client refs, lock-owner state, and migration recovery status. `nfs40_test_and_free_expired_stateid()` always returns `-NFS4ERR_BAD_STATEID`, reflecting v4.0 limitations. `nfs40_open_expired()` clears delegation state IDs before reopening expired state.

## Dependencies
Dependencies include NFSv4 XDR procedure tables, sequence/session helpers, lease renewal helpers, migration and fs_locations structures, state recovery machinery, delegation clearing, lock-state lifetime helpers, and NFSv4 tracepoints.

## Risks And Edge Cases
Slot freeing must wake waiters or free slots under the slot-table lock. Async renewal must not reschedule after shutdown and must distinguish `LEASE_MOVED`, `CB_PATH_DOWN`, and normal lease recovery. Migration calls must renew leases only after successful compounds. Lock-owner release is NFSv4.0-only and must ignore later minor versions. Incorrect state recovery ops would break reboot or no-grace recovery.

## Test Signals
Exercise NFSv4.0 lease renewal, server reboot recovery, lease moved migration, callback path down, expired open and lock recovery, lock-owner release after unlock/close, slot table saturation, and fault injection on RENEW, FS_LOCATIONS, FSID_PRESENT, and RELEASE_LOCKOWNER.
