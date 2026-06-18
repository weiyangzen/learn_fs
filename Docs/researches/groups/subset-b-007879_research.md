# subset-b-007879 research

Grouped research for SeaweedFS S3 API object-lock, versioning, routed object I/O, path validation, PUT helper, and remote-storage test files under `sources/distributed-fs/seaweedfs/weed/s3api`. Each section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_lock_headers_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_lock_headers_test.go

## Purpose

This test file covers S3 Object Lock header extraction, response-header rendering, request validation, error-code mapping, and documented PUT permission rules. It protects the integration between HTTP headers and `filer_pb.Entry.Extended` metadata used by object retention and legal hold enforcement.

## Important APIs, Types, and Functions

The tests exercise `extractObjectLockMetadataFromRequest`, `addObjectLockHeadersToResponse`, `validateObjectLockHeaders`, and `mapValidationErrorToS3Error`. They assert use of `s3_constants.AmzObjectLockMode`, `AmzObjectLockRetainUntilDate`, `AmzObjectLockLegalHold`, and the internal extended keys for object lock mode, retention-until timestamp, and legal hold.

## Control Flow

`TestExtractObjectLockMetadataFromRequest` builds PUT requests with Object Lock headers, calls the extractor, and checks that mode, legal hold, and retention date are written into `Entry.Extended`. Invalid retention dates and invalid legal hold values must return typed errors and avoid storing invalid fields. `TestAddObjectLockHeadersToResponse` runs the opposite path, converting extended metadata back into HTTP headers, including RFC3339 formatting and defaulting legal hold to `OFF` when retention/mode metadata exists. `TestObjectLockHeaderRoundTrip` verifies request-to-entry-to-response preservation. `TestValidateObjectLockHeaders` checks bucket-versioning requirements, mode/date pair requirements, future date validation, bypass-header rules, and mixed valid headers. `TestMapValidationErrorToS3Error` pins the public S3 error code emitted for each validation error. `TestObjectLockPermissionLogic` is a documentation-style test explaining non-versioned overwrite checks versus versioned create-new-version behavior.

## State and Persistence Behavior

The test state is in-memory `httptest` requests, recorders, and `filer_pb.Entry` values. The persistent contract being tested is that object lock state is serialized into `Entry.Extended` as mode strings, legal hold strings, and Unix-second retention timestamps; those fields later drive object-lock enforcement and HEAD/GET response headers.

## Dependencies and Integration Points

The tests depend on `filer_pb.Entry`, `s3_constants`, `s3err`, `httptest`, `time`, `strconv`, and `testify/assert`. They integrate with implementation helpers likely used by PUT, HEAD, GET, and object-lock handlers outside this file.

## Risks and Edge Cases

Important risks covered include partial extraction on invalid retention dates, invalid legal hold values accidentally persisting, missing legal-hold response defaults, object-lock headers accepted for non-versioned buckets, retention dates in the past, mode/date mismatch, and incorrect S3 error mapping. The permission-logic test is not executable enforcement, so regressions in `checkObjectLockPermissions` still require separate behavioral tests.

## Test Signals

Strong test signals are the round-trip tests, validation matrix, and response-header nil/invalid metadata cases. Remaining gaps are integration tests that exercise real PUT/HEAD/DELETE handlers against a filer and IAM governance-bypass authorization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_lock_headers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_ownership_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_ownership_test.go

## Purpose

This test file verifies how SeaweedFS assigns object owner metadata during S3 PUT-like writes. It focuses on `setObjectOwnerFromRequest`, ensuring bucket object-ownership modes choose either the bucket owner or uploader account and that failure cases fall back safely.

## Important APIs, Types, and Functions

The main test is `TestSetObjectOwnerFromRequest`. It constructs an `S3ApiServer`, optional `BucketRegistry`, `BucketMetaData`, AWS `s3.Owner`, and a `filer_pb.Entry`. The output contract is `entry.Extended[s3_constants.ExtAmzOwnerKey]`. `stringPtr` is a local helper for AWS SDK pointer fields.

## Control Flow

Each table row sets up bucket metadata and an uploader account id in `s3_constants.AmzAccountId`. The test calls `setObjectOwnerFromRequest` and checks whether the owner key was written. `BucketOwnerEnforced` with a valid bucket owner writes the bucket owner id. `ObjectWriter` and `BucketOwnerPreferred` write the uploader. Missing bucket registry, missing metadata, no bucket owner, nil owner ID, and missing uploader all take fallback paths.

## State and Persistence Behavior

No persistent filer writes occur. The tested persistence contract is metadata mutation on a `filer_pb.Entry`: owner identity is stored in the extended attributes map so list/version responses and ACL behavior can later expose correct owner information.

## Dependencies and Integration Points

The test depends on `BucketRegistry` cache internals, `BucketMetaData.ObjectOwnership`, AWS SDK owner structures, `filer_pb.Entry`, and `s3_constants` ownership mode strings. It integrates with bucket metadata loading and account id propagation from authenticated requests.

## Risks and Edge Cases

The key risk is incorrect owner attribution in `BucketOwnerEnforced` mode, which would break S3 Object Ownership semantics. The test also guards nil registry and cache miss behavior. It does not cover ACL grants, bucket-owner-preferred ACL override cases, or multi-account IAM identity lookup beyond the uploaded account id header.

