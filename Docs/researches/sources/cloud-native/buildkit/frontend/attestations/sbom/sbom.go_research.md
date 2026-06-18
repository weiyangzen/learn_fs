# sources/cloud-native/buildkit/frontend/attestations/sbom/sbom.go

Purpose: builds a reusable SBOM scanner closure that runs a scanner image against an LLB state and returns a BuildKit attestation.

Important APIs: `Scanner` function type; `CreateSBOMScanner` resolves scanner image config and returns a closure; `HasSBOM` checks result attestations for SPDX predicate type. Constants define core and extra mount names plus source/output directories.

Control flow: the scanner image is resolved, entrypoint and cmd are combined, and empty command is rejected. The returned closure builds scanner environment, includes scanner params as `BUILDKIT_SCAN_*`, mounts the core target and optional extra states read-only, runs scanner image with `/tmp` tmpfs, and returns a bundle attestation pointing at `/run/out/`.

State and persistence: scan output exists as an LLB state until solved; attestation metadata identifies SBOM reason and core name. No local persistence.

Dependencies and integration: integrates sourceresolver, LLB image/run/mount primitives, gateway attestation kinds, in-toto SPDX predicate type, and builder SBOM flow.

Risks and test signals: risks include scanner image config lacking command, environment key collisions, missing scanner policy enforcement, and extra mount naming. Coverage is mostly integration through Dockerfile builder SBOM paths.
