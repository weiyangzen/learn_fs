<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/recovery.c -->
# sources/distributed-fs/ceph-client/fs/gfs2/recovery.c

## Purpose
`recovery.c` implements GFS2 journal replay and recovery result reporting. It reads journal blocks, builds revoke replay state, validates log headers, iterates active journal descriptors, replays non-revoked metadata and journaled data via lops hooks, repairs statfs accounting from log headers, writes clean recovery headers, and coordinates asynchronous recovery work.

## Important APIs, types, and functions
External APIs are `gfs2_replay_read_block`, `gfs2_revoke_add`, `gfs2_revoke_check`, `gfs2_revoke_clean`, `__get_log_header`, `gfs2_recover_func`, `gfs2_recover_journal`, and `gfs2_log_pointers_init`. Internal helpers include `get_log_header`, `foreach_descriptor`, `clean_journal`, `gfs2_recovery_done`, `update_statfs_inode`, and `recover_local_statfs`. The global workqueue `gfs2_recovery_wq` is defined here and allocated in `main.c`.

## Control Flow
`gfs2_recover_journal` marks a journal descriptor with `JDF_RECOVERY`, queues `gfs2_recover_func`, and optionally waits for the bit to clear. The worker refuses recovery on withdrawn or spectator mounts. For foreign journals, it tries to acquire the journal glock exclusively with `LM_FLAG_TRY`; busy journals are treated as another node doing the work. It also locks the journal inode glock shared. It validates the journal descriptor, finds the journal head with `gfs2_find_jhead`, and skips replay if the head has `GFS2_LOG_HEAD_UNMOUNT`.

If replay is required, the worker locks `sd_freeze_mutex`, rejects frozen or read-only-block-device cases, and may temporarily allow recovery on a read-only mount if the device is writable and recovery has not yet been checked. Under `sd_log_flush_lock` read mode, it runs two descriptor passes from `lh_tail` to `lh_blkno`: pass 0 lets lops collect revokes, pass 1 replays metadata and journaled data. It then applies local statfs changes from the log header to the master statfs inode, zeros the local statfs inode for that jid, writes a clean recovery log header, and releases locks. Recovery of the local journal initializes `sd_log_sequence`, tail, head, and flush pointers from the recovered head. Completion sends a uevent and invokes `lm_recovery_result` so `lock_dlm.c` can clear or retain control-LVB jid bits.

## State and Persistence
Persistent state read during recovery includes journal log headers, descriptors, revoke records, metadata/data payloads, and statfs deltas stored in log headers. Persistent writes include replayed in-place metadata/data buffers, statfs inode updates, zeroed local statfs changes, and a clean recovery header marked with `GFS2_LOG_HEAD_RECOVERY`. In-memory state includes `jd_revoke_list`, replay counters, `jd_recover_error`, `JDF_RECOVERY`, and recovery status fields in `lm_lockstruct`.

## Dependencies and Integration Points
Recovery depends on journal extent mapping and metadata readahead, log header parsing and writing from `log.c`, lops scan hooks from `lops.c`, glocks and journal glops, statfs helpers, freeze/read-only superblock state, DLM lock-manager result callbacks, uevents, and the global recovery workqueue. `ops_fstype.c` invokes recovery during mount; `lock_dlm.c` schedules recovery for failed jids.

## Risks
Replay must not run while the filesystem is frozen or on a read-only block device. The two-pass scan requires revokes to be collected before payload replay; wraparound logic in `gfs2_revoke_check` is critical. `foreach_descriptor` treats unexpected headers or metatype failures as consistency errors. Concurrent log flushes and recovery share `jd_log_bio`, so `sd_log_flush_lock` protects them. Error paths must unlock freeze mutex and glocks exactly once and must report `LM_RD_GAVEUP` so another node can retry.

## Test Signals
Signals include clean journal detection, dirty journal replay, revoke skip behavior across wraparound, metadata and journaled-data replay, statfs delta recovery and zeroing, recovery on read-only mount with writable device, rejection on read-only block device, frozen filesystem rejection, busy foreign journal glock, malformed log header/hash/CRC, descriptor metatype errors, local journal pointer initialization, uevent status, and DLM recovery result propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/recovery.c -->