## Test Signals

The table-driven cases give direct coverage for owner selection and fallback behavior. Useful follow-up integration tests would verify owner metadata in ListObjects, ListObjectVersions, and copy/multipart completion paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_ownership_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_retention.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_retention.go

## Purpose

This implementation file provides S3 Object Lock retention, legal hold, and bucket Object Lock configuration helpers. It parses XML bodies, retrieves and mutates object-lock metadata on filer entries, evaluates governance bypass permission, enforces legal hold and retention protections, and validates Object Lock availability.

## Important APIs, Types, and Functions

Key public data types are `ObjectRetention`, `ObjectLegalHold`, `ObjectLockConfiguration`, `ObjectLockRule`, and `DefaultRetention`. `DefaultRetention.UnmarshalXML` tracks whether `Days` and `Years` were explicitly present. Important helpers include `parseXML`, `parseObjectRetention`, `parseObjectLegalHold`, `parseObjectLockConfiguration`, `getObjectEntry`, `getObjectRetention`, `setObjectRetention`, `getObjectLegalHold`, `setObjectLegalHold`, `getRetentionFromEntry`, `getLegalHoldFromEntry`, `checkGovernanceBypassPermission`, `evaluateGovernanceBypassRequest`, `enforceObjectLockProtections`, `isObjectLockAvailable`, and `handleObjectLockAvailabilityCheck`. Sentinel errors distinguish missing config, missing object/version, compliance/governance enforcement, malformed XML, invalid periods, and permission failures.

## Control Flow

XML parsing uses a generic streaming decoder and closes the request body after decoding. Object lookup selects a specific version when `versionId` is present; otherwise it checks bucket versioning and reads either the latest version or the regular object entry. Retention and legal hold getters translate extended metadata into S3 XML response structs and return missing-configuration errors when required fields are absent.

Setters first resolve the filer entry and target entry path. For version-specific updates they write into `.versions/<version-file>`. For versioned latest updates they inspect `ExtVersionIdKey` to decide whether the latest entry is a regular null object or a version file. Retention mutation prevents changing compliance mode or shortening compliance retention, and requires a governance bypass to change or shorten governance retention. It writes mode, Unix-second retain-until date, and WORM compatibility timestamp, then persists through `mkFile`. Legal hold writes the status into extended metadata and also persists through `mkFile`.

Protection enforcement first checks bucket Object Lock status to avoid object lookups on unlocked buckets. If enabled, it loads the relevant entry, tolerates not-found conditions during delete, extracts retention and legal hold, rejects active legal hold, rejects active compliance retention, and rejects governance retention unless a prevalidated bypass is allowed. Governance bypass is granted only when the request has `x-amz-bypass-governance-retention: true` and IAM authorizes either `s3:BypassGovernanceRetention` or admin action on the resource.

## State and Persistence Behavior

State is stored in `filer_pb.Entry.Extended`: object-lock mode, retain-until timestamp, legal hold status, default-retention config on bucket entries, and version id metadata. `setObjectRetention` also updates `WormEnforcedAtTsNs`. Mutations rewrite entries with `mkFile`, preserving chunks and replacing selected metadata. Comments call out a race risk where concurrent retention and legal-hold updates can overwrite each other because the full extended map is rewritten.

## Dependencies and Integration Points

The file depends on `filer_pb`, S3 constants, S3 error mapping, IAM authorization, bucket versioning helpers, object versioning helpers, filer entry fetch/update helpers, and logging. It is used by object-lock REST handlers and by delete/overwrite paths that call `enforceObjectLockProtections`.

## Risks and Edge Cases

Important risks include stale or corrupted retention timestamps, concurrent metadata rewrites losing fields, governance bypass authorization drift, object lookup differences between versioned, suspended, null, and unversioned states, and returning nil enforcement when bucket lookup returns not found. Compliance retention is intentionally stricter than governance retention. The code depends on wall-clock `time.Now()` for active-retention checks.

## Test Signals

Companion tests cover XML parsing, validation, default retention, header round trips, and stale day/year cleanup. Higher-level integration tests should cover actual REST handlers, IAM bypass policy, concurrent legal-hold and retention updates, and version-specific deletion under WORM conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_retention.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_retention_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_retention_test.go

## Purpose

This test file validates Object Lock retention and legal-hold parsing and validation logic. It also tests bucket Object Lock configuration parsing, default retention constraints, and persistence cleanup when switching default-retention units.

## Important APIs, Types, and Functions

Tests cover `ValidateRetention`, `ValidateLegalHold`, `parseObjectRetention`, `parseObjectLegalHold`, `parseObjectLockConfiguration`, `ValidateObjectLockConfiguration`, `validateDefaultRetention`, `StoreObjectLockConfigurationInExtended`, `LoadObjectLockConfigurationFromExtended`, and `CreateObjectLockConfiguration`. `timePtr` is a local helper.

## Control Flow

