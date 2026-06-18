## sources/cloud-native/buildkit/solver/debug.go

Purpose: optional scheduler debugging instrumentation for solver edge state transitions.

Important APIs/types/functions: package globals `debugScheduler` and `debugSchedulerSteps` read `BUILDKIT_SCHEDULER_DEBUG` and `BUILDKIT_SCHEDULER_DEBUG_STEPS`. `debugSchedulerCheckEdge` selects edges to log. The remaining `debugScheduler*` helpers log merge decisions, pre/post unpark state, pipe creation, incoming finish/update, cache upgrades, dependency requests, and inconsistent graph state.

Control flow: most helpers are no-ops unless `e.debug` is true or a serious error occurs. `debugSchedulerPreUnparkSlow` emits detailed fields for edge, deps, incoming requests, update pipes, states, cache keys, and slow/preprocess availability.

State and persistence: debug configuration is process environment state read at init/lazily. Output goes to BuildKit logging, not persistent solver state.

Dependencies and integration points: used throughout `edge.go` and edge merging logic elsewhere. Uses `go-csvvalue` for comma-separated debug step parsing and `bklog`.

Risks and test signals: `debugSchedulerCheckEdge` appears to compute `name` from `steps[0]` inside the loop and then checks `strings.Contains(name, v)`, which may not match the intended current vertex name; debug filtering could be inaccurate. No tests in subset.
