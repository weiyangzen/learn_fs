# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_list_test.go

Purpose: this test file exercises S3 ListObjects/ListObjectsV2 XML rendering, prefix and marker normalization, recursive filer traversal, delimiter/common-prefix behavior, permission matching for list requests, and regressions around marker echo and prefix paths ending in `/`. It is a broad regression harness for listing behavior implemented elsewhere in the `s3api` package.

Important APIs/types/functions: `testListEntriesStream` implements the gRPC streaming client shape expected by `SeaweedFilerClient.ListEntries`; `testFilerClient` supplies directory-scoped synthetic `filer_pb.Entry` slices; `markerEchoFilerClient` simulates a backend that incorrectly echoes `StartFromFileName`; `ensureEntryAttributes` protects tests from nil attributes. Tests directly call `normalizePrefixMarker`, `buildTruncatedNextMarker`, `getListObjectsV1Args`, `getListObjectsV2Args`, `sanitizeV1MarkerEcho`, `Identity.CanDo`, and `S3ApiServer.doListFilerEntries`.

Control flow: the tests bypass HTTP for most cases and drive internal listing helpers with mock filer clients. `TestDoListFilerEntries_BucketRootPrefixSlashDelimiterSlash_ListsDirectories` proves prefix `/` and delimiter `/` at bucket root still lists directories. Marker echo tests set a cursor, pass an exclusive marker, and verify echoed markers are skipped without losing following entries. Prefix-ending-with-slash tests model `prefixEndsOnDelimiter` so traversal descends into only the exact directory and does not match sibling directories like `1000` when the prefix is `1/`.

State and persistence behavior: no persistent state is written; all state is in test-local maps keyed by filer directory. The tests model persisted SeaweedFS metadata through `filer_pb.Entry` fields such as `Name`, `IsDirectory`, `Attributes`, `Extended`, and callback-collected list results.

Dependencies and integration points: the test depends on `filer_pb`, `s3err.EncodeXMLResponse`, `httptest`, gRPC stream interfaces, and `testify/assert`. Its strongest integration points are the filer listing stream contract, S3 XML response structs (`ListBucketResult`, `ListEntry`, `PrefixEntry`), and auth wildcard matching for object-level `List` actions.

Risks: several subtests are documentation-style assertions using `assert.True(t, true)` rather than executable coverage of production delimiter grouping. Mock clients ignore some real filer semantics, especially ordering, limit, and start behavior, so regressions in production pagination may not be fully caught. Still, the marker echo mock intentionally stresses a real no-progress risk.

Test signals: strong signals cover XML namespace output, invalid `max-keys`, allow-unordered parsing, marker echo no-progress protection, root prefix slash listing, exact directory prefix traversal, and object-level list permissions for issue-style scenarios.
