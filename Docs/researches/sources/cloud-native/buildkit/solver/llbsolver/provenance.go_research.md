# sources/cloud-native/buildkit/solver/llbsolver/provenance.go

Purpose: connects solve requests, result proxies, source metadata, provider walking, and SLSA predicate creation into BuildKit's provenance attestation pipeline.

Important APIs/types/functions: `provenanceBridge`, `ResolveSourceMetadata`, `Solve`, `requests`, `findByResult`, `captureProvenance`, `ProvenanceCreator`, `NewProvenanceCreator`, `scrubMinRequest`, `incompleteMaterialsError`, `Predicate`, `addProvenanceToResult`, `getRefProvenance`, and `getProvenance`.

Control flow: `provenanceBridge.Solve` wraps definition solves with result proxies or delegates frontend solves through nested provenance bridges. It records build results and registers provenance refs. `captureProvenance` walks solver provenance providers: `SourceOp` captures source identifiers, `ExecOp` records secret/SSH use, network access, proxy material/incomplete requests, and resource samples; `BuildOp` marks materials incomplete. `addProvenanceToResult` computes captures for result refs and attestations, merges hidden refs, filters images by platform, optimizes and sorts sources. `NewProvenanceCreator` builds a SLSA v1 predicate, applies mode/min/max/reproducible/usage/complete-materials attrs, adds build config and layers in max mode, and can convert to SLSA v0.2 in `Predicate`.

State/persistence: bridge stores request context, nested builds, source images, subbridges, and provenance-store record IDs for the solve lifetime. `ResultProxy` stores captured provenance after result evaluation. Attestation content is generated later but mutates predicate finish time and optional sys usage.

Dependencies/integration: solver jobs/results, frontends, source metadata resolution, ops provenance providers, cache export, image layer descriptors, BuildKit result attestations, SLSA types, Dockerfile version, resources sampler, and errdefs.

Risks: provenance depends on correct result ownership and bridge lookup by result ID. Min mode intentionally scrubs secrets/SSH/build-args/labels and marks request incomplete. Complete-materials mode fails on local sources or proxy-incomplete requests. Layer capture depends on cache exporter metadata and must strip internal annotations.

Test signals: `provenance_test.go` covers local-source incomplete-material errors; predicate/store/type tests cover major helpers. Full bridge behavior is integration-heavy.
