# sources/cloud-native/buildkit/client/pinrace_6731_test.go

## Purpose
This integration regression test targets issue 6731, where provenance capture could observe an HTTP source `SourceOp` while its pin was still empty during an ignore-cache shifted-state race. The symptom being guarded is an empty digest reaching provenance capture and failing with an invalid checksum digest format.

## Important APIs, Types, and Functions
- `init` registers `testPinRaceIgnoreCacheShift` in the global integration test list.
- `testPinRaceIgnoreCacheShift` sets up a slow no-cache HTTP server, creates a client, and runs several deterministic race iterations.
- `runPinRaceIteration` constructs the warmup, race-creator, and walker LLB graphs and coordinates two physical `c.Build` calls.
- The test uses `llb.HTTP`, `llb.IgnoreCache`, `llb.Merge`, gateway frontends, `gateway.Client.Solve`, `Ref.Evaluate`, and provenance frontend attrs.

## Control Flow
Each iteration first runs a warmup gateway build in Job 1. That frontend solves and evaluates a non-ignore-cache chain, then blocks on `warmupHold` to keep base, mid, and root states active. A second gateway build in Job 2 then starts a racer chain using ignore-cache and a fresh copy destination, waits a head start, and evaluates a walker chain using ignore-cache and the original mid digest. The delayed HTTP server widens the window where the racer is in source cache-key resolution while the walker provenance traversal can observe the shifted state.

## State and Persistence Behavior
The test deliberately relies on daemon-resident solver state, active refs, resolver caches, and job isolation. It keeps Job 1 alive to hold state in `actives`, while Job 2 uses a separate resolver cache so the HTTP source has to perform a slow fetch. No durable artifacts are asserted; the important state is in-memory BuildKit scheduler/provenance state.

## Dependencies and Integration Points
The file integrates with the client gateway build path, HTTP source resolver, provenance capture, LLB merge/diff scheduler behavior, the integration sandbox, and worker feature compatibility for merge-diff. It skips Windows and needs timing-sensitive behavior from the BuildKit daemon.

## Risks and Edge Cases
The regression is timing-sensitive. The test mitigates flakiness with repeated iterations, a slow HTTP server, no-cache response headers, and a controlled warmup hold. Future solver optimizations may narrow or remove the race window, but the expected signal remains that the build succeeds without empty-pin provenance errors.

## Test Signals
A pass indicates provenance capture can tolerate ignore-cache shifted sources while source resolution is in flight. A failure with checksum/digest parsing or provenance source-pin errors points to a recurrence in `SourceOp` pin publication, resolver cache isolation, or provenance walking.
