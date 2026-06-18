## sources/distributed-fs/seaweedfs/weed/s3api/s3tables/utils_namespace_test.go

Purpose: verifies namespace normalization, ARN handling, and namespace metadata property round-tripping.

Important tests: `TestValidateNamespaceSupportsMultiLevel`, `TestValidateNamespaceSupportsDottedInput`, `TestValidateNamespaceRejectsEmptyDottedSegment`, `TestParseNamespace`, `TestParseTableFromARNWithMultiLevelNamespace`, `TestBuildTableARNWithDottedNamespace`, `TestExpandNamespace`, and `TestNamespaceMetadataPropertiesRoundTrip`.

Control flow: the tests compare normalized dot-separated strings, expanded string slices, parsed ARN components, and JSON marshal/unmarshal behavior for nil, empty, and populated `Properties`.

State and dependencies: no persistent state. Uses Go JSON and reflection only.

Signals and risks: these tests protect compatibility between AWS-style dotted namespaces and internal single-directory namespace keys. They also document that empty properties disappear due to `omitempty`. Invalid namespace coverage includes reserved `aws` prefix and empty dotted segments, but not every bucket/table validation branch.
