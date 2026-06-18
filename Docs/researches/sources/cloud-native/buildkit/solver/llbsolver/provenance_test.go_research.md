# sources/cloud-native/buildkit/solver/llbsolver/provenance_test.go

Purpose: tests user-facing incomplete-materials error construction for provenance complete-materials mode.

Important APIs/types/functions: `TestIncompleteMaterialsErrorIncludesLocalSources` exercises `incompleteMaterialsError`.

Control flow: constructs a capture containing a local source named `context`, calls the error builder, asserts the error unwraps/ascribes to `errdefs.ProvenanceMaterialsIncompleteError`, and checks detail fields and message text.

State/persistence: none.

Dependencies/integration: llbsolver provenance capture, provenance types, solver errdefs, and testify.

Risks: coverage is narrow: only local-source incomplete details are tested, not proxy incomplete requests or empty details.

Test signals: protects complete-materials diagnostics so users see which local source prevented complete provenance and machine-readable incomplete detail includes reason `local_source`.
