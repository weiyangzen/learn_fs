# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/management/ManagementTaskCoordinator.java

Purpose: Background coordinator that repeatedly chooses and runs block management tasks such as tier alignment, swap restoration, and promotion.

Important APIs: Constructor wires block store, metadata manager, load tracker, and eviction-view supplier; `start`; `close`; private `initializeTaskProviders`, `getNextTask`, and `runManagement`.

Control flow: A daemon runner loop optionally backs off when worker load is detected, asks providers in priority order for a task, runs the selected task on the coordinator thread, logs results, and sleeps after no-progress runs. `close` shuts down the task executor and interrupts the runner.

State and persistence: Holds a runner thread, fixed task executor, provider list, and service references. No persistent state.

Dependencies and integration: Reads management backoff and thread-count config. Currently initializes `TierManagementTaskProvider`; tasks use the same executor for transfer partitions.

Risks and test signals: Provider order creates implicit priority. Exceptions are logged and loop continues. Tests should cover start/close lifecycle, load backoff, no-task sleep, no-progress sleep, provider priority, and interrupt behavior.
