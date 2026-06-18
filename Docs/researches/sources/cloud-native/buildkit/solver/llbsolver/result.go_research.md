# sources/cloud-native/buildkit/solver/llbsolver/result.go

Purpose: defines llbsolver result wrappers and lazy result proxy evaluation, including provenance capture and source-location error enrichment.

Important APIs/types/functions: `Result`, `Attestation`, `workerRefResolver`, `resultProxy`, `newResultProxy`, `ID`, `Definition`, `Provenance`, `Release`, `wrapError`, `loadResult`, and `Result`.

Control flow: `resultProxy.Result` uses a flightcontrol group to run evaluation once, refuses access after release, calls bridge `loadResult`, borrows refs embedded in `ExecError`, captures provenance on success, stores result/error, and releases loaded results if a concurrent release wins. `wrapError` enriches vertex errors with source ranges from definition source metadata. `Release` releases borrowed error refs and cached result refs, warning on double release.

State/persistence: proxy caches one `solver.CachedResult`, error, borrowed error results, and captured provenance in memory. It owns release of those refs.

Dependencies/integration: frontend result proxies, solver cached results/provenance providers, BuildKit worker refs/remotes, cache ref config, session groups, errdefs, flightcontrol, and logging.

Risks: ownership around `ExecError` is delicate; `OwnerBorrowed` prevents double-finalizer release. Race between evaluation and release is guarded by mutex but must be preserved. Source-location enrichment depends on matching vertex digest keys.

Test signals: no direct tests in this subset; ownership invariants are referenced by comments and likely covered in worker/result tests outside this scope.
