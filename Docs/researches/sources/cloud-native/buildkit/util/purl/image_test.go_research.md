<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/purl/image_test.go -->
# sources/cloud-native/buildkit/util/purl/image_test.go

Purpose: validates image reference to package-url conversion and package-url back to normalized image reference conversion.

Important APIs and types: `TestRefToPURL` and `TestPURLToRef` exercise `RefToPURL` and `PURLToRef` with `packageurl.TypeDocker`, OCI platform specs, and generated digests.

Control flow: tests run table cases for plain names, tags, Docker Hub familiar forms, canonical refs, registry names, platform qualifiers, invalid refs, invalid purl types, and digest-bearing purls.

State and persistence: pure table tests with no external state.

Dependencies and integration: uses `net/url` for expected escaped platform strings, containerd platform normalization, OCI specs, packageurl-go, and `testify/require`.

Risks: tests intentionally normalize platform OSVersion to empty before comparison because purl platform strings cannot carry all platform fields. No fuzzing of arbitrary purl qualifier ordering or malformed digest/version combinations beyond listed cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/purl/image_test.go -->
