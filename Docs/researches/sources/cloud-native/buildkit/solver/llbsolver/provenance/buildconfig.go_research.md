# sources/cloud-native/buildkit/solver/llbsolver/provenance/buildconfig.go

Purpose: converts LLB definitions into SLSA BuildKit build configuration metadata and source location maps.

Important APIs/types/functions: `AddBuildConfig`, `digestMap`, `toBuildSteps`, and `walkDigests`.

Control flow: `AddBuildConfig` gets the result definition, converts it to ordered build steps, attaches `BuildConfig` to SLSA v1 internal parameters, and, if source metadata exists, converts source-info definitions and remaps locations from op digests to `stepN` keys. `toBuildSteps` unmarshals each LLB op, strips non-reproducible local source attrs (`local.session`, `local.unique`), identifies the synthetic last vertex, walks dependencies depth-first, maps digests to step indexes, clones ops with inputs removed, and writes input references as `stepN:index`. Optional resource usage is attached from capture samples.

State/persistence: mutates the predicate passed in; no external persistence. It reads immutable result definitions and capture samples.

Dependencies/integration: protobuf LLB definitions, provenance capture samples, SLSA typed build config, solver result proxy definitions, and digest mapping used later for layer metadata.

Risks: assumes last definition vertex is synthetic with exactly one input. Bad or missing input digests fail conversion. Stripping local attrs is important for stable/reproducible provenance.

Test signals: no direct tests in this subset; exercised indirectly through provenance creator max-mode paths.
