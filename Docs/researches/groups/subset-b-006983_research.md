# Research: subset-b-006983

This grouped report covers RGW admin utilities and core RGW modules in `sources/distributed-fs/ceph/src/rgw`. Each section preserves the source path and is bounded by reconciliation markers for deterministic per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/radosgw-admin/sync_checkpoint.cc -->
# sources/distributed-fs/ceph/src/rgw/radosgw-admin/sync_checkpoint.cc

## Purpose
Implements the `radosgw-admin` bucket sync checkpoint operation. It waits until local bucket sync has caught up with one or more remote source bucket pipes by comparing full-sync state, incremental generation, and per-shard bilog markers.

## Important APIs, Types, and Functions
- `rgw_bucket_sync_checkpoint(...)` is the exported entry point used by admin command handling. It accepts the RADOS store, bucket sync policy, destination bucket info, optional source zone/bucket filters, retry delay, and absolute timeout.
- `bucket_source_sync_checkpoint(...)` handles one source pipe: it polls full sync status, waits for incremental mode, waits for `latest_gen`, then checks per-shard incremental markers.
- `source_bilog_info(...)` resolves the zone connection for the source zone and calls `rgw_read_remote_bilog_info()`.
- Helpers format and compare `BucketIndexShardsManager` values against `std::vector<rgw_bucket_shard_sync_info>`.

## Control Flow
The entry point scans `policy.get_all_sources()`, applies optional source filters, and builds a list of source entries. For each accepted source it spawns two Boost.Asio coroutines on a local `io_context`: one fetches remote bilog marker info and `latest_gen`, the other reads source bucket instance info. After `ioctx.run()`, it checkpoints each source sequentially. The per-source wait loop first tolerates missing full-sync status (`-ENOENT`) while sync is starting, then waits for `BucketSyncState::Incremental`, then for `full_status.incremental_gen >= latest_gen`, then for all local incremental shard markers to reach or pass remote markers.

## State and Persistence
The file does not write durable state directly. It reads durable sync status objects through `rgw_read_bucket_full_sync_status()` and `rgw_read_bucket_inc_sync_status()`, and reads remote bilog state through zone services. The output is process-local progress logging plus admin stdout/stderr. Timeout and retry state are held in local variables.

## Dependencies and Integration Points
It depends on RGW RADOS SAL (`rgw::sal::RadosStore`), bucket sync policy and status helpers, zone connection maps, cls RGW bilog APIs, and Boost.Asio stackful coroutines. It integrates with `radosgw-admin` via `sync_checkpoint.h`.

## Risks and Edge Cases
The marker comparison is lexicographic and shard-order dependent, so malformed or mismatched shard marker sets can give misleading progress. Source fetches throw `std::system_error` from coroutines and are collapsed into negative errno returns. A bucket whose remote markers are all empty is considered caught up without reading incremental status. The function can block until timeout and sleeps on the calling thread during polling.

## Test Signals
Useful tests include mocked full-sync status transitions from missing to incremental, generation lag and catch-up, empty-source marker handling, source zone/bucket filtering, per-shard marker ordering, timeout behavior, and failures from remote bilog or source bucket info reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/radosgw-admin/sync_checkpoint.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/radosgw-admin/sync_checkpoint.h -->
# sources/distributed-fs/ceph/src/rgw/radosgw-admin/sync_checkpoint.h

## Purpose
Declares the admin-facing bucket sync checkpoint API for waiting on bucket replication catch-up.

## Important APIs, Types, and Functions
- Forward declares `DoutPrefixProvider`, `rgw::sal::RadosStore`, `RGWBucketInfo`, and `RGWBucketSyncPolicyHandler`.
- Exposes `rgw_bucket_sync_checkpoint(...)` with source-zone/source-bucket filters, retry delay, and timeout deadline.

## Control Flow
This header has no control flow. It establishes the contract consumed by `radosgw-admin` command code and implemented in `sync_checkpoint.cc`.

## State and Persistence
No state is stored here. The signature makes persistence dependencies explicit through the RADOS store, bucket info, and sync policy inputs.

## Dependencies and Integration Points
Includes `common/ceph_time.h` for deadline/delay types and `rgw_basic_types.h` for `rgw_zone_id`/`rgw_bucket`. It is a narrow integration point between admin commands and bucket sync internals.

## Risks and Edge Cases
The API exposes an absolute timeout rather than a duration; callers must compute it consistently with the monotonic coarse clock. Optional filters must be interpreted by the implementation without silently skipping all intended sources.

## Test Signals
Compile/link coverage should confirm only the minimal forward declarations are needed. Admin tests should verify caller-provided filters and timeout values reach the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/radosgw-admin/sync_checkpoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw-gap-list -->
# sources/distributed-fs/ceph/src/rgw/rgw-gap-list

## Purpose
Bash diagnostic script that finds possible RGW bucket data gaps by comparing objects known to bucket indexes (`radosgw-admin bucket radoslist`) against actual objects present in one or more data pools (`rados ls`). It is explicitly experimental and designed to produce candidates requiring verification.

## Important APIs, Types, and Functions
- `prompt_pool()` lists pools and asks the operator which data pools to scan.
- `radosgw_radoslist()` runs `radosgw-admin bucket radoslist --rgw-obj-fs="$fs"`, sorts uniquely by RADOS object id, and writes intermediate files.
- `rados_ls()` scans supplied pools with `rados ls`, sorts unique object ids, and records failures through flag files.
- Embedded awk script performs a single-pass sorted comparison and emits unique `Bucket: ... Object: ...` candidate lines.

## Control Flow
The script parses `-m`, `-p`, and `-t`, validates pools with `rados lspools`, runs the RADOS and RGW listings either sequentially or in parallel, checks non-empty intermediates, writes an awk comparator to a temp file, runs it over sorted data, sorts the candidate output, and reports counts and file locations.

## State and Persistence
It writes timestamped intermediates and errors under the current working directory: `rados-*.intermediate`, `radosgw-admin-*.intermediate`, `*.error`, and `gap-list-*.gap`. Temporary files, flag files, and the generated awk script live under `temp_prefix`.

