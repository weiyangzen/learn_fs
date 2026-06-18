# subset-b-008233 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/list_object_versions_regression_test.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/list_object_versions_regression_test.rs

Purpose: End-to-end regression coverage for RustFS `ListObjectVersions` behavior. The file protects two object-version listing edge cases: issue #2252, where a newest version created immediately after a delete marker could be missing or incorrectly marked, and prefix traversal where an object named like a prefix marker must not hide child objects under the slash-suffixed prefix.

Important APIs/types/functions: The tests use `RustFSTestEnvironment`, `init_logging`, `env.start_rustfs_server`, `env.create_s3_client`, AWS SDK S3 `Client`, `ByteStream`, `BucketVersioningStatus`, and `VersioningConfiguration`. The local helper `create_s3_client` only wraps the environment factory. The test operations are S3 `create_bucket`, `put_bucket_versioning`, `put_object`, `delete_object`, and `list_object_versions`.

Control flow: `test_list_object_versions_immediately_returns_latest_put_after_delete_marker` starts a fresh RustFS server, creates a bucket, enables versioning, writes a first object version, deletes it to create a delete marker, writes a second version, then calls `list_object_versions` twice with the exact key as prefix. It collects versions and delete markers from both responses and asserts stable counts and `is_latest` flags. `test_list_object_versions_prefix_with_marker_object_returns_children` starts a fresh server, creates a bucket, suspends versioning, creates a zero-byte marker object `data01`, writes two child objects under `data01/meta/...`, lists versions with prefix `data01/`, and verifies only the children are returned.

State and persistence behavior: The first test depends on RustFS persisting version metadata and delete-marker metadata in the immediately visible object namespace. It captures returned `version_id` values from each mutation and uses them to distinguish original version, delete marker, and newest version. The second test uses suspended versioning, so the state under inspection is the null-version/listing representation of marker and child keys rather than multiple generated versions.

Dependencies and integration points: This file integrates the e2e test harness with the S3-compatible versioning API, delete-marker creation, object namespace prefix filtering, and RustFS server lifecycle. The tests are marked `#[serial]`, which matters because they start and stop external server state and use fixed bucket names.

Risks: The assertions are intentionally strict about returned counts and latest flags, but they do not inspect ordering. The first test does not stop the server explicitly, so cleanup relies on the environment drop path. Fixed bucket names are safe under serialized isolated runs but would be collision-prone if the serial constraint were removed. The prefix-marker case uses suspended versioning only; enabled-versioning behavior for the same key pattern is not covered here.

Test signals: Strong signals are exactly two object versions plus one delete marker on both immediate listings, newest `version_id` marked `is_latest=true`, older object and delete marker marked non-latest, and `ListObjectVersions(prefix="data01/")` returning both expected child object keys despite the presence of `data01`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/list_object_versions_regression_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/list_objects_duplicates_test.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/list_objects_duplicates_test.rs

Purpose: End-to-end regression tests for duplicate results in `ListObjectsV2`. The file protects common-prefix de-duplication when explicit directory marker objects exist, and content de-duplication/order when listing below a prefix without a delimiter.

Important APIs/types/functions: It uses `RustFSTestEnvironment`, `init_logging`, AWS SDK S3 `Client`, `ByteStream`, `serial_test::serial`, and `tracing::info`. Helpers include `create_s3_client` and a retrying `create_bucket` that tolerates `BucketAlreadyOwnedByYou` and `BucketAlreadyExists` and retries transient creation failures up to 20 times.

Control flow: `test_list_objects_v2_unique_common_prefixes` creates `folder/file.txt` and a zero-byte `folder/` marker, then lists the bucket with `delimiter("/")`. It filters `result.common_prefixes()` for `folder/` and asserts there is exactly one entry, then asserts the explicit marker is not also exposed in `Contents`. `test_list_objects_v2_unique_contents_with_explicit_directory_markers` creates `marker/`, `marker/subdir/`, `marker/file.txt`, and `marker/subdir/file.txt`, lists with `prefix("marker/")` and no delimiter, collects content keys, and asserts the exact four-key lexicographic sequence and `key_count=4`.

State and persistence behavior: The tests persist real object keys into a temporary RustFS bucket. The first test checks the delimiter projection layer, where raw keys and marker objects collapse into `CommonPrefixes`. The second checks the flat object listing state under a prefix, where marker objects should appear as normal objects when no delimiter is supplied and nested file keys must not be duplicated.

Dependencies and integration points: These tests exercise the RustFS S3 ListObjectsV2 implementation through the AWS SDK, especially the interaction between object-store key iteration, delimiter rollup, prefix filtering, `Contents`, `CommonPrefixes`, and `KeyCount` serialization. They model behavior used by backup tools such as Veeam that create zero-byte slash-ending folder markers.

