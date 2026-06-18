# sources/cloud-native/moby/integration/internal/container/states.go

Purpose: polling predicates for common container states in integration tests.

Important APIs and helpers: `RunningStateFlagIs`, `IsStopped`, `IsInState`, `IsSuccessful`, and `IsRemoved`.

Control flow: predicates call `ContainerInspect` and return `poll.Success`, `poll.Continue`, or `poll.Error` based on running flag, status membership, exit code, or not-found classification. `IsStopped` is a specialization for `StateExited`; `IsSuccessful` requires exit code 0; `IsRemoved` succeeds on not found.

State and persistence: reads daemon container inspect state and interprets status/exit code. It does not mutate state.

Dependencies and integration: depends on Moby client, container state types, containerd error definitions, and gotest `poll`.

Risks: polling predicates surface non-not-found inspect errors as hard errors. `IsInState` treats any listed state as success but does not check health or restart count.

Test signals: helper-only; provides consistent wait behavior across container lifecycle tests.
