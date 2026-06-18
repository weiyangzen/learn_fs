# sources/cloud-native/buildkit/solver/llbsolver/provenance/capture_test.go

Purpose: validates capture deduplication, redaction, merge, sorting, optimization, and sample recording behavior.

Important APIs/types/functions: tests cover `AddImage`, `AddSecret`, `AddSSH`, `AddGit`, `Merge`, `Sort`, `OptimizeImageSources`, and `AddSamples`, with a detailed `TestCaptureAddGitBundleDedup`.

Control flow: table-style and subtests construct `Capture` values, invoke add/merge operations, and assert slice lengths and key fields. Bundle tests ensure normal git and bundle-backed git sources with the same URL both survive, identical bundle URLs dedupe, and different bundle URLs are preserved.

State/persistence: no external state; tests inspect in-memory capture state.

Dependencies/integration: provenance types, OCI platform struct, digest helper, and testify.

Risks: tests do not cover nil entries in secret/SSH slices or deep-copy semantics. They intentionally pin dedupe behavior that affects SLSA materials downstream.

Test signals: strong for provenance material identity rules and credential redaction. These tests protect against silent material loss when git bundles are involved.
