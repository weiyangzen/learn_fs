# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-helpers.h

## Purpose
Defines the changelog xlator’s private state, per-FOP local state, record structures, dispatcher contracts, barrier/drain state, and macros used by FOP implementations.

## APIs, Types, and Functions
Important types are `changelog_log_data_t`, `changelog_dispatcher_t`, `changelog_time_slice_t`, `changelog_rollover_t`, `changelog_fsync_t`, `drain_mgmt_t`, `barrier_notify_t`, `barrier_flags_t`, `changelog_ev_selector_t`, `changelog_priv_t`, `changelog_local_t`, `changelog_inode_ctx_t`, `changelog_entry_fields`, and `changelog_opt_t`. The header declares persistence, update, dispatch, barrier, snapshot, and path-resolution helpers. Macros initialize locals, fill optional records, manage iobuf refs, unwind FOPs with cleanup, skip inactive/internal operations, enforce FOP boundaries, update slice versions, and handle pthread errors.

## Control Flow, State, and Persistence
`changelog_priv_t` is the xlator’s state container: active/rpc flags, brick and changelog directories, file descriptors for changelog/HTIME/CSNAP, rollover counters, locks, type maps, dispatcher and encoder selections, drain colors/counters, barrier queue/timer, RPC server, rotating buffer, reverse clients, and cleanup counters. `changelog_local_t` carries one FOP’s pending record and optional previous entry for multi-record operations such as rename. Optional records are stored in an iobuf as `changelog_opt_t` arrays and later serialized by encoders.

## Dependencies and Integration
Includes Gluster locking, timers, iobufs, rot-buffs, call stubs, rpcsvc, changelog xlator declarations, event-handle types, misc constants, and message IDs. It is included by most changelog source files and by FOP code in `changelog.c`.

## Risks and Test Signals
Risks include macro-heavy control flow, lock-order coupling, manual optional-record memory ownership, fd lifetime complexity, and many state fields that must be initialized consistently in the main xlator. Test signals include compile coverage of all FOP macros, memory leak checks for optional records, lock-order stress around rollover, and state initialization/reconfigure tests.
