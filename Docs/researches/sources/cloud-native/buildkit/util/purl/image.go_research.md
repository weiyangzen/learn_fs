<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/purl/image.go -->
# sources/cloud-native/buildkit/util/purl/image.go

Purpose: converts Docker/OCI image references with optional platform information to and from package-url (`purl`) strings.

Important APIs and types: `RefToPURL` and `PURLToRef`.

Control flow: `RefToPURL` parses and normalizes an image reference, records digest as a `digest` qualifier for canonical refs, extracts tag as package version when present, collapses familiar Docker names into namespace/name fields, and appends normalized platform as a qualifier. `PURLToRef` parses purl strings, requires type `docker`, rebuilds a reference from namespace/name/version/digest qualifiers, parses a platform qualifier while clearing OSVersion/OSFeatures that containerd may infer, defaults tag to `latest` when neither version nor digest exists, then validates through distribution reference parsing.

State and persistence: pure conversion; no process or filesystem state.

Dependencies and integration: uses distribution/reference, containerd/platforms, OCI digest and platform specs, and packageurl-go. Intended for SBOM/package identity and image reference interchange.

Risks: digest can be represented either as a version that parses as a digest or as a qualifier; mismatches are rejected. Only Docker purl type is accepted in reverse conversion. Platform string parsing may still normalize OS/architecture according to containerd behavior.

Test signals: `image_test.go` covers default tags, Docker Hub familiar names, registry namespaces, canonical digests, digest qualifier/version interactions, platforms, and invalid types/refs.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/purl/image.go -->