The retention validation matrix checks valid governance/compliance modes, missing fields, invalid mode, past dates, and empty structs. Legal hold validation accepts only uppercase `ON` and `OFF`. XML parsing tests cover namespace and no-namespace payloads for retention, legal hold, and bucket configuration, plus empty and malformed XML. Bucket Object Lock configuration tests cover `ObjectLockEnabled`, optional rule/default retention, days versus years, mode validation, and maximum bounds. The stale-years test starts with persisted years metadata, stores a days-based config, and verifies the old years key is removed before reloading.

## State and Persistence Behavior

All state is in-memory request bodies and `filer_pb.Entry.Extended`. The tests verify that XML presence bits for `DaysSet` and `YearsSet` survive unmarshalling and that storage helpers avoid stale metadata when a config changes from years to days.

## Dependencies and Integration Points

The file depends on `filer_pb.Entry`, `s3_constants`, XML body parsing through HTTP request bodies, and validation helpers implemented outside the test file. It integrates with bucket metadata persistence because Object Lock config is stored in extended attributes.

## Risks and Edge Cases

Risks covered include accepting lowercase legal hold values, missing mode/date fields, malformed XML, namespace compatibility with clients such as Veeam, both days and years being present, neither being present, out-of-range retention durations, and stale default-retention fields persisting across config updates. The tests do not exercise actual HTTP handlers or filer writes.

## Test Signals

The table-driven matrices are strong signals for pure validation and parser behavior. Remaining gaps are end-to-end PutObjectRetention/GetObjectRetention and PutObjectLockConfiguration/GetObjectLockConfiguration flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_retention_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_routed_read.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_routed_read.go

## Purpose

This file implements route-by-key object entry reads for multi-filer deployments. It prefers the filer that owns an object's write route so a read can observe a just-written object before cross-filer replication reaches the local/default filer.

## Important APIs, Types, and Functions

The main function is `getObjectEntryRoutedByKey(bucket, object)`. Supporting helpers are `priorWriteOwner`, `markOwnerUnreachable`, `ownerRecentlyUnreachable`, and `lookupEntryOnFiler`. `unreachableOwnerTTL` is a two-second skip window for recently failed owner reads.

## Control Flow

The read path builds the full filer path, resolves the current write owner with `routableWriteOwner`, and falls back to normal `GetEntry` if no owner or filer client is available. If the owner was recently marked unreachable, it reads local/default first to avoid repeated failed dials. Otherwise it uses `withFilerClientFailover` to call `LookupEntry` on the preferred owner. When the owner returns `ErrNotFound`, the code asks the lock client for the prior owner and probes it once to cover ring rebalance windows.

## State and Persistence Behavior

No persistent state is written. In-memory state is a `sync.Map`-style `unreachableOwners` map from owner address to expiry time. Filer state is read by `LookupDirectoryEntry`.

## Dependencies and Integration Points

The file depends on `pb.WithFilerClient`, `filer_pb.LookupEntry`, route-key helpers from routed write code, object write lock client ownership APIs, and `util.FullPath`. It integrates with S3 GET/HEAD entry lookup paths and with owner failover/rebalance behavior.

## Risks and Edge Cases

Risks include stale ring ownership, owner transport failures, false-positive recent-unreachable skips, and prior-owner probes returning stale data during rebalances. The TTL is deliberately short, trading extra local reads for faster owner recovery. Empty object names and missing lock clients bypass routing.

## Test Signals

The companion test verifies the unreachable-owner flag behavior. Integration tests should cover just-written reads, owner failover, and prior-owner fallback during a simulated ring move.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_routed_read.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_routed_read_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_routed_read_test.go

## Purpose

This test file pins the in-memory unreachable-owner cache used by routed reads. It ensures owner addresses marked after read failures are skipped for the TTL window and that unrelated owners are not affected.

## Important APIs, Types, and Functions

`TestOwnerRecentlyUnreachable` calls `ownerRecentlyUnreachable` and `markOwnerUnreachable` on an `S3ApiServer`. It uses `pb.ServerAddress` values as owner keys.

## Control Flow

The test starts with an unmarked owner and expects a false result, marks that owner unreachable, expects true for the same owner, and then verifies a different owner remains false.

## State and Persistence Behavior

State is only in the server's in-memory unreachable-owner map. No filer or disk state is touched.

## Dependencies and Integration Points

The test depends on the routed-read helper methods and `pb.ServerAddress`. It indirectly protects `getObjectEntryRoutedByKey` from repeatedly dialing an owner that recently failed.

## Risks and Edge Cases

The test does not wait past `unreachableOwnerTTL`, so expiration behavior is not directly covered. It also does not test concurrent map access or integration with `withFilerClientFailover`.

## Test Signals

The test is a focused unit signal for owner marking isolation. Broader routed-read tests should simulate lookup failures and owner recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_routed_read_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_routed_write.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_routed_write.go

## Purpose

This file implements owner-routed object write helpers. It routes PUT, multipart completion, metadata replacement, and eligible deletes to a deterministic owner filer using a shared object route key, reducing distributed-lock contention and improving consistency for concurrent writes to the same object.

## Important APIs, Types, and Functions

Key functions are `objectRouteKey`, `routableWriteOwner`, `routedObjectOwner`, `routeWriteCondition`, `buildWriteCondition`, `buildDeleteCondition`, `singleStrongETag`, `objectTxnOnFiler`, `routedPut`, `routedMkFile`, `writeMultipartObject`, `routedDelete`, and `routedMetadataReplace`. Helper constructors `clause` and `etagClause` build `filer_pb.WriteCondition` clauses. `objectWriteRouteKeyPrefix` namespaces ring keys.

