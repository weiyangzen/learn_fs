# sources/cloud-native/buildkit/solver/llbsolver/provenance_store_test.go

Purpose: validates provenance store lookup semantics and related min-mode request scrubbing.

Important APIs/types/functions: tests include `TestProvenanceStoreLooksUpByDefinitionDigest`, `TestProvenanceStoreOmitsInputRoot`, `TestProvenanceStoreLookupAfterDefinitionOpRoundTrip`, `TestProvenanceStoreUnregister`, `TestProvenanceStoreAmbiguousDigest`, and `TestScrubMinRequestScrubsNestedRequests`.

Control flow: tests generate simple LLB definitions with `llb.Scratch().File(...)`, register request provenance, and assert lookup behavior for same, different, round-tripped, unregistered, and ambiguous definitions. The scrub test builds nested `Parameters` with build args, labels, secrets, SSH, inputs, and root request, then asserts min-mode removal and retained structural args.

State/persistence: in-memory store only. Tests assert registration does not mutate the original protobuf definition.

Dependencies/integration: BuildKit LLB client, provenance types, and testify.

Risks: tests use simple file definitions, so complex multi-output definitions are not covered. They pin ambiguity behavior that can hide input provenance when multiple conflicting requests share a digest.

Test signals: strong for lifecycle and equality semantics of request provenance records, plus recursive min-mode scrubbing.