## Dependencies and Integration Points
Requires `bash`, `rados`, `radosgw-admin`, `sort`, `awk`, `grep`, `wc`, and Ceph environment variables such as `CEPH_ARGS`. It relies on `LC_ALL=C` for reproducible sorting and on `--rgw-obj-fs` using byte `0xFE` as a field separator.

## Risks and Edge Cases
The tool is prone to false positives if objects are created or deleted during listing, especially in multithread mode. It assumes the field separator cannot appear in normal output. It skips RADOS names containing NUL. Failures terminate via `TERM` to the top-level process, which can be brittle with background jobs.

## Test Signals
Tests can use synthetic sorted inputs for the embedded awk comparator, missing pool validation, multithread flag-file handling, empty intermediate rejection, duplicate bucket/object suppression, and output stability under `LC_ALL=C`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw-gap-list -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw-gap-list-comparator -->
# sources/distributed-fs/ceph/src/rgw/rgw-gap-list-comparator

## Purpose
Awk helper that intersects two sorted `rgw-gap-list` result files. It is intended to reduce false positives by retaining only candidate gap lines that appear in two independent runs.

## Important APIs, Types, and Functions
- Accepts `-v filetwo=<second sorted file>` and `-v matchout=<output file>`.
- `advance_f2()` reads the next line from the second file.
- `test_lines()` compares the current primary input line with `f2line`, emits matches, and guides advancement.
- `status_out()` reports scan progress to stderr every 100k lines.

## Control Flow
On `BEGIN`, the script validates required variables, initializes counters, opens the second file, and prints a progress header. For each line of the first file, it advances through `filetwo` until the second line is at or beyond the first, then writes exact string matches to `matchout`. It exits early when the second file reaches EOF.

## State and Persistence
Only local awk counters and the current second-file line are kept in memory. Durable output is appended to `matchout`; callers are advised to remove old output before running.

## Dependencies and Integration Points
Designed to consume sorted text outputs from `rgw-gap-list`. It depends on awk string comparison using the same collation as the sorted files, so operators must use `LC_ALL=C` consistently.

## Risks and Edge Cases
Input files must be sorted identically or matches may be missed. Because output is append-only, stale results remain if `matchout` is not removed first. It does exact line matching, so harmless formatting changes in upstream output prevent correlation.

## Test Signals
Use fixture pairs with exact matches, non-overlapping data, duplicate lines, unsorted inputs, and EOF on either file. Verify progress counters do not affect stdout/stderr contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw-gap-list-comparator -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw-orphan-list -->
# sources/distributed-fs/ceph/src/rgw/rgw-orphan-list

## Purpose
Experimental Bash diagnostic script that finds possible orphaned RGW data objects by comparing `rados ls --all` output from data pools against `radosgw-admin bucket radoslist`. It warns that indexless buckets appear entirely orphaned.

## Important APIs, Types, and Functions
- `prompt_pool()` interactively selects one or more RGW data pools.
- `rados_ls()` scans pools with `rados ls --all`, separates namespace/locator entries into an issues file, extracts plain object ids, and sorts them.
- `radosgw_radoslist()` generates and sorts the RGW-admin view.
- Final comparison uses `ceph-diff-sorted "$rados_out" "$rgwadmin_out" | grep "^<"` to capture objects present in RADOS but absent from RGW-admin listing.

## Control Flow
The script validates arguments and pools, produces both sorted listings, warns on empty intermediate files, computes the delta, calculates candidate count and percentage, and prints locations of outputs and issue files.

## State and Persistence
Timestamped intermediates, error files, issue files, and `orphan-list-*.out` are written in the current directory. Temporary sorting files are created under `/tmp` or an optional temp directory.

## Dependencies and Integration Points
Requires Ceph client tools, `radosgw-admin`, `ceph-diff-sorted`, standard Unix text tools, and `CEPH_CONF` when configuration is not in the default path. It relies on the ceph-radosgw package for `ceph-diff-tool`/`ceph-diff-sorted`.

## Risks and Edge Cases
Indexless buckets invalidate results. Namespaces or locators are excluded from normal orphan detection and require manual review. Live cluster mutations can produce false positives. Empty inputs only warn rather than always fail, so operator judgment is required.

