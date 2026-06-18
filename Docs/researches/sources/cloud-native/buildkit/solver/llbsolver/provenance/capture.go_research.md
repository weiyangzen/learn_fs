# sources/cloud-native/buildkit/solver/llbsolver/provenance/capture.go

Purpose: defines the mutable capture object accumulated from solve providers before conversion into provenance predicates.

Important APIs/types/functions: `Capture`, alias `Result`, `Clone`, `Merge`, `Sort`, `OptimizeImageSources`, `AddImage`, `AddImageBlob`, `AddLocal`, `AddGit`, `AddHTTP`, `AddSecret`, `AddSSH`, `AddSamples`, and `parseRefName`.

Control flow: add methods deduplicate by stable identities while preserving meaningful distinctions: images dedupe by ref/local/platform, git sources dedupe by redacted URL plus bundle URL, secrets/SSH merge optional flags with non-optional winning, and empty SSH ID becomes `default`. `Merge` replays add methods and ORs network/incomplete flags. `OptimizeImageSources` drops digest-only image references when a tag ref for the same name:tag exists. `Sort` imposes deterministic ordering across all slices.

State/persistence: in-memory only, later embedded in `provenance.Result` and attestation predicates. `Samples` map tracks per-op resource samples by digest.

Dependencies/integration: provenance type structs, result wrapper, URL credential redaction, OCI/reference parsing, resource sample types, and digests.

Risks: dedupe keys directly affect material completeness; overly broad git/image dedupe can drop required materials. Clone copies sample map but not deep sample values. Sort assumes non-nil secret/SSH entries.

Test signals: `capture_test.go` covers image/platform dedupe, secret optional merge, SSH default ID, git redaction and bundle dedupe, merge flags, sorting, image source optimization, and sample map initialization.
