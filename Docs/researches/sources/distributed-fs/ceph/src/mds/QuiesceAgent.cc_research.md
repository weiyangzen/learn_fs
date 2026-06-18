# sources/distributed-fs/ceph/src/mds/QuiesceAgent.cc

Purpose: implements the worker-side quiesce agent that receives root state maps from the quiesce DB manager, starts or cancels local quiesce requests, and asynchronously acknowledges observed state back to the manager.

Important APIs and control flow: `db_update()` reconciles an incoming `QuiesceMap` with current tracked roots, removes failed roots from the response, reuses existing `TrackedRoot`s where possible, computes actual state, and arms pending roots for the agent thread. `agent_thread_main()` swaps pending roots into current, performs upkeep outside the mutex, issues `submit_request()` for roots that should quiesce, calls `cancel_request()` for roots that should release, builds an ack for state changes, sends `agent_ack()`, then waits for pending work or callback-triggered upkeep. `set_pending_roots()` arms a new version; `set_upkeep_needed()` wakes the thread when request completion changes state. `TrackedRoot::~TrackedRoot()` cancels an abandoned active quiesce request.

State and persistence: all state is in-memory. `current` and `pending` hold versioned root maps; each `TrackedRoot` stores request handle, cancel function, quiesce/cancel results, committed DB state, and expiry. No disk persistence is done here; durable/replicated state lives in the quiesce DB manager/listings.

Dependencies and integration: depends on `QuiesceDb.h`, Ceph `Thread`, `Context`, and callbacks supplied by MDS quiesce integration (`submit_request`, `cancel_request`, `agent_ack`). It avoids synchronous ack races by always returning false from `db_update()`.

Risks and test signals: risks center on threading and lifetimes: callback captures `this`, tracked roots use a spin lock, destructors can synchronously cancel, and reset warns about deadlock if called while holding the MDS lock. Tests should cover repeated DB versions, rollback logging, quiesce completion followed by release, cancellation failures, shutdown while callbacks are pending, and asynchronous ack ordering.
