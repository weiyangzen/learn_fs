# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_list_directory_test.go

Purpose: tests directory handling in `doListFilerEntries`, especially the distinction between common prefixes, explicit directory probes, and phantom empty-directory keys.

Important coverage includes `TestDirectoryListedAsCommonPrefix`, `TestEmptyDirectorySurfacedAsMarker`, `TestNonEmptyDirectoryGetsNoPhantomMarker`, and `TestEmptyDirectoryHiddenInFlatListing`. These directly exercise `ListingCursor` and `doListFilerEntries` with a fake filer client.

Control flow builds synthetic directory/file entries under `/buckets/...`, invokes `doListFilerEntries` with different delimiter, prefix, and `prefixEndsOnDelimiter` settings, and records callback entries. It verifies regular directories are passed to delimiter handling as common-prefix candidates, empty real directories are surfaced as folder markers only during explicit `<dir>/` probes, non-empty directories emit their children instead of phantom markers, and plain flat listing hides empty directories while still returning real objects inside non-empty directories.

State and persistence are in-memory fake filer entries keyed by directory path. The tests mutate an empty directory's MIME to `FolderMimeType` through implementation behavior when surfacing it as a directory key object.

Dependencies include `testFilerClient`, `filer_pb.Entry`, `s3_constants.FolderMimeType`, and `testify/assert`. Integration point is S3 client compatibility for tools that infer directories via ListObjects under trailing-slash prefixes.

Risks: tests cover selected directory shapes but not pagination, URL encoding, versioned buckets, multipart upload folder skipping, or delimiter values other than `/`. They are precise guards against regressions that either hide legitimate empty-directory probes or expose deleted-object directory leftovers as phantom S3 keys.
