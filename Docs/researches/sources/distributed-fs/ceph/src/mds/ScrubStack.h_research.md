# sources/distributed-fs/ceph/src/mds/ScrubStack.h

Purpose: declares `ScrubStack`, the MDCache-owned scrub work stack and distributed scrub coordination object.

Important APIs and types: public APIs include `enqueue()`, `scrub_abort()`, `scrub_pause()`, `scrub_resume()`, `scrub_status()`, `scrub_summary()`, `advance_scrub_status()`, `handle_mds_failure()`, `dispatch()`, `remove_inode_if_stacked()`, uninline failure/counter helpers, and config-change handling. Protected/private helpers manage queueing, waiting, auth validation, inode/dirfrag scrub, final validation callbacks, state messages, pending aborts, path summaries, message handlers, and uninline.

State and persistence: the header declares intrusive stack/waiting lists, in-progress counts, remote scrub gather sets, scrub epochs, abort flags, per-rank stats and counters, active tag map, state enum, clear-stack flag, and control contexts. The object is expected to be empty and idle at destruction.

Dependencies and integration: depends on `CInode`, `ScrubHeader`, cluster log, `Cond`, `elist`, `Finisher`, `CDir`, and MDS message types. It is tightly coupled to `MDCache` and MDS locking.

Risks and test signals: state transitions are asynchronous: abort and pause can be delayed until in-progress work completes, while resume cancels pending pause contexts. Tests should validate stack/waiting list accounting, summary/status output, rank 0 peer coordination, config refresh of `mds_scrub_stats_review_period`, and destructor invariants after completion.