## Control Flow

Writes hash `s3.object.write:<filer path>` through `objectWriteLockClient`. Versioned and object-lock PUTs can route because versioned PUT creates a new version and unversioned overwrites are checked at the gateway. Non-versioned deletes route only when versioning is not configured and Object Lock is not enabled. Conditional routing is conservative: simple `If-Match`/`If-None-Match` with `*` or a single strong ETag becomes a filer `WriteCondition`; weak ETags, ETag lists, time conditions, or combined match/none-match fall back to the lock path. Unique version paths route only for unconditional writes because conditional versioned writes must check latest state.

`routedPut` sends one `ObjectTransaction` containing a PUT mutation plus optional finalize mutations under a lock key. `routedMkFile` builds a normal filer entry and writes it via `routedPut`. `writeMultipartObject` chooses routed or normal `mkFile`. `routedDelete` sends a DELETE mutation with optional condition. `routedMetadataReplace` uses `PATCH_EXTENDED` to merge managed metadata changes under lock, deleting managed keys that were dropped while preserving non-managed keys such as legal hold, retention, and version id.

## State and Persistence Behavior

Persistent changes are applied by owner filer `ObjectTransaction` mutations: PUT, DELETE, and PATCH_EXTENDED. Route keys are included so a stale gateway-to-owner view can be corrected by filer-side routing. Metadata replacement intentionally avoids whole-entry rewrites to reduce races with concurrent retention/legal-hold mutations.

## Dependencies and Integration Points

The file depends on `filer_pb.ObjectTransaction`, conditional-header parsing, `s3_constants`, route ownership APIs, `pb.WithFilerClient`, `util.FullPath`, and local metadata-copy helper functions. It integrates with PutObject, multipart completion, DeleteObject, CopyObject metadata replacement, versioned finalize helpers, and object-lock enforcement.

## Risks and Edge Cases

Risks include routing a conditional write that needs gateway-side evaluation, stale owner ring views, transaction errors reported through `resp.Error`, metadata patch delete-list mistakes, and bypassing object-lock/versioning checks for deletes. The code mitigates this by only routing simple conditions and by excluding configured versioning and object-lock buckets from the unversioned delete fast path.

## Test Signals

Companion tests cover condition reduction, strong ETag parsing, HTTP date parsing in related conditional paths, delete condition reduction, and unique-version routing restrictions. Integration tests should cover actual object transactions on owner filers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_routed_write.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_routed_write_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_routed_write_test.go

## Purpose

This test file validates routed write condition reduction and related conditional-date parsing. It ensures only conditions that can be safely enforced by filer-side `WriteCondition` are routed.

## Important APIs, Types, and Functions

Tests cover `buildWriteCondition`, `parseConditionalHeaders`, `validateConditionalCopyHeaders`, `buildDeleteCondition`, `singleStrongETag`, and `routeWriteCondition`. Local helpers `reqWith` and `oneClause` build requests and inspect single-clause conditions.

## Control Flow

The write-condition tests verify unconditional requests, `If-None-Match: *`, `If-Match: *`, single strong ETags, weak ETags, ETag lists, combined match/none-match headers, and time-based conditions. Date parsing tests ensure RFC850, ANSIC, and RFC1123-with-UTC variants are accepted for regular and copy conditional headers. Delete condition tests cover only `If-Match`, matching DeleteObject semantics. Route-condition tests verify unconditional versioned writes can route, conditional overwrites can route when reducible, conditional unique writes cannot route, and weak ETags force fallback.

## State and Persistence Behavior

No persistent state is mutated. The tests construct `filer_pb.WriteCondition` values and check their clauses.

## Dependencies and Integration Points

The file depends on `filer_pb.WriteCondition`, S3 conditional header constants, S3 error codes, and timestamp parsing behavior. It protects the boundary between gateway conditional logic and owner-filer transaction conditions.

## Risks and Edge Cases

The main risk is incorrectly routing conditions whose semantics require reading latest object state or complex HTTP precondition evaluation. The tests specifically guard weak ETags, lists, mixed headers, and time headers. They do not test filer-side enforcement itself.

## Test Signals

These are strong unit signals for condition classification. End-to-end tests should verify precondition failures through routed PUT, routed multipart completion, and routed delete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_routed_write_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_versioned_finalize.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_versioned_finalize.go

## Purpose

This file provides routed finalize and routed version-delete helpers for versioned objects. It lets the owner filer atomically recompute `.versions` latest-pointer metadata, demote previous latest versions, and delete specific versions under the object's per-path lock.

## Important APIs, Types, and Functions

Key functions are `objectWriteOwner`, `latestPointerRecompute`, `routedVersionedFinalize`, `wormDeleteCondition`, `routedDeleteSpecificVersion`, `routedDeleteNullVersion`, and `versionedFinalize`. The central mutation type is `filer_pb.ObjectMutation_RECOMPUTE_LATEST`; conditions use `filer_pb.WriteCondition`.

## Control Flow

