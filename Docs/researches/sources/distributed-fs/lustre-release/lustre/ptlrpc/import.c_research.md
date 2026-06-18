# sources/distributed-fs/lustre-release/lustre/ptlrpc/import.c

## Purpose
`import.c` manages Lustre client-side PTLRPC imports: connection state, reconnect and failover, invalidation, replay recovery, disconnect, idle disconnect, cleanup, and adaptive timeout measurement. An import is the client's connection/session state toward a target; this file is the state-machine core that moves it between NEW, CONNECTING, FULL, DISCON, REPLAY, RECOVER, EVICTED, IDLE, and CLOSED.

## Important APIs, types, and functions
- State helpers: `import_set_state_nolock()`, `import_set_state()`, `ptlrpc_init_import()`, `ptlrpc_import_enter_resend()`, and `deuuidify()`.
- Disconnect/invalidate: `ptlrpc_set_import_discon()`, `ptlrpc_deactivate_import()`, `ptlrpc_invalidate_import()`, `ptlrpc_cleanup_imp()`, `ptlrpc_fail_import()`, and `ptlrpc_reconnect_import()`.
- Connect path: `import_select_connection()`, `ptlrpc_connect_import()`, `ptlrpc_connect_import_locked()`, `ptlrpc_connect_interpret()`, `ptlrpc_connect_set_flags()`, and `ptlrpc_prepare_replay()`.
- Recovery: `ptlrpc_import_recovery_state_machine()`, `signal_completed_replay()`, `completed_replay_interpret()`, and `ptlrpc_invalidate_import_thread()`.
- Disconnect path: `ptlrpc_disconnect_prep_req()`, `ptlrpc_disconnect_import_async()`, `ptlrpc_disconnect_import()`, `ptlrpc_disconnect_and_idle_import()`, and their interpret/end helpers.
- Adaptive timeout utilities: `obd_at_measure()` and `import_at_get_index()`.
- Local structs: `ptlrpc_connect_async_args` carries committed transno and initial-connect status; `disconnect_async_arg` carries completion/result/noclose for async disconnect.

## Control flow
Failure begins with `ptlrpc_set_import_discon()` or `ptlrpc_fail_import()`, which transition a FULL import to DISCON, optionally mark it invalid, emit OBD events, and wake the pinger. `ptlrpc_invalidate_import()` deactivates the import if needed, aborts inflight RPCs, waits until `imp_inflight` reaches zero, emits invalidate events, flushes security contexts, and wakes waiters.

Connect starts in `ptlrpc_connect_import_locked()` under `imp_lock`. It rejects CLOSED/FULL/already-connecting imports, increments connection count, records initial versus reconnect state, selects a connection, adapts security, rebuilds connect data from original requested flags, lets the OBD layer prepare reconnect data, packs a CONNECT RPC with DLM handle, connect data, optional SELinux policy, timeout data, async args, and replay/transno flags, then queues it to `ptlrpcd`.

`ptlrpc_connect_interpret()` is the central decision point. On errors it wakes no-resend delayed requests, updates force-reconnect flags, deactivates on permanent access/version failures, schedules pinger retries, and leaves the import DISCON. On success it validates server connect data, negotiated flags, checksums, BRW sizes, mod-RPC limits, namespace flags, adaptive-timeout support, and version compatibility. It then chooses a recovery path based on connect reply flags: initial connect may go FULL or wait for server recovery; reconnect may enter REPLAY, REPLAY_LOCKS, RECOVER, EVICTED, or FULL depending on handles, recovery flags, invalid state, lightweight flags, and cached-data availability.

The recovery state machine replays committed and replay lists, replays LDLM locks, sends a replay-complete PING, waits for replay completion, resends pending requests, activates the import, and wakes delayed requests. Eviction launches a separate invalidation thread to avoid blocking the triggering task.

Disconnect uses a target-specific DISCONNECT opcode, sets no-resend and short timeout, then either sends async and completes on interpretation or directly closes/disconnects when already not FULL or forced. Idle disconnect sends a DISCONNECT only when the import has no resource holders beyond the disconnect request and no namespace lock references; a late reply can either move to IDLE or immediately reconnect if new requests appeared.

## State and persistence behavior
The import state is in-memory and guarded mostly by `imp_lock`. `import_set_state_nolock()` also maintains a ring history of states and timestamps and initializes replay substate on replay transitions. `imp_generation` invalidates old requests across disconnect/reconnect boundaries. Flags such as `IMPF_INVALID`, `IMPF_REPLAYABLE`, `IMPF_RESEND_REPLAY`, `IMPF_PINGABLE`, `IMPF_DEACTIVE`, `IMPF_CONNECT_TRIED`, and `IMPF_VBR_FAILED` coordinate recovery and retry behavior. Lists such as sending, delayed, committed, replay, unreplied, and connection lists are manipulated under lock. Adaptive timeout state keeps rolling bins, current timeout, and worst-ever timestamp in memory. No state survives module unload or client restart except through server recovery protocols and replayed transactions.

## Dependencies and integration points
This file integrates with PTLRPC request allocation/packing/queuing, ptlrpcd, the pinger, OBD reconnect/import events, LNet peer discovery, class import/export/connection references, LDLM namespace and lock replay, sptlrpc security adaptation and context flushing, SELinux policy packing, checksum negotiation, adaptive timeout code, failure-injection hooks, and Lustre console/debug logging. It exports key entry points for other client subsystems to initialize, deactivate, reconnect, disconnect, idle, and clean imports.

## Risks
- State transitions are highly concurrent: pinger, request callbacks, invalidation thread, disconnect, idle disconnect, and user-triggered reconnect can race.
- `ptlrpc_invalidate_import()` waits indefinitely in principle for inflight RPC completion; sluggish networks and long reply unlink paths are explicitly handled but operationally risky.
- Connect flag negotiation must reject unsupported server-granted features without breaking rolling upgrades.
- Replay ordering depends on committed/replay lists and known replied XID preparation; incorrect ordering risks transaction loss or duplicate replay.
- Server-handle changes distinguish recoverable failover from eviction; mistakes can either evict unnecessarily or retain invalid server state.
- Idle disconnect uses generation checks to handle late replies; incorrect generation updates can strand requests or reconnect unexpectedly.

## Test signals
Important coverage includes initial connect, reconnect after timeout, multi-NID failover selection, unreachable peers, access denied and protocol mismatch paths, checksum and BRW negotiation, server handle change with and without recovery flags, replay of committed/replay lists, LDLM lock replay, replay-complete failure, eviction invalidation thread, delayed/no-resend request wakeup, disconnect while recovering, async disconnect completion, idle disconnect races with new requests, adaptive-timeout bin rollover and bounds, and failure-injection points named in the code.
