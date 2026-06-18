# sources/distributed-fs/ceph-client/include/linux/sched/rseq_api.h

Purpose: compatibility include that exposes restartable-sequences APIs through the scheduler include namespace.

Important APIs and types: no new symbols are defined; it includes `linux/rseq.h`.

Control flow: scheduler code that needs rseq hooks can include this wrapper; runtime behavior belongs to rseq implementation and task `rseq` state.

State and persistence: no state is owned here.

Dependencies and integration points: connects scheduler headers with restartable sequence declarations.

Risks and test signals: risk is include layering drift or missing rseq declarations after refactors. Compile-test rseq/scheduler integration and run rseq selftests.