Risks: The first test encodes a specific interpretation that `folder/` should be represented only as a common prefix when delimiter `/` is supplied, not also as an object. This is compatible with the target regression but should be reviewed if RustFS intentionally changes directory-marker compatibility behavior. The bucket helper retries for server readiness but uses string matching on SDK error text. Fixed bucket names require serialized execution.

Test signals: Signals are one and only one `CommonPrefix` with prefix `folder/`, no `Contents` object keyed `folder/` in delimiter mode, exact `Contents` vector `marker/`, `marker/file.txt`, `marker/subdir/`, `marker/subdir/file.txt`, and `result.key_count() == Some(4)`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/list_objects_duplicates_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/list_objects_v2_metadata_extension_test.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/list_objects_v2_metadata_extension_test.rs

Purpose: End-to-end regression coverage for RustFS's nonstandard ListObjectsV2 metadata extension exposed by `GET /{bucket}?list-type=2&metadata=true`. It verifies that object user metadata, object tags, and internal placement fields are serialized in the listing XML response.

Important APIs/types/functions: The file uses `RustFSTestEnvironment`, `init_logging`, `local_http_client`, `reqwest::StatusCode`, `http::header::HOST`, `rustfs_signer::sign_v4`, `rustfs_signer::constants::UNSIGNED_PAYLOAD`, `s3s::Body`, and `urlencoding::encode`. The helper `signed_get` builds a raw HTTP GET request, signs it with AWS Signature V4, copies signed headers into a reqwest request, and sends it through the local HTTP client.

Control flow: The test starts RustFS, creates a bucket, uploads `objects/metadata-object.txt` with user metadata `project=alpha` and `owner=ops`, sets tags `env=test&project=alpha`, then manually requests the list-type=2 endpoint with `metadata=true` and a URL-encoded prefix matching the object key. It asserts HTTP 200, reads the XML text body, logs it, and performs string containment checks for the listing root, a `Contents` entry, metadata extension nodes, tag extension text, and internal shard fields.

State and persistence behavior: Persistent state is the uploaded object body plus associated user metadata and tags. The test checks that metadata keys are returned in stripped form, meaning response XML uses `<project>` instead of an `x-amz-meta-project` style key. It also expects internal fields `<K>1</K>` and `<M>0</M>`, tying the response to RustFS's internal object layout metadata for this test environment.

Dependencies and integration points: This file bypasses the AWS SDK list operation because the metadata extension is query-parameter-specific and needs raw signed HTTP. It integrates request signing, host header handling, RustFS authentication credentials from the environment, HTTP response handling, S3-compatible object creation, XML serialization, tag encoding, and the object metadata lookup path behind listing.

Risks: XML validation is string-based rather than parsed, so it is sensitive to tag spelling and escaping but not to structural ordering. The expected internal `<K>` and `<M>` values may be environment-specific and could require updates if erasure or storage layout defaults change. Because metadata tag names are used directly as XML element names, invalid XML-name metadata keys would need separate coverage. The test does not explicitly stop the server.

Test signals: Signals are status `200 OK`, response containing `<ListBucketResult`, `<Contents>`, `<UserMetadata>`, `<project>alpha</project>`, `<owner>ops</owner>`, escaped `<UserTags>env=test&amp;project=alpha</UserTags>`, `<Internal>`, `<K>1</K>`, and `<M>0</M>`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/list_objects_v2_metadata_extension_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/list_objects_v2_pagination_test.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/list_objects_v2_pagination_test.rs

Purpose: Broad end-to-end regression suite for `ListObjectsV2` pagination semantics in RustFS. It covers issue #1596 around `IsTruncated` and `NextContinuationToken`, issue #2775 around repeated-prefix continuation forwarding, max-keys boundary cases, S3's 1000-key cap, delimiter/common-prefix pagination, and false truncation when many raw keys collapse into fewer visible results.

Important APIs/types/functions: The file uses `RustFSTestEnvironment`, `init_logging`, AWS SDK S3 `Client`, `ByteStream`, `HashSet`, `serial_test::serial`, and `tracing::info`. Helpers include `create_s3_client` and `create_bucket`, which creates a bucket and tolerates already-existing/owned errors. Core SDK calls are `put_object` and `list_objects_v2` with combinations of `prefix`, `delimiter`, `max_keys`, and `continuation_token`.

Control flow: Each test starts a fresh RustFS server and bucket, creates deterministic object keys, issues one or more `list_objects_v2` requests, and asserts page content and pagination flags. The repeated-prefix test uses `max_keys=2`, walks pages under `engineering/`, verifies strictly increasing lexicographic order, requires a continuation token whenever truncated, and checks exact expected keys with noise keys excluded. The basic pagination tests cover all objects fitting within `max_keys`, multi-page listing with continuation token reuse, exact object-count equality, empty buckets, `max_keys=0`, and `max_keys` above the service limit. The delimiter tests create directory-shaped key sets and verify visible result counting across `Contents` and `CommonPrefixes`, including large raw populations that collapse into few prefixes.

