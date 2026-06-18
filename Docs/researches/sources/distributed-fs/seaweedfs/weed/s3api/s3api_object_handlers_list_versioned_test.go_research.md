# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_list_versioned_test.go

Purpose: this file validates listing behavior when objects are represented by SeaweedFS `.versions` directories. It checks that versioned objects project as normal current objects in ordinary listings, delete-marker latest versions are hidden, `.versions` directories are not recursively traversed, XML for `ListObjectVersions` preserves interleaved ordering, and key-marker traversal starts from the correct directory component.

Important APIs/types/functions: tests reuse `testFilerClient` and introduce `customTestFilerClient` to track traversed directories. They exercise `doListFilerEntries`, `S3ListObjectVersionsResult` XML marshaling, `VersionListEntry`, `VersionEntry`, `DeleteMarkerEntry`, `PrefixEntry`, `versionCollector.computeStartFrom`, and logic equivalent to version-directory prefix filtering.

Control flow: synthetic filer entries include directory names ending in `s3_constants.VersionsFolder` plus `Extended` fields such as `ExtLatestVersionIdKey`, latest size, latest mtime, latest ETag, and latest delete-marker flag. Ordinary listing tests call `doListFilerEntries` with callbacks that collect projected keys. XML tests build `S3ListObjectVersionsResult.Entries` in expected order and assert that marshaling emits `DeleteMarker`, `Version`, and `CommonPrefixes` in the same interleaved stream. Marker tests verify `computeStartFrom` chooses the local component to pass to filer listing and that directories before a marker are skipped unless the marker descends into them.

State and persistence behavior: version state is modeled as `filer_pb.Entry.Extended` metadata on `.versions` directory entries rather than live version files. The tests assert the production contract that latest-version cached metadata on the directory is enough for normal ListObjects projection without reading the version directory contents.

Dependencies and integration points: relies on `s3_constants` version metadata keys, `encoding/xml`, `filer_pb`, gRPC stream interfaces, and listing helpers in the S3 API package. It integrates with the versioned write path indirectly: `putVersionedObject` and `versionedFinalize` are expected to maintain the cached latest metadata this test consumes.

Risks: callback logic in some tests mirrors production behavior rather than invoking the HTTP response path, so XML/list accumulator regressions outside `doListFilerEntries` may need separate tests. The file is strong on directory traversal safety but less strong on real filer pagination because the mock is in-memory and simplified.

Test signals: clear regression signals cover no duplicate projection of `.versions` objects, delete-marker suppression, `maxKeys` truncation state, `.versions` traversal avoidance, leading-slash prefix normalization for version listings, XML interleaving, and key-marker start computation.
