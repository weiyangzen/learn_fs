# sources/cloud-native/buildkit/solver/llbsolver/provenance/predicate_test.go

Purpose: unit-tests SLSA material emission, request filtering, config-source mapping, and proxy metadata generation.

Important APIs/types/functions: tests exercise `slsaMaterials`, `FilterArgs`, `digestSetForCommit`, `findMaterial`, and `NewPredicate`.

Control flow: material tests parse emitted package URLs and inspect qualifiers for image blobs and git bundles. Filtering tests verify host-specific/attestation args are removed while ordinary Dockerfile args remain and context credentials are redacted. Predicate tests build captures with requests, secrets, SSH, inputs, git sources, context subdirs, and proxy incomplete entries, then assert SLSA external parameters and metadata.

State/persistence: no external state; constructs in-memory captures and material lists.

Dependencies/integration: package-url parser, provenance types, digest helper, and testify.

Risks: tests do not cover every source type combination or invalid purl errors. They pin privacy-sensitive filtering and bundle purl behavior, which are high-value regression areas.

Test signals: strong for SLSA predicate shape, git bundle material preservation, config source derivation, completeness/hermetic flags under proxy incomplete materials, and request preservation for min/max provenance paths.
