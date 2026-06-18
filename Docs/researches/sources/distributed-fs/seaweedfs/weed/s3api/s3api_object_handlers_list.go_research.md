# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_list.go

Purpose: implements S3 ListObjects V1 and V2 over SeaweedFS filer entries, translating hierarchical filer directories into S3 `Contents` and `CommonPrefixes` with marker/continuation-token, delimiter, prefix, URL encoding, owner, versioning, and empty-directory compatibility behavior.

Important APIs and types include `OptionalString`, `ListBucketResultV2`, `listBucketResultV1`, `toListBucketResultV1`, `ListObjectsV2Handler`, `ListObjectsV1Handler`, `sanitizeV1MarkerEcho`, `listFilerEntries`, `ListingCursor`, `normalizePrefixMarker`, `buildTruncatedNextMarker`, `doListFilerEntries`, `getListObjectsV2Args`, `getListObjectsV1Args`, `compareWithDelimiter`, and `adjustMarkerForDelimiter`.

Control flow parses request arguments, rejects invalid max-keys and unordered-with-delimiter combinations, adjusts delimiter-ending markers, calls `listFilerEntries`, checks bucket existence on empty results, and writes V1 or V2 XML. `listFilerEntries` normalizes prefix/marker into a filer directory plus child prefix, hoists versioning state, recursively traverses filer directories with `doListFilerEntries`, appends or deduplicates versioned entries, converts directories to common prefixes or directory-key objects depending on delimiter and MIME, sorts common prefixes with delimiter-aware ordering, and URL-encodes after sorting.

State and persistence are read-only filer stream state. `ListingCursor` tracks remaining max keys, truncation, and trailing-slash prefix probes. Versioned buckets synthesize logical latest object entries from `.versions` directories while skipping delete markers. Real but empty directories can be surfaced as folder markers only for explicit `<dir>/` probes; plain flat listings hide them.

Dependencies include `filer_pb.ListEntries`, S3 XML model types, `newListEntry`, `entryUrlEncode`, bucket/version helpers, and AWS SDK constants. Integration points are S3 bucket list routes, versioning metadata, directory marker semantics, and client compatibility with Hadoop/Spark style directory probes.

Risks include off-by-one truncation, marker exclusivity, delimiter sorting compatibility, duplicate versioned entries, hidden multipart upload folders affecting limits, and distinguishing real directories from S3 directory-key objects. Companion directory tests cover common-prefix directory handling and empty directory probe behavior, but broader pagination and versioning combinations need integration tests.