`latestPointerRecompute` builds a recompute mutation over the object's `.versions` directory. It copies version metadata into latest-pointer extended keys, uses ascending or descending scan behavior depending on new inverted version id format, can exclude a version about to be deleted, and can stamp the displaced prior latest with `ExtNoncurrentSinceNsKey`. `routedVersionedFinalize` sends that recompute as a single owner transaction. `wormDeleteCondition` builds legal-hold and retention guards for object-lock buckets; governance bypass changes the retention clause so only compliance mode remains gated. `routedDeleteSpecificVersion` validates the version id, recomputes latest excluding the target, and deletes the version file in one owner transaction. `routedDeleteNullVersion` deletes the regular object entry with optional WORM condition. `versionedFinalize` returns a `putFinalize` that uses routed recompute when possible and falls back to `updateLatestVersionInDirectory` after create.

## State and Persistence Behavior

Persistent state lives in `.versions` directory metadata and version file entries. Recompute updates latest version id, latest filename, cached size, mtime, ETag, owner, delete-marker flag, and noncurrent timestamp. Routed deletes remove either `.versions/v_<id>` entries or null regular object entries, optionally deleting chunk data.

## Dependencies and Integration Points

This file depends on route-key helpers, version id format helpers, filer object transactions, Object Lock constants, S3 error mapping, and `putFinalize` used by PutObject. It integrates with versioned PUT, delete-specific-version, null-version deletion, lifecycle noncurrent logic, and WORM enforcement.

## Risks and Edge Cases

Risks include choosing the wrong scan direction for old versus new version ids, recomputing a pointer while excluding the wrong filename, incorrectly demoting prior latest, and mapping WORM precondition failures to client-visible errors. The atomic transaction design reduces dangling-pointer risk compared with separate update/delete operations.

## Test Signals

Direct tests are in versioning self-heal and routed write test files rather than here. Useful integration tests should cover routed versioned PUT, routed delete of current/latest version, delete markers, null version deletion, and object-lock precondition failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_versioned_finalize.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_versioning.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_versioning.go

## Purpose

This is the core SeaweedFS S3 object versioning implementation. It stores versions under hidden per-object `.versions` directories, maintains cached latest-version metadata on the directory entry, creates delete markers, lists versions, retrieves specific/latest versions, deletes versions, and self-heals stale latest pointers.

## Important APIs, Types, and Functions

Important data types include `S3ListObjectVersionsResult`, `VersionListEntry`, `ObjectVersion`, `versionListItem`, and `versionCollector`. Key functions include `clearCachedVersionMetadata`, `markVersionNoncurrent`, `setCachedListMetadata`, `createDeleteMarker`, `createNullDeleteMarker`, `listObjectVersions`, `buildSortedCombinedList`, `truncateAndSetMarkers`, `splitIntoResult`, `findVersionsRecursively`, `versionCollector.collectVersions`, `getObjectVersionList`, `calculateETagFromChunks`, `getSpecificObjectVersion`, `deleteSpecificObjectVersion`, `repointLatestBeforeDeletion`, `retryFilerOp`, `updateLatestVersionAfterDeletion`, `clearStaleLatestVersionPointer`, `ListObjectVersionsHandler`, `getLatestObjectVersion`, `recoverLatestVersionWithoutPointer`, `versionIdFromEntry`, `selectLatestVersion`, `scanLatestVersionEntry`, `healStaleLatestVersionPointer`, `getLatestVersionEntryFromDirectoryEntry`, `recoverLatestListEntryByScan`, and owner helpers.

## Control Flow

Version creation writes version files into `bucket/object.versions/` using generated old or new-format version ids. Delete marker creation writes a version file tagged with `ExtDeleteMarkerKey` and then updates or recomputes the `.versions` latest pointer. Suspended-versioning delete uses a special `null` delete marker that overwrites the fixed null version slot.

Listing walks the bucket recursively, collecting `.versions` directories, explicit directory marker objects, regular/null objects, and common prefixes. `versionCollector` applies prefix, delimiter, key-marker, version-id-marker, duplicate, and max-collection filters. Results are merged into one sorted list so `Version`, `DeleteMarker`, and `CommonPrefixes` can be emitted in S3 order with custom XML element names.

Specific-version reads validate version ids and map `null` to the regular object path while non-null versions read `.versions/v_<id>`. Latest-version reads use the cached pointer on the `.versions` directory. If the directory or pointer is missing, the code falls back to pre-versioning/null regular objects or rescans the versions directory. If the pointer references a missing version file, `healStaleLatestVersionPointer` scans remaining entries and persists a repaired pointer best-effort.

Version deletion validates ids, handles null-version deletion separately, and detects whether the deleted version is latest. When deleting current latest, `repointLatestBeforeDeletion` scans for the next-newest other version and updates or clears the pointer before removing the blob. This makes failures leave recoverable orphan blobs rather than dangling pointers. After deletion, `updateLatestVersionAfterDeletion` can rescan, update pointer metadata, remove empty `.versions` directories, clear stale pointers when only orphan entries remain, and enqueue reconciliation on persistent failure.

## State and Persistence Behavior

