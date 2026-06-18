# sources/cloud-native/buildkit/solver/llbsolver/provenance/predicate.go

Purpose: converts captured BuildKit sources/request data into SLSA v1 provenance predicate fields and material descriptors.

Important APIs/types/functions: `slsaMaterials`, `parseBundleLocatorURL`, `digestSetForCommit`, `setPURLQualifier`, `findMaterial`, `NewPredicate`, `RequestProvenance`, and `FilterArgs`.

Control flow: `slsaMaterials` emits purl-backed materials for image refs and image blobs, raw URL materials for git sources, additional purl bundle materials for bundle-backed git, and URL/digest materials for HTTP sources. `NewPredicate` builds resolved dependencies, external request/config source, internal builder platform, local source request entries, VCS metadata, completeness/hermetic flags, and proxy-network metadata. `RequestProvenance` derives config source from the context arg and captured materials, removes consumed context/filename args, and redacts credentials. `FilterArgs` drops host-specific and attestation args while redacting context URLs.

State/persistence: returns new typed predicate/request structures. It clones maps where needed and mutates request arg copies.

Dependencies/integration: in-toto SLSA common/v1 structs, BuildKit provenance types, Dockerfile git URL fragment utility, purl utilities, package-url parser, source type schemes, and URL redaction.

Risks: bundle locator parsing is intentionally permissive because validation happens upstream; malformed locators are skipped. Commit digest algorithm is inferred by length only. Filtering decisions define what user inputs appear in attestations and are security/privacy sensitive.

Test signals: `predicate_test.go` covers image blob purls, OCI blob purls, git bundle materials, argument filtering/redaction, commit digest choice, material lookup with subdir fragments, request preservation, config source derivation, contextsubdir retention, and proxy-network metadata.
