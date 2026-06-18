# sources/control-plane/rook/pkg/daemon/multus/statemachine.go

Purpose: provides a generic polling state-machine runner for Multus validation states with per-state timeout handling, suggestion accumulation, and context cancellation behavior.

Important APIs/types/functions: `validationState` interface requires `Run(ctx, vsm)`. `validationStateMachine` stores current state, timer, owner refs, results, last suggestions/error, and done flag. Methods are `SetNextState()`, `Exit()`, `Run()`, `resetTimer()`, and `exitContextCanceled()`.

Control flow: `Run()` creates a timer with `vt.ResourceTimeout`, loops until context cancellation, timeout, or `Exit()`, resets the timer whenever the state changes, runs the current state's `Run()`, records latest suggestions/error, and sleeps two seconds between iterations. A timeout returns the last error wrapped with a validation timeout and adds the last suggestions to results.

State and persistence behavior: no external persistence. It carries in-memory execution state and references to Kubernetes owner refs for downstream states. State transitions are explicit via `SetNextState()`, and completion is explicit via `Exit()`.

Dependencies and integration points: used by `ValidationTest.Run()` in `validation.go`. Depends on `ValidationTestResults` suggestion collection and `meta.OwnerReference` for states that create resources.

Risks: `resetTimer()` drains `timer.C` when `Stop()` returns false; if the timer has fired but the channel was already drained, this pattern can block in some timer misuse scenarios, though here it is used inside one loop. The `default` select branch plus sleep means it polls rather than blocking on state-specific watches. On context cancellation, the last error may be nil, so wrapping `%w` with nil can produce less actionable output.

Test signals: no direct state-machine unit tests. Behavior is indirectly exercised only if validation workflow tests exist elsewhere; this subset does not include them.
