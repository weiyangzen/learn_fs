<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_stack.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_stack.c

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_stack.c_research.md`.

Purpose: handles GNI LND hardware quiesce, timeout bumping, critical-error reset, and optional RCA node-state monitoring. It is the recovery path used when Gemini/GNI hardware pauses or reports unrecoverable errors.

Important APIs/types/functions: `kgnilnd_bump_timeouts()` refreshes peer, connection, TX, and datagram timers after a pause. `kgnilnd_quiesce_wait()` transitions all worker threads into or out of quiescence. `kgnilnd_reset_stack()` tears down and recreates device resources. `kgnilnd_ruhroh_thread()` serializes quiesce and reset work. `kgnilnd_pause_threads()`, `kgnilnd_hw_in_quiesce()`, `kgnilnd_check_hw_quiesce()`, `kgnilnd_quiesce_end_callback()`, and `kgnilnd_critical_error()` are the hardware event entry points. Under `GNILND_USE_RCA`, `kgnilnd_rca()` subscribes to RCA events and reports peer up/down state.

Control flow: a quiesce or callback sets global flags and wakes the ruhroh waitqueue. The ruhroh thread locks `kgn_quiesce_mutex`, sets `kgn_quiesce_trigger`, wakes LND worker queues, waits until `GNILND_IS_QUIESCED`, handles timeout-bump callbacks, then clears the trigger and waits for workers to resume. Reset flow first quiesces, cancels network datagrams and connections, drains ready/purgatory lists, asserts all hardware resources are gone, finalizes devices, reinitializes devices/datagrams/FMA blocks, bumps timers by reset duration, and resumes traffic.

State and persistence behavior: all state is in live globals: quiesce trigger, reset/pause flags, bump duration, reset count, connection lists, peer queues, device counters, datagrams, and optional RCA subscription tickets. Barriers (`set_mb`, `smp_rmb`) enforce visibility between interrupt callbacks and the ruhroh thread. No state persists across module unload.

Dependencies and integration: tightly coupled to GNI device lifecycle (`kgnilnd_dev_init/fini`, datagram cancellation, FMA mapping), peer/connection locks, LNet peer notification, wait queues, timers, and optional Cray RCA APIs (`krca_register`, `krca_subscribe`, `krca_wait_event`, `krca_get_sysnodes`).

Risks: reset is assert-heavy and can panic if resources remain. Quiesce waits scale with timeout tunables and can stall if a worker fails to check in. Nested loops reuse `i` in `kgnilnd_bump_timeouts()` while walking devices/datagram buckets, which is easy to break during edits. Callback overwrites of bump information are acknowledged as possible but assumed rare. RCA filtering must not report irrelevant service/GPU events as LNet peer changes.

Test signals: inject hardware quiesce callbacks and critical errors, verify all worker threads pause/resume, run traffic through reset and confirm peer notifications and reconnects, validate no live FMA blocks/EPs/connections remain before reinit, test shutdown races, and exercise RCA up/down/unavailable events when built with RCA support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_stack.c -->