Persistent state is split between regular object entries, `.versions` child entries, and `.versions` directory extended metadata. Extended keys include version id, delete marker, latest version id, latest filename, cached latest size/mtime/ETag/owner/delete-marker flag, noncurrent timestamp, storage class, and owner. Filer mutations use `mkFile`, `updateEntry`, `rm`, `rmObject`, and list/get operations. Retry wrappers handle transient filer failures for load-bearing pointer updates. Self-heal functions may repair pointer metadata or clear stale pointer fields while leaving orphan files for later cleanup.

## Dependencies and Integration Points

The file depends on filer listing and ETag helpers, version id format/comparison helpers, S3 constants and errors, logging, gRPC status codes, object-lock/versioned finalize helpers, lifecycle noncurrent metadata, list response XML types, IAM owner lookup, and an optional version-heal queue. It integrates with GET/HEAD, DELETE, ListObjectVersions, regular ListObjects via cached latest entries, PutObject versioned finalization, lifecycle processing, and remote-storage/copy paths.

## Risks and Edge Cases

High-risk areas include multi-page `.versions` scans, mixed old/new version id formats, delete markers being the current latest, stale latest pointers, missing extended metadata, orphan files, concurrent writers during pointer clear, transient filer errors after blob deletion, and differences between versioned, suspended, null, and pre-versioning objects. The code deliberately promotes newest delete markers during self-heal so reads preserve S3 deleted-object semantics rather than resurrecting older content.

## Test Signals

Self-heal tests cover `selectLatestVersion` and `versionIdFromEntry` behavior for mixed formats, delete markers, empty/untagged entries, filename fallback, and untagged delete markers. Routed write tests cover conditional transaction pieces. Additional integration tests are needed for full PUT/DELETE/LIST flows with real filer state, multi-page directories, and concurrent pointer repair.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_versioning.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_versioning_self_heal_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_versioning_self_heal_test.go

## Purpose

This test file validates the pure selection logic used by versioning self-heal. It ensures stale pointer repair selects the chronologically newest version entry, including delete markers and filename-only version files.

## Important APIs, Types, and Functions

The tests exercise `selectLatestVersion` and `versionIdFromEntry`. Helpers `newVersionEntry` and `newUntaggedVersionFile` build synthetic `.versions` child entries. The tests use version-id helpers such as `createOldFormatVersionId` and `createNewFormatVersionId`.

## Control Flow

Cases verify mixed old/new format comparison, newest delete marker selection, content winning when newer than a delete marker, only-delete-marker directories, empty or untagged entries returning no latest, attribute-first version id extraction, filename fallback for `v_<id>`, mixed tagged and untagged entries, and delete marker recognition when the version id is derived from filename.

## State and Persistence Behavior

The file uses in-memory `filer_pb.Entry` slices only. It models `.versions` directory children and their extended metadata without touching a filer.

## Dependencies and Integration Points

The tests depend on version id comparison/format helpers, `filer_pb.Entry`, `s3_constants.ExtVersionIdKey`, and `ExtDeleteMarkerKey`. They protect `healStaleLatestVersionPointer`, `recoverLatestVersionWithoutPointer`, `updateLatestVersionAfterDeletion`, and list recovery paths that call `selectLatestVersion`.

## Risks and Edge Cases

The covered risk is accidental resurrection of deleted objects by selecting an older content version over a newer delete marker. Another key risk is ignoring entries written outside the normal PUT path that have valid `v_<id>` filenames but missing extended version id metadata. The tests do not cover persistence of repaired pointers.

## Test Signals

The unit coverage is strong for selector semantics. Integration tests should combine these cases with actual `.versions` scans and pointer persistence failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_versioning_self_heal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_path_validation.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_path_validation.go

## Purpose

This file implements request path validation middleware for S3 routes. It prevents bucket, object, `versionId`, and `uploadId` path segments from normalizing into parent-directory traversal or unsafe filer entry names.

## Important APIs, Types, and Functions

Key functions are `hasPathSegmentQuery`, `hasInvalidPathSegment`, and `validateRequestPath`. The middleware uses `mux.Vars`, `s3_constants.IsValidBucketName`, `IsValidObjectKey`, `IsValidPathSegment`, and `s3err.WriteErrorResponse`.

## Control Flow

`hasPathSegmentQuery` cheaply checks raw query text for `versionId` or `uploadId`, including percent-encoded query names, while avoiding allocation on common unrelated queries without percent escapes. `validateRequestPath` reads mux-captured `bucket` and `object` variables, rejects empty or invalid bucket/object values, and only parses query values when path-segment query keys are present. Invalid values produce `ErrInvalidRequest`; otherwise the wrapped handler is called.

## State and Persistence Behavior

The middleware has no persistent state. It protects downstream filer path construction, where path joins would otherwise collapse `..`, `.`, slashes, or backslashes into a different bucket/object path.

## Dependencies and Integration Points

The file depends on Gorilla mux and S3 validation constants. It integrates with production routing using `SkipClean(true)`, where unsafe segments survive routing and must be rejected before IAM authorization and filer access.

## Risks and Edge Cases

The primary security risk is authorizing one bucket while reading or mutating another after path normalization. Query values are also risky because version ids and upload ids can become filer entry names. The raw-query fast path must recognize encoded query names without imposing allocation overhead on common list queries.

