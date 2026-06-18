## sources/cloud-native/buildkit/util/flightcontrol/flightcontrol.go

Purpose: implements BuildKit's singleflight-like coordination with cancellation-aware shared contexts and progress replay for callers joining an in-flight operation.

Important APIs/types: `Group[T].Do(ctx, key, fn)` synchronizes by key. Internal `call[T]` owns result/error, ready/cleaned channels, waiter contexts, a shared context, and progress state. `sharedContext` implements context behavior whose done channel closes only when all waiter contexts are done. `progressState` stores latest progress by ID and fans raw progress to attached writers.

Control flow: `Do` loops over `g.do` and retries on internal `errRetry`, with randomized exponential backoff capped at 15 seconds. `g.do` creates a `call` if no key exists or waits on the existing one. `call.wait` attaches the caller's progress writer, appends a cancelable child context, starts `run` once, and returns either the shared result, the caller cancellation cause, or `errRetry` after cleanup when a previous errored call must be removed. `run` executes `fn` with the shared context, stores result/error, closes `ready`, and closes progress writer on exit.

State/persistence: in-memory map of active calls protected by `Group.mu`; entries are deleted only after `ready`. Progress state stores latest item per progress ID and live raw writers. No persistence. Dependencies: BuildKit `util/progress`, `sync`, `slices`, `math/rand`, `pkg/errors`.

Integration points: used for deduplicating expensive BuildKit operations while allowing multiple solve callers to observe progress. The custom context's `Value` bridges both progress context and the first active caller context.

Risks: complex cancellation races; errored calls trigger retry rather than sharing failure; backoff uses `time.Sleep` without observing caller cancellation during sleep; `Deadline` returns the first active deadline rather than the earliest. Progress replay stores latest-by-ID only, so historical intermediate states are not preserved. Test signals: `flightcontrol_test.go` covers sharing, one/both caller cancellation, race retry, contention, and massive parallel failure.
