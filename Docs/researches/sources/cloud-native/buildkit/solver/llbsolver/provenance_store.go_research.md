# sources/cloud-native/buildkit/solver/llbsolver/provenance_store.go

Purpose: tracks request provenance for frontend input definitions so nested/input provenance can be associated with later result definitions.

Important APIs/types/functions: `provenanceStore`, `provenanceRecord`, `newProvenanceStore`, `register`, `unregister`, `lookup`, `provenanceBridge.registerProvenanceRefs`, `registerProvenanceRef`, `requestProvenance`, `inputProvenance`, `rootRequestProvenance`, `hasRequestProvenance`, and `definitionHeadDigest`.

Control flow: `register` computes a definition head digest from the synthetic last vertex input, stores a cloned request under a random record ID, and indexes it by digest. `lookup` gathers records for the same digest, strips nested root request from each clone, and returns a request only if all records are equal; ambiguity returns false. Bridges register refs after solve and unregister record IDs when released. Request provenance is derived from bridge frontend request args plus looked-up frontend inputs and optional root request.

State/persistence: in-memory store protected by mutex. Records live for solve/bridge lifetime and are explicitly unregistered by `releaseProvenanceRefs`.

Dependencies/integration: frontend results, solver result proxies, provenance capture/types, LLB definitions, identity IDs, and request filtering helpers.

Risks: head digest extraction depends on the definition shape used by `llb.NewDefinitionOp` round trips. Ambiguous records intentionally suppress input provenance. Failure to unregister can leak request records across solves.

Test signals: `provenance_store_test.go` covers digest lookup, input root omission, definition round-trip lookup, unregister, ambiguity, and min-request scrubbing in related code.