## Test Signals

Companion tests cover traversal, encoded traversal, empty mux captures, unsafe query values, encoded query names, unrelated query pass-through, and zero allocations for common unrelated queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_path_validation.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_path_validation_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_path_validation_test.go

## Purpose

This test file validates the S3 path-validation middleware's security and performance behavior. It ensures unsafe path and query segments are rejected before inner handlers run.

## Important APIs, Types, and Functions

Tests cover `validateRequestPath` and `hasPathSegmentQuery`. They use `mux.NewRouter().SkipClean(true)`, `mux.SetURLVars`, `httptest`, and standard HTTP status assertions.

## Control Flow

`TestValidateRequestPath_RejectsTraversal` mirrors production bucket/object routes and sends raw request URIs with clean paths, bucket-only paths, trailing slash paths, `..`, `.`, backslash traversal, percent-encoded traversal, and invalid bucket captures. `TestValidateRequestPath_RejectsEmptyCapturedVars` injects empty mux variables directly as defense in depth. `TestValidateRequestPath_RejectsUnsafePathQueryValues` checks `versionId` and `uploadId` values, including encoded slash/backslash traversal and repeated values. `TestHasPathSegmentQuery_CommonPathDoesNotAllocate` asserts unrelated queries do not allocate.

## State and Persistence Behavior

No persistent state is changed. The tests observe response codes and whether the wrapped handler was invoked.

## Dependencies and Integration Points

The file depends on Gorilla mux route behavior and the validation middleware. It protects the boundary between HTTP routing, IAM authorization, and filer path normalization.

## Risks and Edge Cases

The tests cover the exact class of traversal where `/{bucket}/{object}` captures would later be normalized by the filer into another bucket path. Remaining risks include future changes to bucket/object validation helpers and additional query parameters that become path-like entry names but are not included in this middleware.

## Test Signals

The route-level tests are strong security regression signals, and the allocation test protects the hot query path used by listing APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_path_validation_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_put_handlers.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_put_handlers.go

## Purpose

This file centralizes server-side encryption processing for PUT-to-filer paths. It wraps request bodies with SSE-C, SSE-KMS, and SSE-S3 encryption readers and returns metadata needed for object headers and later decryption.

## Important APIs, Types, and Functions

`PutToFilerEncryptionResult` carries the final data reader, SSE type, customer key, IV, KMS key, S3 key, and serialized KMS/S3 metadata. Functions include `handleSSECEncryption`, `handleSSEKMSEncryption`, `handleSSES3MultipartEncryption`, `handleSSES3SinglePartEncryption`, `handleSSES3Encryption`, and `handleAllSSEEncryption`.

## Control Flow

SSE-C parsing validates customer-provided headers and wraps the reader with customer-key encryption when present. SSE-KMS detects KMS headers, builds default bucket/object encryption context, merges optional user context, handles multipart base IV plus part offset or single-part generated IV, serializes KMS metadata, and returns errors for bad context or encryption failures. SSE-S3 detects internal S3-managed encryption, either decodes multipart key/base-IV metadata and derives an offset-adjusted IV, or creates/stores a new key for single-part uploads. `handleAllSSEEncryption` applies SSE-C, then KMS, then SSE-S3, updating the reader after each step and selecting the response SSE type by the first active mode.

## State and Persistence Behavior

The file does not write filer entries directly. It creates encrypted reader streams and serialized metadata that callers persist into object extended metadata. SSE-S3 single-part handling stores generated keys in the S3 key manager; multipart handling stores the derived IV on the key before serialization so decryption uses the correct part offset.

## Dependencies and Integration Points

Dependencies include SSE-C/KMS/S3 helper functions, S3 header constants, KMS encryption context parsing, key managers, base64 decoding, request bucket/object extraction, and S3 error mapping. It integrates with PutObject and multipart upload code that sends encrypted chunks to the filer and records SSE metadata.

## Risks and Edge Cases

Risks include applying multiple SSE layers if incompatible headers are not rejected elsewhere, losing the derived IV for multipart SSE-S3, accepting malformed base IV/key metadata, incorrect KMS encryption context merge, and returning generic internal errors for client-supplied internal headers. The chain order matters because each step wraps the output of the previous one.

## Test Signals

No direct tests are in this subset for this file. Adjacent SSE tests should verify single-part and multipart encryption/decryption, metadata serialization, invalid headers, and mutually exclusive SSE modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_put_handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_put_object_helper.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_put_object_helper.go

## Purpose

This helper file chooses the correct request body reader for S3 PUT processing. Its main concern is AWS chunked streaming payloads, especially unsigned streaming payloads when IAM authentication is disabled.

## Important APIs, Types, and Functions

The sole function is `getRequestDataReader(s3a, r)`, returning an `io.ReadCloser` and `s3err.ErrorCode`. It uses `getRequestAuthType`, `s3a.iam.isEnabled`, and `s3a.iam.newChunkedReader`.

## Control Flow

The function starts with the raw request body. When IAM is enabled, streaming signed and streaming unsigned requests are both passed through the IAM chunked reader. When IAM is disabled, streaming signed requests fail with `ErrAuthNotSetup`, but streaming unsigned requests are still processed by `newChunkedReader` so chunk framing and checksum trailers are stripped before storage. Non-streaming requests pass through unchanged.