## Test Signals
Synthetic fixture tests should cover namespace/locator filtering, delta computation, empty-input warning behavior, missing pool detection, and `ceph-diff-sorted` error propagation through `PIPESTATUS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw-orphan-list -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw-restore-bucket-index -->
# sources/distributed-fs/ceph/src/rgw/rgw-restore-bucket-index

## Purpose
Interactive experimental recovery script that reconstructs lost bucket index entries by scanning a bucket data pool for head objects matching a bucket marker, deriving RGW object names, and invoking `radosgw-admin object reindex`.

## Important APIs, Types, and Functions
- `get_pool()` infers the data pool from bucket instance explicit placement or zone placement pools.
- `handle_versioned()` handles versioned buckets by reading OLH xattrs, decoding `RGWOLHInfo`, sorting object versions by mtime, and building an objects file with version ids.
- `test_temp_space()` aborts when the temp filesystem or inode space is exhausted.
- Final action is `radosgw-admin object reindex --bucket=... --objects-file=... --yes-i-really-mean-it`.

## Control Flow
The script validates required tools (`radosgw-admin`, `ceph-dencoder`, `jq`) and decoder support, parses bucket/realm/zone/pool/temp/proceed/debug options, fetches bucket entry and instance metadata, determines shard count and data pool, scans either live `rados ls` output or a provided listing for names with the bucket marker, derives object names, optionally runs versioned-bucket handling, prompts the operator unless `-y` was supplied, and reindexes the objects.

## State and Persistence
Temporary metadata, marker listing, object-list, versioned object-list, zone info, decoded OLH info, and optional debug log are written under the temp directory. Unless debug disables cleanup, temp files are removed at completion or termination. Durable cluster changes happen only through `radosgw-admin object reindex`.

## Dependencies and Integration Points
Integrates with RGW metadata (`bucket:` and `bucket.instance:`), zone placement config, RADOS object xattrs, `ceph-dencoder` for `RGWOLHInfo`, and the admin object reindex path. It supports multisite selectors via realm, zonegroup, and zone arguments.

## Risks and Edge Cases
It is destructive/recovery-oriented and can restore wrong or stale entries if marker parsing is wrong or the input `rados ls` file is stale. Versioned bucket logic depends on OLH metadata and `stat2` mtimes. Several shell expansions are unquoted around object names, pool names, and temp paths, so unusual names may break processing. Operator review is the main guard unless `-y` is used.

## Test Signals
Tests should use fixture metadata JSON and listing files for non-versioned and versioned buckets, pool inference cases, missing tool/decoder checks, temp-space aborts, empty object list handling, prompt bypass with `-y`, and correct object-file format for `object reindex`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw-restore-bucket-index -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_account.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_account.cc

## Purpose
Implements account admin operations for RGW: id generation/validation, account creation/modification/removal, account info/stat retrieval, and account user listing.

## Important APIs, Types, and Functions
- `generate_id()` creates `RGW` plus 17 numeric digits.
- `validate_id()` and `validate_name()` enforce account identifier and account name constraints.
- `root_arn()` constructs an IAM root ARN for an account id.
- `create()`, `modify()`, `remove()`, `info()`, `stats()`, and `list_users()` implement the operations declared in `rgw_account.h`.

## Control Flow
Create validates name/id, applies quota defaults from config, creates an `RGWAccountInfo`, generates a write version, and calls `driver->store_account()` in exclusive mode. Modify loads by id/name/email, rejects tenant changes, applies name/email/limit/quota updates, and stores non-exclusively with the old info for index updates. Remove loads the account, then lists users, buckets, roles, groups, OIDC providers, and topics in chunks; without `purge_data`, any child resource aborts deletion, while with purge it removes each child before deleting the account. Info and stats load the account and format JSON; stats can sync or reset account stats before loading them. `list_users()` pages through account users and optionally filters to root users.

## State and Persistence
All durable work is delegated to `rgw::sal::Driver`: account records and indexes, users, buckets, roles, groups, OIDC providers, topics, quotas, and stats. `RGWObjVersionTracker` is used for account/group/topic persistence paths. Output is streamed through `RGWFormatterFlusher`.

## Dependencies and Integration Points
Depends on SAL driver account APIs, quota helpers, ARN support, role/OIDC/topic/bucket/user abstractions, and Ceph UTF-8/random utilities. It is used by RGW admin REST/CLI account paths.

## Risks and Edge Cases
`remove()` can be highly destructive with `purge_data=true`, cascading through users, buckets, roles, groups, OIDC providers, and topics. Partial failures can leave some children removed and the account still present. `list_users()` subtracts all returned users from `remaining`, including entries skipped by `root_only`, so a root-only query with max entries may return fewer visible users than requested. Name validation forbids `$` and `:` but not all possible operationally confusing characters.

## Test Signals
Tests should cover id/name validation, create default quota application, duplicate create behavior, modify by each lookup key, tenant immutability, quota scope updates, non-purge deletion blockers, purge cascade ordering/failure, stats sync/reset, and paginated user listing with `root_only`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_account.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_account.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_account.h

## Purpose
Declares RGW account admin helper functions and the `AdminOpState` parameter bundle used by account command handlers.

## Important APIs, Types, and Functions
- `AdminOpState` holds lookup keys, tenant/name/email updates, account limits, quota updates, and `purge_data`.
- Declares lifecycle operations: `create`, `modify`, `remove`, `info`, `stats`, and `list_users`.
- Declares validation helpers and `root_arn()`.

## Control Flow
No implementation flow is present. The header defines operation contracts that accept `DoutPrefixProvider`, SAL driver, formatter, yield context, and error-message outputs.

## State and Persistence
The header itself stores no state. `AdminOpState` is transient command state that drives persistent SAL operations in the implementation.

## Dependencies and Integration Points
Uses `std::optional` for optional numeric/bool updates, forwards the SAL driver and ARN type, and integrates with Ceph formatter/yield conventions.

## Risks and Edge Cases
Because many fields are optional, callers must distinguish unspecified values from explicit zero/false values. `purge_data` is a high-risk switch that changes `remove()` from validation-only to destructive cascade.

## Test Signals
Compile/API tests should catch signature changes. Admin command tests should verify correct `AdminOpState` population for every CLI/REST option, especially false quota-enabled values and purge behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_account.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_acl.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_acl.cc

## Purpose
Implements RGW ACL core behavior: grant registration, permission lookup, public detection, owner emptiness, JSON dumping, equality, and test-instance generation.

## Important APIs, Types, and Functions
- `RGWAccessControlList::add_grant()` inserts grants and updates user/group/referer lookup structures.
- `get_perm()`, `get_group_perm()`, and `get_referer_perm()` compute permissions for identities, public groups, and Swift referer grants.
- `RGWAccessControlPolicy::get_perm()` and `verify_permission()` implement overall permission checks.
- `is_public()` detects grants to AllUsers or AuthenticatedUsers.

## Control Flow
Grant registration maps canonical users and emails into `acl_user_map`, groups into `acl_group_map`, and referers into `referer_list`. Policy permission checks begin with identity ACL-spec permissions, add owner READ_ACP/WRITE_ACP, optionally add public/authenticated group grants, and finally apply referer ACL transformations when a referer string exists and the requested mask is not yet satisfied. `verify_permission()` expands Swift object permission bits into S3-style read/write ACP semantics before comparing against the requested permission and user permission mask.

## State and Persistence
The object state is in encoded ACL/policy types: user/group maps, referer list, grant map, and owner. This file does not persist directly; persistence occurs when containing bucket/object/user metadata encodes these classes.

## Dependencies and Integration Points
Integrates with `rgw::auth::Identity`, ACL types, S3 URI conversion for backward compatibility, formatter JSON encoding, and Swift referer compatibility through `RGW_REFERER_WILDCARD`.

## Risks and Edge Cases
Referer grants are order-sensitive because the last matching referer rewrites `referer_perm`. Email grants are registered in `acl_user_map` by address, which depends on identity ACL-spec behavior. `ACLGrant::generate_test_instances()` appears to set `g1` instead of `g2` for the group sample, which weakens generated test coverage. Public ACL checks intentionally ignore invalid/none values but not all semantic policy combinations.

## Test Signals
Tests should cover owner implicit ACP rights, public ACL ignoring, authenticated versus anonymous identities, referer positive/negative and wildcard behavior, Swift READ_OBJS/WRITE_OBJS conversion, serialization round trips, and generated-test-instance coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_acl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_acl.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_acl.h

## Purpose
Defines the core RGW ACL data model: grant variants, referer grants, access control lists, owners, and access control policies.

## Important APIs, Types, and Functions
- `ACLGrant` wraps canonical user, email, group, unknown, or referer grantees plus `ACLPermission`.
- `ACLReferer` parses HTTP referer hosts and matches wildcard/domain rules.
- `RGWAccessControlList` stores grant maps and accelerated permission maps.
- `ACLOwner` supports user or account owners through `rgw_owner`.
- `RGWAccessControlPolicy` combines owner and ACL and exposes permission verification.

## Control Flow
Most methods are inline encode/decode helpers and simple builders. Decode paths preserve legacy compatibility, reconstructing grantee variants from encoded type and fields. `create_default()` grants full control to the owner and sets owner identity/display name. `ACLReferer::is_match()` extracts host from a URL, supports `*`, exact host, and suffix matches for leading-dot specs.

## State and Persistence
These are serialized metadata types. Encoders use versioned Ceph encoding macros; the numeric values of grantee and group enums are encoded and must not change. ACL maps and referer lists are stored with the policy when bucket/object metadata persists ACLs.

## Dependencies and Integration Points
Depends on `rgw_basic_types.h`, `include/types.h`, Boost optional/string predicates, and `rgw::auth::Identity` in method contracts. S3 and Swift adapters construct these shared types.

## Risks and Edge Cases
Variant index order is tied to `ACLGranteeTypeEnum`; reordering the variant or enum breaks decoding semantics. Referer host parsing rejects malformed URLs but has minimal normalization. `remove_canon_user_grant()` erases grants by owner string and does not affect group/referer grants.

## Test Signals
Round-trip encode/decode tests across legacy versions, referer URL parsing, default policy creation, owner account/user variants, and grant-map registration consistency are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_acl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_acl_s3.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_acl_s3.cc

## Purpose
Implements S3 ACL XML parsing/serialization, canned ACL construction, and `x-amz-grant-*` header parsing for RGW's shared ACL model.

## Important APIs, Types, and Functions
- XML object classes parse `AccessControlPolicy`, `Owner`, `Grant`, `Grantee`, `Permission`, `ID`, `URI`, and `EmailAddress`.
- `read_owner_display_name()` resolves user or account owners through SAL.
- `resolve_grant()` validates canonical user ids, email users, and group URIs.
- Namespace exports: `acl_uri_to_group()`, `acl_group_to_uri()`, `parse_policy()`, `write_policy_xml()`, `create_canned_acl()`, and `create_policy_from_headers()`.

## Control Flow
S3 XML parsing builds an XML object tree, validates required owner and ACL elements, resolves the owner against SAL, then converts each grant into a canonical/group ACLGrant. Header parsing walks known grant headers, splits comma-separated grantees, parses key/value forms (`emailAddress=`, `id=`, `uri=`), resolves external identifiers, and adds grants. Canned ACL creation always grants object owner full control, optionally grants public/authenticated users or bucket owner, and handles ObjectOwnership overrides.

## State and Persistence
The file constructs in-memory `RGWAccessControlPolicy` objects. Persistence happens later when bucket/object metadata stores the policy. Reads against SAL validate and enrich grantees with display names, but this file does not write metadata directly.

## Dependencies and Integration Points
Depends on RGW XML parser classes, SAL user/account lookup, S3 error codes, `RGWEnv` request headers, object ownership settings, and the shared ACL types.

## Risks and Edge Cases
Email grantees require lookup and may return S3-specific unresolved-email errors. `BucketOwnerEnforced` rejects most ACLs and rewrites owner to the bucket owner. XML serialization omits non-S3-compatible permission bits. Header splitting is comma-based and assumes grantee value parsing handles quoted values correctly.

## Test Signals
Tests should cover all canned ACLs, ObjectOwnership modes, XML owner/grant validation, email/canonical/group grant resolution failures, header parsing for each permission, XML round trips, and non-S3 permission filtering in output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_acl_s3.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_acl_s3.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_acl_s3.h

## Purpose
Declares the S3 ACL adapter API used to translate S3 XML, canned ACLs, and request headers into RGW access control policies.

## Important APIs, Types, and Functions
- `acl_uri_to_group()` and `acl_group_to_uri()` map AWS group URIs to RGW group enums.
- `parse_policy()` parses an S3 `AccessControlPolicy` XML document.
- `write_policy_xml()` serializes a policy as S3 XML.
- `create_canned_acl()` and `create_policy_from_headers()` build policies from request-level ACL inputs.

## Control Flow
The header only declares contracts. The signatures show that parsing and header construction may yield on SAL lookups and may return detailed error messages.

## State and Persistence
No state is stored here. Output state is a caller-owned `RGWAccessControlPolicy`.

## Dependencies and Integration Points
Includes async yield support, RGW XML, shared ACL types, object ownership, SAL forward declarations, and `RGWEnv`.

## Risks and Edge Cases
Callers must pass the correct bucket owner and object ownership mode or S3 ACL semantics can be wrong. `parse_policy()` takes `std::string_view`; callers must keep the backing document alive during parsing.

## Test Signals
API tests should verify all public functions remain available to S3 request handlers and preserve expected error propagation for validation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_acl_s3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_acl_swift.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_acl_swift.cc

## Purpose
Implements Swift container and account ACL conversion to/from RGW's shared ACL model, including Swift referrer ACL syntax and account ACL JSON.

## Important APIs, Types, and Functions
- `create_container_policy()` parses `X-Container-Read` and `X-Container-Write` lists.
- `merge_policy()` preserves old read/write grants when only one side is updated.
- `format_container_acls()` renders policy grants back into Swift header strings.
- `create_account_policy()` parses `X-Account-Access-Control` JSON arrays for admin/read-write/read-only.
- `format_account_acl()` serializes account grants back to Swift account ACL JSON.

## Control Flow
Container policy creation starts from a default owner-full-control policy, splits read/write lists on spaces and commas, parses each grant as a user or `.r` referrer spec, and updates an `rw_mask` to record which ACL sides were supplied. Referrer grants may be positive or negative and are rejected for write ACLs. Account policy creation parses JSON arrays and adds grants with full-control, read/write, or read-only permissions. Formatting walks the grant map and partitions grants by Swift semantics.

## State and Persistence
This file only constructs and formats `RGWAccessControlPolicy`. Durable state is stored by the calling bucket/account metadata paths. It does load user records through SAL to set canonical ids and display names.

## Dependencies and Integration Points
Depends on Swift header semantics, RGW JSON parser, shared ACL types, SAL user loading, and public group compatibility (`.r:*` maps to AllUsers).

## Risks and Edge Cases
`user_to_grant()` silently creates a canonical grant even when user loading fails, using the requested id with an empty display name. Negative referer grants depend on order-preserving `referer_list` handling in core ACL checks. Formatting cannot represent every possible RGW ACL and skips unsupported entries. `uid_is_public()` indexes the first two chars without checking length, so malformed empty/short strings could be risky if passed.

## Test Signals
Tests should cover `.r:*`, exact/suffix/negative referers, write-referrer rejection, partial read/write updates via `merge_policy()`, account ACL JSON categories, missing users, and format/parse round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_acl_swift.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_acl_swift.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_acl_swift.h

## Purpose
Declares Swift ACL adapter functions for container headers and account ACL JSON.

## Important APIs, Types, and Functions
- `create_container_policy()` builds policy from Swift read/write header lists.
- `merge_policy()` preserves unchanged read/write sides.
- `format_container_acls()` renders read/write headers.
- `create_account_policy()` and `format_account_acl()` handle `X-Account-Access-Control`.

## Control Flow
No implementation logic is present. The signatures expose ownership, SAL driver, read/write masks, and optional serialized account ACL output.

## State and Persistence
No state is stored. Callers own the `RGWAccessControlPolicy` output and persist it elsewhere.

## Dependencies and Integration Points
Forward-declares ACL and formatter types, includes SAL forward declarations and user owner types, and sits between Swift request handlers and core ACL storage.

## Risks and Edge Cases
The `rw_mask` contract is important: callers must pass it through `merge_policy()` when only one header side is updated. Account ACL formatting can return `std::nullopt`, which callers must treat as no header rather than an empty JSON object.

## Test Signals
Header-level Swift tests should verify declarations match implementation and that request handlers correctly call merge/format helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_acl_swift.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_acl_types.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_acl_types.h

## Purpose
Defines fundamental serialized RGW ACL-adjacent types and constants shared beyond the RGW process context: permission bits, access keys, subusers, user caps, and ACL grantee/group/permission wrappers.

## Important APIs, Types, and Functions
- Permission constants such as `RGW_PERM_READ`, `RGW_PERM_WRITE`, `RGW_PERM_FULL_CONTROL`, Swift object bits, and `RGW_PERM_INVALID`.
- `RGWAccessKey` and `RGWSubUser` serialized user credential/subuser records.
- `RGWUserCaps` parses, stores, checks, encodes, and dumps admin capability maps.
- `ACLGranteeTypeEnum`, `ACLGroupTypeEnum`, `ACLPermission`, and `ACLGranteeType` provide encoded ACL primitives.

## Control Flow
Inline encode/decode methods use Ceph versioned encoding macros with legacy compatibility. `RGWUserCaps` exposes parsing and checking APIs whose bodies are elsewhere.

## State and Persistence
These types are durable serialized metadata. Numeric enum values and encoded struct versions are persistent wire/storage contracts and must remain stable. `RGWAccessKey` includes active flag and creation date in newer versions while preserving older decodes.

## Dependencies and Integration Points
The header intentionally avoids RADOSGW/OSD-only includes. It depends on common Ceph types and Formatter. It is included by `rgw_basic_types.h` and core ACL/user metadata code.

## Risks and Edge Cases
Changing enum order or permission bit meanings breaks existing metadata. `RGW_PERM_INVALID` is outside normal low-bit permissions and must not be confused with full control. Capability parsing must preserve backward-compatible string forms.

## Test Signals
Encoding compatibility tests, generated-test-instance coverage, cap parsing/removal, active/inactive key JSON decoding, and permission mask behavior are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_acl_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_aio.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_aio.cc

## Purpose
Implements wrappers that turn librados read/write operations and D3N cache reads into `Aio::OpFunc` callbacks consumable by RGW AIO throttles.

## Important APIs, Types, and Functions
- `Aio::librados_op()` overloads for `ObjectReadOperation` and `ObjectWriteOperation`.
- `Aio::d3n_cache_op()` wraps a D3N L1 cache async read.
- Internal `state` stores AIO completion state in `AioResult::user_data`.
- `cb()` transfers librados completion return values back to the owning throttle.

## Control Flow
For non-yield librados operations, the wrapper creates a librados completion with `AioResult` as callback arg, places state in `user_data`, submits `ctx.aio_operate()`, and either waits for `cb()` or immediately returns failed submissions to the throttle. For yield-based operations, it uses `librados::async_operate()` bound to the coroutine strand so the handler can call `Aio::put()` without locking. D3N cache operations assert a yield context and delegate to `D3nL1CacheRequest`.

## State and Persistence
No durable state is owned here. Runtime state includes completion objects, result buffers, tracing context pointers, and cache request objects. RADOS operations mutate or read persistent objects according to the caller-supplied operation.

## Dependencies and Integration Points
Depends on librados C++ and asio wrappers, D3N cache request/driver headers, RGW tracing, and `Aio` throttle implementations.

## Risks and Edge Cases
The placement-new state must fit in `AioResult::user_data`; the static assert guards this. If `aio_operate()` fails synchronously, cleanup must mirror callback cleanup. Yield operations depend on all public throttle calls occurring on the same strand. D3N cache reads require async/yield mode.

## Test Signals
Tests should cover synchronous submit failure, read/write completion result propagation, data buffer movement for reads, trace context pass-through for writes, yield and non-yield paths, and D3N yield assertion/put behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_aio.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_aio.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_aio.h

## Purpose
Defines RGW's abstract asynchronous IO interface, result types, intrusive owning result list, error helper, and factory functions for librados/D3N operation callbacks.

## Important APIs, Types, and Functions
- `AioResult` carries object id, request id, read data, result code, and aligned internal user data.
- `AioResultEntry` enables intrusive list ownership.
- `AioResultList` is an owning intrusive list that disposes entries on destruction.
- `Aio` declares `get`, `put`, `poll`, `wait`, and `drain`.
- `check_for_errors()` returns the first negative completion result.

## Control Flow
The interface contract is that callers submit with `get()` and receive completions from previous operations, while async callbacks return entries via `put()`. `poll()`, `wait()`, and `drain()` expose nonblocking, next-completion, and all-completion retrieval.

## State and Persistence
State is per-request runtime state. Durable effects depend on operation callbacks supplied by callers.

## Dependencies and Integration Points
Uses librados forward declarations, RGW raw object types, Ceph yield contexts, Boost intrusive lists, and function2 move-only callbacks. Implemented by throttle classes in `rgw_aio_throttle.*`.

## Risks and Edge Cases
`AioResult` is noncopyable/nonmovable because entries are intrusive and may contain placement state. Callers must drain before destroying implementations. `cost` semantics are implementation-specific and can reject oversized operations.

## Test Signals
Interface-level tests should verify result ownership, disposal on list destruction, first-error detection, id/object association, and correct behavior of concrete throttles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_aio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_aio_throttle.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_aio_throttle.cc

## Purpose
Implements blocking and yielding AIO throttles that limit outstanding operation cost and collect completions for RGW async IO.

## Important APIs, Types, and Functions
- `Throttle::waiter_ready()` interprets the active wait condition.
- `BlockingAioThrottle::{get,put,poll,wait,drain}` use a mutex and condition variable.
- `YieldingAioThrottle::{get,put,poll,wait,drain}` use coroutine completions instead of blocking.
- `YieldingAioThrottle::async_wait()` creates an async completion tied to the yield executor.

## Control Flow
`get()` allocates a pending entry, rejects costs larger than the window with `-EDEADLK`, otherwise increments `pending_size`, waits for availability if needed, queues the pending entry, and invokes the submitted operation. `put()` moves entries from pending to completed, decrements cost, and wakes the waiting thread/coroutine if its condition is met. `wait()` waits for at least one completion; `drain()` waits for no pending entries.

## State and Persistence
Only runtime lists and counters are kept. No durable state is persisted. Completed result lists transfer ownership to callers by moving the intrusive owning list.

## Dependencies and Integration Points
Implements the `Aio` interface from `rgw_aio.h`. Blocking mode uses Ceph mutex/condition_variable; yielding mode uses Boost.Asio yield contexts and Ceph async completions.

## Risks and Edge Cases
All public functions must be called from one thread for blocking or one coroutine strand for yielding. The yielding `get()` sets `waiter=Available` before `async_wait()` but relies on `put()` to reset it. Oversized costs become completed error entries rather than throwing. Destructors assert both pending and completed lists are empty, so callers must drain and consume results.

## Test Signals
Tests should cover window backpressure, oversized cost errors, poll/wait/drain semantics, concurrent callback wakeups, yielding wakeup on the correct executor, and destructor assertions after proper drain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_aio_throttle.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_aio_throttle.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_aio_throttle.h

## Purpose
Declares RGW AIO throttle implementations and the `make_throttle()` factory that selects blocking or coroutine-yielding behavior.

## Important APIs, Types, and Functions
- `Throttle` stores the common window, pending size, pending/completed lists, and waiter state.
- `BlockingAioThrottle` is for synchronous/threaded contexts.
- `YieldingAioThrottle` is for coroutine strand contexts.
- `make_throttle(window_size, optional_yield)` selects `YieldingAioThrottle` when a yield context exists.

## Control Flow
The header documents the call-context constraints and declares the `Aio` overrides. The factory makes async mode transparent to callers.

## State and Persistence
No durable state. Runtime state is owned by throttle instances and must be empty at destruction.

## Dependencies and Integration Points
Includes Ceph mutex, async completion, yield context, and the abstract AIO interface. Used by RGW data paths that submit bounded concurrent RADOS/cache operations.

## Risks and Edge Cases
Choosing the wrong throttle for the execution model can deadlock or race. `window` units are caller-defined, so callers must pass costs consistently.

## Test Signals
Construction tests should verify factory selection, interface substitutability, and lifecycle requirements for both concrete throttles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_aio_throttle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_amqp.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_amqp.cc

## Purpose
Implements RGW AMQP notification publishing with connection reuse, bounded message queueing, optional publisher confirms, SSL support, and a background manager thread.

## Important APIs, Types, and Functions
- Public namespace functions: `init`, `shutdown`, `connect`, `publish`, `publish_with_confirm`, metric getters, and `status_to_string`.
- `connection_id_t` identifies broker host/port/vhost/exchange/SSL.
- `connection_t` owns rabbitmq-c connection state, reply queue, callbacks, credentials, SSL settings, and reconnect timing.
- `new_state()` opens sockets, logs in, opens channels, enables confirms, verifies exchange, and declares/consumes a private reply queue.
- `Manager` owns connections, a lock-free message queue, counters, and the runner thread.

## Control Flow
`init()` creates the singleton manager. `connect()` parses an AMQP URL, reuses or creates a connection entry, and attempts state creation. `publish()` and `publish_with_confirm()` enqueue heap-allocated messages. The background thread consumes queued messages, publishes them to either the normal or confirming channel, records callbacks by delivery tag for confirm mode, scans connections for ACK/NACK/RETURN/CLOSE frames, invokes callbacks, destroys failed connection state, deletes idle connections, and retries failed connections after a short delay.

## State and Persistence
Runtime state includes the singleton manager pointer, connection map, message queue, callback vectors, counters, and rabbitmq-c connection resources. AMQP messages may be published with persistent delivery mode for confirm path, but this file does not persist RGW metadata.

## Dependencies and Integration Points
Depends on rabbitmq-c headers/APIs, OpenSSL, Boost lockfree queue/hash/optional, Ceph logging/time/thread naming, and RGW notification subsystem. It is used by RGW pubsub/notification code to publish events to AMQP endpoints.

## Risks and Edge Cases
The connection-map iteration relies on no rehashing and coarse locking; additions/removals while iterating are delicate. Confirm callbacks are limited by `max_inflight`; overflow invokes an immediate error after the message was already published successfully. Non-confirm publish errors destroy the connection without per-message retry. Reconnect backoff is fixed and short. `mandatory_delivery` is stored in `connection_t::mandatory` but not visibly assigned from the connect argument in the constructor call path, which should be checked. URL parsing uses a mutable copy because rabbitmq-c stores pointers.

## Test Signals
Tests should cover URL parsing and connection id reuse, SSL verify/CA failure codes, exchange/queue/confirm setup failures, queue-full behavior, manager shutdown with queued messages, ACK/NACK/multiple callback handling, connection close/retry, idle deletion, metric counters, and `mandatory_delivery` propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_amqp.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_amqp.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_amqp.h

## Purpose
Declares the RGW AMQP notification publishing API and connection identifier type.

## Important APIs, Types, and Functions
- `reply_callback_t` receives integer publish-confirm status.
- `init()`/`shutdown()` manage the global AMQP manager.
- `connect()` creates or reuses a connection for URL/exchange/SSL settings.
- `publish()` and `publish_with_confirm()` enqueue messages.
- Getter functions expose queue, connection, in-flight, and configured limit metrics.

## Control Flow
No implementation logic is present, but the API establishes an asynchronous model: connect first, then publish by returned `connection_id_t`; confirm callbacks are invoked later by the manager thread.

## State and Persistence
No state is stored in the header. `connection_id_t` is a value key copied from parsed AMQP connection info.

## Dependencies and Integration Points
Uses `CephContext`, `boost::optional`, and rabbitmq-c's `amqp_connection_info` forward declaration. Consumed by RGW notification code.

## Risks and Edge Cases
Callers must handle negative RGW-specific status codes and normal AMQP status codes. The callback can run asynchronously on the manager thread, so callback implementations must be thread-safe and nonblocking.

## Test Signals
API tests should verify lifecycle ordering, status string coverage, metric behavior before/after init, and callback invocation contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_amqp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_appmain.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_appmain.cc

## Purpose
Implements `rgw::AppMain`, the main orchestration object for RGW process initialization and shutdown: frontends, storage, REST APIs, auth, logs, performance counters, HTTP clients, realm reloaders, Lua, dedup, KMS cache, and service-map registration.

## Important APIs, Types, and Functions
- `init_frontends1()` parses frontend config and handles legacy region-to-zonegroup settings.
- `init_storage()` creates config store, loads site, and creates the storage driver with configured background threads.
- `cond_init_apis()` registers S3, Swift, Swift auth, admin, zero, and related REST resources based on `rgw_enable_apis`.
- `init_frontends2()` creates frontend objects, scheduler/rate limiter/auth registry, starts frontends, registers service map, and installs realm watchers/reloaders.
- `shutdown()` tears subsystems down in dependency order.

## Control Flow
Initialization is staged. Frontend config parsing happens early so global config can be finalized. Storage setup loads site configuration and starts driver-managed services. API registration is conditional on HTTP frontend presence and enabled API names. Frontend startup applies default frontend config, instantiates matching frontend classes (`beast`, `loadgen`, `rgw-nfs`, optional Arrow Flight), initializes and runs each, then registers the daemon in the service map. For RADOS-backed drivers, realm watchers can pause/reload frontends, Lua background work, and dedup background work.

## State and Persistence
`AppMain` owns runtime objects: frontend configs/frontends, config store, site, driver environment, REST registry, auth registry, rate limiter, scheduler context, logs, LDAP helper, KMS cache, Lua/dedup backgrounds, realm watcher/reloader, and IO context pool. Persistent effects include service-map registration, ops log sinks, driver-managed background services, and possible Lua package installation.

## Dependencies and Integration Points
This file integrates much of RGW: global config, DriverManager, REST managers, frontends, auth strategies, dmclock scheduler, curl/HTTP/KMIP clients, perf counters, tracepoints, LDAP, ops logging, Lua, dedup, realm notification, and NFS mode.

## Risks and Edge Cases
Initialization order matters: storage and site must exist before REST/auth, frontends cannot be deleted before IO contexts finish, and request handling must stop before storage closes. Some errors are fatal while service-map registration errors are logged and ignored. Swift-at-root conflicts with S3 registration. `rgw_keystone_admin_password` warning highlights plaintext secret risk. Shutdown assumes `env.driver` exists and follows the expected initialization path.

## Test Signals
Integration tests should cover frontend parsing defaults, bad frontend configs, API enable/disable combinations, Swift-at-root conflicts, storage-driver creation failure, service-map registration failure tolerance, realm reload setup, NFS background-thread flags, and shutdown ordering under active frontends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_appmain.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_arn.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_arn.cc

## Purpose
Implements AWS-style ARN parsing, formatting, construction from RGW buckets/objects/IAM resources, wildcard matching, ordering, and ARN resource parsing.

## Important APIs, Types, and Functions
- `to_partition()` and `to_service()` convert parsed strings to enums, with optional wildcard support.
- `ARN::parse()` parses full ARN strings with or without wildcard acceptance.
- `ARN::to_string()`, `operator==`, and `operator<` provide value semantics.
- `ARN::match()` treats `this` as a wildcard-capable pattern.
- `ARNResource::parse()` and `to_string()` handle the resource segment.

## Control Flow
Parsing uses one of two static regexes depending on wildcard support. If the whole string is `*` and wildcards are allowed, it returns a fully wildcard ARN. Otherwise it validates partition and service values, then stores raw region/account/resource strings. Matching rejects wildcard candidates, checks partition/service with enum wildcards, then applies RGW wildcard matching to region, account, and resource.

## State and Persistence
No durable state. ARN objects are value types embedded in policy/account/role logic elsewhere.

## Dependencies and Integration Points
Depends on `rgw_common.h` for wildcard matching and RGW bucket/object types for constructors. Used by IAM, account root ARNs, role/policy logic, and S3 resource policies.

## Risks and Edge Cases
The `operator<` implementation compares fields with OR instead of lexicographic tie-breaking, so it can violate strict weak ordering for some combinations. Service mapping must be kept current for accepted AWS service names. Wildcard case-insensitivity applies to region/account but not resource.

## Test Signals
Tests should cover every supported partition/service, wildcard parse/match, invalid services, bucket/object constructors, ARNResource separator variants, strict weak ordering behavior, and case-sensitive resource matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_arn.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_arn.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_arn.h

## Purpose
Declares ARN value types and enum domains for RGW's AWS-compatible identity/resource policy handling.

## Important APIs, Types, and Functions
- `Partition` enumerates AWS partitions plus wildcard.
- `Service` enumerates accepted AWS service names plus wildcard.
- `ARN` stores partition, service, region, account, and resource; supports parsing, formatting, and pattern matching.
- `ARNResource` stores resource type, resource, and qualifier for parsing resource subparts.
- `std::hash<rgw::Service>` supports service maps.

## Control Flow
The header provides inline formatting operators and constructors but leaves parsing/matching implementation to the `.cc`.

## State and Persistence
No direct persistence. ARN strings are typically serialized in IAM/policy metadata elsewhere.

## Dependencies and Integration Points
Forward-declares RGW bucket/object types and uses Boost optional. It is included by account, IAM, role, and policy code.

## Risks and Edge Cases
The enum set is a compatibility boundary; missing services prevent parsing otherwise valid AWS ARNs. Constructors from strings assume callers supply resource type/path semantics correctly.

## Test Signals
Compile tests and policy tests should exercise parsing, stringification, bucket/object constructors, wildcard resource defaults, and service hashing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_arn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_asio_client.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_asio_client.cc

## Purpose
Implements the Boost.Beast/ASIO `ClientIO` adapter that converts parsed HTTP requests into RGW environment variables and writes HTTP responses through RGW's buffered client IO interface.

## Important APIs, Types, and Functions
- `ClientIO::init_env()` populates `RGWEnv` from Beast request headers, HTTP version, method, target/query, local port, SSL flag, and remote address.
- `complete_request()` updates RGW queue counters.
- `send_status()`, `send_100_continue()`, `send_header()`, `send_content_length()`, and `complete_header()` generate HTTP/1.1 response bytes.
- `dump_date_header()` formats the Date header.

## Control Flow
Construction snapshots keepalive and `Expect: 100-continue` state from the parser. `init_env()` maps `Content-Length`/`Content-Type` to CGI-style names and other headers to `HTTP_...` uppercase dash-transformed variables, then splits target into `SCRIPT_URI` and `QUERY_STRING`. Response methods write into `txbuf` and flush at key boundaries. If a request expected `100-continue` but final status is sent before `100 Continue`, keepalive is disabled to avoid body bytes being misinterpreted as the next request.

## State and Persistence
Runtime state includes the parser reference, local/remote endpoints, `RGWEnv`, output buffer, and keepalive/continue flags. No durable state is persisted.

## Dependencies and Integration Points
Depends on Boost.Beast HTTP parser, Boost.Asio endpoints, RGW `RestfulClient`/`BuffererSink`, output buffering, and RGW perf counters. Used by the beast frontend request path.

## Risks and Edge Cases
The adapter emits raw HTTP/1.1 bytes and relies on callers to avoid header injection in names/values. It preserves the raw request target for `REQUEST_URI` and only simple-splits on `?`. Keepalive handling for early final responses to `Expect: 100-continue` is subtle and important for protocol correctness.

## Test Signals
Tests should cover header environment mapping, query splitting, SSL/server port flags, keepalive/close response headers, early status with `Expect: 100-continue`, date header presence, content length formatting, and perf counter increments/decrements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_asio_client.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_asio_client.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_asio_client.h

## Purpose
Declares the Beast/ASIO RGW client IO adapter used by the RGW beast frontend.

## Important APIs, Types, and Functions
- `ClientIO` derives from `io::RestfulClient` and `io::BuffererSink`.
- Holds a Beast request parser reference, SSL flag, endpoint addresses, environment, static output buffer, and keepalive/continue state.
- Overrides environment initialization, request completion, flushing, status/header/body output, and environment access.

## Control Flow
The header exposes direct `send_body()` forwarding to `write_data()` and `keep_alive()` inspection. Implementation handles the detailed HTTP/env translation.

## State and Persistence
Only per-request runtime state is held. The parser is referenced, so its lifetime must exceed `ClientIO`.

## Dependencies and Integration Points
Includes Boost.Asio TCP, Boost.Beast HTTP/core, Ceph asserts, and RGW client IO abstractions. It is coupled to `request_parser<buffer_body>`.

## Risks and Edge Cases
The parser reference and endpoint snapshots must remain valid during the request. `keep_alive()` returns adapter state, which can be changed by response handling after construction.

## Test Signals
Construction/lifetime tests, send-body forwarding, environment access, and keepalive state transitions should accompany implementation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_asio_client.h -->
