# sources/cloud-native/buildkit/solver/llbsolver/proc/provenance.go

Purpose: defines the post-solve processor that creates in-toto provenance attestations for each exported platform.

Important APIs/types/functions: `ProvenanceProcessor`. It returns an `llbsolver.Processor` closure parameterized by SLSA version, attestation attrs, and custom provenance environment.

Control flow: the processor parses platform metadata, reads `inline-only`, finds provenance capture and result refs for each platform ID, constructs a `ProvenanceCreator`, and adds an attestation with predicate type and lazy `ContentFunc`. The content function builds the predicate and marshals it as indented JSON when exporter code requests it.

State/persistence: mutates `llbsolver.Result` by adding attestations. Provenance JSON is generated lazily, so job completion time, layer metadata, and resource samples can be finalized at content generation.

Dependencies/integration: exporter platform metadata, gateway attestation kind, result attestation metadata keys, resources sampler, solver job, and `NewProvenanceCreator`.

Risks: missing capture or output ref for a platform is fatal. Lazy content generation means errors can surface during export/finalization rather than initial processor registration. Attribute parsing is permissive for `inline-only`: invalid bool leaves false.

Test signals: no direct tests in this subset; `provenance.go`, predicate, and store tests cover lower-level behavior.
