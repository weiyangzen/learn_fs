# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_user.cc

## Purpose
Implements the RADOS-backed RGW administrative user workflow declared in `rgw_user.h`: user create/modify/remove/rename/info/list operations, subuser/key/capability pools, metadata sync handlers, and `RGWUserCtl` service wrappers. It is the glue between admin REST state (`RGWUserAdminOpState`), SAL driver/user objects, RGW metadata services, bucket ownership changes, quotas, IAM account integration, and formatter output.

## Important APIs, types, and functions
- Formatting helpers `dump_user_info()`, `dump_subusers_info()`, `dump_access_keys_info()`, and `dump_swift_keys_info()` produce admin API responses, optionally including stats.
- `RGWUserAdminOpState` methods populate request state, user info, attributes, generated subuser names, key type hints, and version trackers.
- `RGWAccessKeyPool` validates, generates, modifies, and removes S3 and Swift keys. It uses `driver->get_user_by_access_key()` and `driver->get_user_by_swift()` for duplicate detection and updates the `RGWUserInfo` key maps before persisting through `RGWUser::update()`.
- `RGWSubUserPool` owns subuser creation/removal/modification and coordinates subuser key creation/removal through `RGWAccessKeyPool`.
- `RGWUserCapPool` parses capability strings into `RGWUserCaps` and persists changes.
- `RGWUser` handles storage initialization, loading existing users, creating users with defaults, renaming, account adoption, bucket deletion on purge, suspension bucket enablement, and final persistence via SAL `User::store_user()`.
- `RGWUserAdminOp_*` static wrappers expose user, subuser, key, and caps operations to the admin layer and convert some errno values to RGW REST error codes.
- `RGWUserMetadataHandler`, behind `WITH_RADOSGW_RADOS`, implements user metadata sync `get()`, `put()`, `remove()`, and listing against `RGWSI_User`.
- `RGWUserCtl` wraps `RGWSI_User` lookup/store/remove APIs by uid, email, Swift key, and S3 access key.

## Control flow
Admin operations generally construct an `RGWUser`, call `init(dpp, driver, op_state, y)`, and then call one of the contracted methods. `init()` attempts lookup by uid, optional unique email, Swift key, or S3 key, then copies loaded info/attrs/version state into `op_state` and initializes the helper pools. Create calls validate non-existence, build a fresh `RGWUserInfo`, apply configured/default quotas and placement fields, optionally add a key and caps with deferred persistence, then calls `update()`. Modify ensures the user exists, clones `old_info`, applies requested fields, manages duplicate email checks, bucket enable/disable on suspension, account migration and bucket adoption, optional key modifications, then persists. Remove lists user buckets and either rejects when buckets exist without `purge_data` or deletes buckets before `remove_user()`. Rename creates a stub destination user, rewrites bucket ACL/ownership, rewrites Swift key ids, then persists the renamed user.

## State and persistence behavior
Primary durable state is `RGWUserInfo` plus attrs and index objects managed by SAL `User::store_user()` and `RGWSI_User::store_user_info()`. `old_info` tracks the previously loaded user so store paths can rewrite secondary indexes correctly. `RGWObjVersionTracker` is copied into and out of `op_state` around reads/writes for optimistic object versioning. User removal clears `op_state` and local populated state. Metadata sync serializes `RGWUserCompleteInfo` including optional attrs. Account migration mutates bucket owner state through bucket `chown()` and user bucket listings, while suspension mutates bucket enabled flags through `driver->set_buckets_enabled()`.

## Dependencies and integration points
Depends on SAL `Driver`, `User`, and `Bucket` interfaces, `RGWSI_User`, `RGWMetadataHandler`, `RGWMetadataLister`, quota helpers, IAM validation (`validate_iam_user_name()`), account validation/loading, bucket chown helpers, formatter/flusher output, and Ceph coroutine/yield plumbing. It integrates with admin REST operations, metadata log sync, multisite user metadata replication, account IAM-style users, bucket listing/removal, and stats sync/load paths.

## Risks and edge cases
User and key operations have several multi-object update windows: keys/subusers/caps are edited in memory and then persisted as a whole user object, while rename and account adoption update many buckets. Failures after partial bucket ownership or ACL changes can leave externally visible partial migration. Duplicate detection depends on configured unique-email behavior and current secondary indexes. Swift key ids are derived from `user:subuser`; rename must rewrite them. Subuser removal ignores the return from `remove_subuser_keys()`, so key purge errors may be hidden before persisting subuser deletion. `generate_subuser()` appends random suffix directly to the full user string without separator. Metadata `mutate()` is unsupported. Several operations translate errors inconsistently between negative errno, RGW-specific constants, and formatted messages.

## Test signals
Useful tests include admin create/modify/remove/list/info flows, duplicate uid/email/S3/Swift key checks, create with generated and explicit keys, subuser key purge, capability parsing, user suspension toggling bucket state, purge-data bucket deletion, account-root validation, account adoption bucket ownership, rename with bucket ACL/chown and Swift key rewrite, metadata sync get/put/remove/list, and failure injection around `store_user()`, bucket chown, and secondary index lookups.