State and persistence behavior: The suite persists object keys and bodies in temporary buckets and observes only listing-derived state. Runtime pagination state is held in `continuation_token`, `last_key`, collected key vectors, page counters, and `HashSet` coverage checks. For service-limit tests, the expected state includes server-side capping of `max_keys` to 1000 and correct continuation to retrieve the remaining keys.

Dependencies and integration points: These tests stress the ListObjectsV2 implementation's storage iterator, prefix filtering, lexicographic ordering, delimiter/common-prefix rollup, response counters (`KeyCount`, `MaxKeys`), truncation calculation, continuation token generation/consumption, and SDK response mapping. The repeated-prefix test starts RustFS with `RUSTFS_CONSOLE_ENABLE=false`, showing integration with server environment configuration in addition to S3 behavior.

Risks: The file creates large fixtures in several tests, including 1002, 1000, 2000, and 1200 objects, so it can be slower and more storage-intensive than narrow e2e tests. Assertions assume deterministic lexicographic ordering and exact response-key order. Safety limits guard against infinite pagination loops but would fail rather than diagnose token contents. The delimiter coverage checks reason about objects covered by returned prefixes, not by expanding a live server-side listing for each prefix.

Test signals: Key signals include `IsTruncated=false` and no `NextContinuationToken` when all visible results fit; `IsTruncated=true` and a present V2 `NextContinuationToken` when more visible results remain; exact total collection of 10 paginated objects; `max_keys=1001` or 2000 being capped to response `MaxKeys=1000`; `max_keys=0` returning no objects and no token; repeated-prefix pages returning exactly seven expected keys in order without duplicates; delimiter listings avoiding false truncation when collapsed visible results fit; and delimiter small-page pagination covering all expected raw keys through returned prefixes.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/list_objects_v2_pagination_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/mc_mirror_small_bucket_test.rs -->
# sources/object-store/rustfs/crates/e2e_test/src/mc_mirror_small_bucket_test.rs

Purpose: End-to-end regression test for issue #3107, validating that MinIO Client `mc mirror` can mirror a modest RustFS bucket without hanging or timing out during list/compare behavior. It exercises RustFS from an external CLI client rather than only through the AWS SDK.

Important APIs/types/functions: The file imports `DEFAULT_ACCESS_KEY`, `DEFAULT_SECRET_KEY`, and `RustFSTestEnvironment`, plus `tokio::fs`, `tokio::time::timeout`, `std::process::Command`, `walkdir::WalkDir`, `uuid::Uuid`, and `serial_test::serial`. Constants are `BUCKET = "ddd"` and `OBJECT_COUNT = 484`. Helpers are `create_issue_3107_fixture`, `mc_available`, `run_mc`, and `count_files`. `TestResult` is the common boxed error result type.

Control flow: The fixture helper writes 484 files below `ddd/requirements/file-XXXX.txt` and three extra marker files under sibling directories `aaa`, `ccc`, and `ccc-package`. The test initializes logging, skips cleanly if `mc --version` is unavailable, starts RustFS, creates bucket `ddd`, creates a unique `mc` alias pointed at the test server, creates fixture and backup directories under the environment temp directory, mirrors the local fixture into the bucket, then mirrors the bucket back to a backup path inside a 20-second timeout using `spawn_blocking` for the CLI call. It counts files in the backup and removes the alias before returning.

State and persistence behavior: Local filesystem state is created under `env.temp_dir` for the source fixture and mirrored backup. Remote RustFS state is populated by `mc mirror --overwrite` into bucket `ddd`; because the source root contains a `ddd` directory plus three sibling directories, the expected remote/backup file count is `OBJECT_COUNT + 3`. The `mc` alias is global client configuration state, so it is given a UUID suffix and explicitly removed at the end.

Dependencies and integration points: This test depends on the external `mc` binary being installed and available on `PATH`. It integrates RustFS bucket creation with MinIO Client alias management, upload mirror, download mirror, object listing/comparison, local directory walking, blocking process execution inside async Tokio tests, and serial server lifecycle. It is a compatibility test for real-world client behavior rather than a unit-level API test.

Risks: The test is skipped when `mc` is missing, so CI environments without MinIO Client will not exercise the regression. `run_mc` uses blocking process execution and captures full stdout/stderr on failure; the download path is wrapped in a 20-second timeout, but the upload mirror is not. If a failure occurs before alias removal, the alias can be left in user/global `mc` config. The fixed bucket name and external CLI config make `#[serial]` important.

Test signals: Strong signals are successful `mc alias set`, successful upload mirror, successful download mirror completing within 20 seconds, and `count_files(backup/ddd-backup) == 487`. A missing `mc` binary is treated as a skip signal, not a failure.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/mc_mirror_small_bucket_test.rs -->
