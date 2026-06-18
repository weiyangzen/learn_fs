# sources/distributed-fs/ceph/src/mds/ScatterLock.h

Purpose: defines `ScatterLock`, a `SimpleLock` specialization for distributed/scattered metadata values that can be dirtied, flushed, and rejoined across MDS ranks.

Important APIs and control flow: state queries include `is_scatterlock()`, `is_sync_and_unlocked()`, `can_scatter_pin()`, dirty/flushing/flushed checks, and scatter/unscatter wanted flags. Mutation APIs include `mark_dirty()`, `start_flush()`, `finish_flush()`, `remove_dirty()`, and update-stamp/list tracking. Rejoin APIs include `infer_state_from_strong_rejoin()`, `encode_state_for_rejoin()`, `decode_state_rejoin()`, and `remove_replica()`.

State and persistence: dirty/flushing/flushed/scatter flags live in `state_flags`. Dirty scatterlocks pin the parent with `PIN_DIRTYSCATTERED`; flush completion drops the pin and clears parent dirty-scattered state. Extra state is lazily allocated in `_more` to hold an updated-list item and timestamp, and is released when dirty is cleared.

Dependencies and integration: depends on `SimpleLock`, `MDSCacheObject`, `xlist`, and MDS context waiters. `Locker` and `CInode` use scatter locks for file and directory metadata scatter/gather behavior.

Risks and test signals: rejoin behavior is delicate: MIX states mark recovery need, flushing is converted back to dirty on decode, and replica removal is blocked during rejoin for several MIX sub-states. Tests should cover dirty pin lifetime, writebehind flush transitions, rejoin encode/decode of gathering states, and delayed rdlock behavior during recovery.
