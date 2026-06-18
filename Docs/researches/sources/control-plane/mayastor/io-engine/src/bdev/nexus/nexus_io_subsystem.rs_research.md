<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_io_subsystem.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_io_subsystem.rs

Purpose: serializes pause and resume operations for the frontend nexus subsystem, mainly NVMe-oF, while supporting nested/concurrent pause requests and a frozen state for faulted nexus behavior.

Important APIs/types/functions: `NexusPauseState`, `NexusIoSubsystem`, `new`, `pause_state`, `suspend`, and `resume`.

Control flow: `suspend` must run on the first core, transitions `Unpaused -> Pausing`, increments the pause counter from zero, pauses the NVMf subsystem if shared, stores `Paused`, and wakes one waiter. If already `Paused` or `Frozen`, it increments the pause counter. If another transition is active, it queues a oneshot waiter and retries. `resume` decrements the pause counter; only the final resume either leaves state `Frozen` when requested/frozen or resumes the NVMf subsystem and stores `Unpaused`.

State and persistence: pause state is an `AtomicCell<NexusPauseState>`, pause count is `AtomicU32`, and waiters are in-memory oneshot senders. There is no persistent state. `Frozen` intentionally keeps the subsystem paused even after the pause count reaches zero.

Dependencies/integration: owns a mutable reference to the nexus `Bdev`, checks share protocol through `Share`, looks up `NvmfSubsystem` by name, uses core identity assertions, and is called by nexus shutdown, snapshot, child retire, remove, and resume flows.

Risks: wrong-core calls panic. Unexpected pause/resume errors can panic except for selected `EPERM`/`ECANCELED` cases. Waiter ordering wakes only one waiter per transition, so correctness relies on each resumed waiter retrying and waking the next. Frozen state blocks later nexus operations through `check_nexus_operation`.

Test signals: nested pause/resume counts, concurrent pause while unpausing, concurrent resume while pausing, freeze-on-fault behavior, NVMf shared vs unshared nexus, tolerated subsystem pause/resume errors, wrong-core assertions, waiter wake chaining, and operation rejection while frozen.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_io_subsystem.rs -->