## State and Persistence Behavior

No persistent state is changed. The returned reader controls what bytes are eventually written to the filer; choosing the raw body for chunked streaming would persist AWS chunk metadata as object data.

## Dependencies and Integration Points

The helper depends on IAM auth-type detection and chunked-reader implementation. It integrates with PutObject and upload-part handlers before encryption and filer writes.

## Risks and Edge Cases

The major risk is corrupting stored object bytes when IAM is off but clients send `STREAMING-UNSIGNED-PAYLOAD-TRAILER`. Conversely, accepting signed streaming without IAM would skip signature validation, so it correctly fails. The function assumes `s3a.iam` is initialized.

## Test Signals

Companion tests cover regular, streaming signed, streaming unsigned with IAM disabled, checksum trailers, IAM-enabled unsigned streaming, and auth-type detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_put_object_helper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_put_object_helper_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_put_object_helper_test.go

## Purpose

This test file verifies `getRequestDataReader` behavior for regular and AWS chunked streaming PUT bodies with IAM enabled and disabled. It specifically guards against storing chunked transfer framing as object content when authentication is off.

## Important APIs, Types, and Functions

Tests cover `getRequestDataReader` and `getRequestAuthType`. They construct `S3ApiServer` instances with memory-backed IAM, toggle `isAuthEnabled`, and assert `s3err` results and whether the returned reader is the raw body or a chunked reader.

## Control Flow

`TestGetRequestDataReader_ChunkedEncodingWithoutIAM` checks regular pass-through, signed streaming rejection with `ErrAuthNotSetup`, and unsigned streaming processing without IAM. `TestGetRequestDataReader_AuthTypeDetection` uses `STREAMING-UNSIGNED-PAYLOAD-TRAILER` with a checksum trailer and verifies both auth-type detection and reader replacement. `TestGetRequestDataReader_IAMEnabled` verifies unsigned streaming is processed when IAM is enabled. `TestAuthTypeDetection` covers signed, unsigned, and regular header classification.

## State and Persistence Behavior

No filer state is touched. The important persistence implication is that the chosen reader decides whether checksum trailer framing is stripped before upload bytes are stored.

## Dependencies and Integration Points

The file depends on the memory credential store, IAM initialization, auth-type constants, S3 error codes, and standard HTTP request bodies. It integrates with PUT/upload-part reader preparation.

## Risks and Edge Cases

The tests cover the known regression where chunked data plus checksum headers was stored incorrectly with IAM disabled. They do not parse a full chunked payload to assert output bytes, only that a different reader is selected.

## Test Signals

The reader identity checks are good classification signals. A stronger integration test would feed a real AWS chunked body and verify decoded content bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_put_object_helper_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_remote_storage_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_remote_storage_test.go

## Purpose

This test file documents and verifies S3 behavior for remote-only filer entries, remote object caching paths, versioned remote paths, source version id resolution, and copy behavior for remote-only sources.

## Important APIs, Types, and Functions

Tests cover `filer_pb.Entry.IsInRemoteOnly`, logic mirrored from `streamFromVolumeServers`, versioned path construction used by remote caching, `resolvedSourceVersionId`, `cachedEntryHasLocalData`, and remote-only copy source detection. `removeDuplicateSlashesTest` mirrors production normalization for path-building tests.

## Control Flow

`TestIsInRemoteOnly` classifies entries with remote metadata, local chunks, zero remote size, and nil remote entry. `TestRemoteOnlyEntryDetection` mirrors streaming logic that distinguishes remote-only entries from corrupt local entries and empty files. `TestVersionedRemoteObjectPathBuilding` checks directory/name selection for empty version id, null version, specific version, nested keys, and leading slashes. `TestResolvedSourceVersionId` ensures explicit request version id wins, while latest-version reads can fall back to the entry's `ExtVersionIdKey`. `TestCachedEntryHasLocalData` checks chunks and inline content. `TestCopyObjectRemoteOnlySourceDetection` guards against copying a remote-only non-empty source through the inline branch with no content, which would create a destination with size but no chunks.

## State and Persistence Behavior

All state is synthetic `filer_pb.Entry` data. The persistent contracts under test are remote-entry metadata (`RemoteEntry.RemoteSize`), chunk/content presence, versioned `.versions/v_<id>` cache paths, and version id extended metadata.

## Dependencies and Integration Points

The file depends on `filer.FileSize`, `filer_pb.Entry`, `filer_pb.RemoteEntry`, S3 constants, and helper functions implemented in remote streaming/copy code. It integrates with GET streaming, cache-on-read from remote storage, CopyObject, and versioned object access.

## Risks and Edge Cases

Risks include mistaking remote-only objects for corrupt local entries, treating zero-byte remote objects as cache misses that should fail, building wrong cache paths for versioned objects, losing latest version id when the request does not specify one, and creating broken copy destinations with `FileSize > 0` but no chunks/content.

## Test Signals

The tests are strong unit-level signals for classification and path construction. Full confidence requires integration tests with configured remote storage, cache fill, versioned remote GET, and CopyObject from remote-only sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_remote_storage_test.go -->
