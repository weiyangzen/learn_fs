## sources/cloud-native/moby/daemon/builder/dockerfile/containerbackend.go

**Purpose:** Manages temporary build containers for classic Dockerfile `RUN`, `WORKDIR` creation, and Windows helper execution.

**Important APIs/types:** `containerManager` tracks `tmpContainers` and an execution backend. `Create`, `Run`, `RemoveAll`, `statusCodeError`, `errCancelled`, and `logCancellationError` implement lifecycle and error adaptation.

**Control flow:** `Run` starts attach in a goroutine, waits for attach readiness, starts a cancellation watcher that force-removes the container if context is canceled, starts the container, waits for attach completion, then waits for non-running status. Nonzero exit codes become `statusCodeError`.

**State and persistence:** Tracks temporary container IDs in memory and removes them with force/remove-volume. Persistent container side effects are committed by callers, not here.

**Dependencies and integration:** Uses builder `ExecBackend` methods, daemon backend container configs, container wait states, and string ID formatting. Called by RUN dispatch and internal Windows account lookup.

**Risks:** Ordering around attach/start/wait is concurrency-sensitive. Cancellation races are handled via `finished` and `cancelErrCh`; mistakes can deadlock. `RemoveAll` must tolerate already-removed containers.

**Test signals:** Mock backend implements required methods, but direct unit tests are not in this subset. Integration should cover cancellation, nonzero exit messages, and cleanup under `--rm`/`--force-rm`.
