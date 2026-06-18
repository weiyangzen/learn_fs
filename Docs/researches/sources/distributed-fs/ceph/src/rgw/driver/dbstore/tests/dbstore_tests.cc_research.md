# sources/distributed-fs/ceph/src/rgw/driver/dbstore/tests/dbstore_tests.cc

## Purpose

This file is a GoogleTest integration suite for the RGW DBStore backend, currently configured to run against `SQLiteDB`. It drives the `rgw::store::DB` interface through both string-dispatched `ProcessOp()` calls and typed helper APIs, validating the persistence model for users, buckets, objects, versioned objects, object data parts, omap-like metadata, and lifecycle tables.

The tests intentionally reuse a single database environment across the whole test program. That makes the file closer to an ordered backend smoke/integration scenario than isolated unit tests: users, buckets, and objects created in earlier tests are read, updated, or removed in later tests.

## Important APIs, Types, and Functions

- `gtest::Environment` owns Ceph global initialization, creates a `SQLiteDB` for a tenant namespace, calls `Initialize()`, and destroys the backend in `TearDown()`.
- `DBStoreTest` provides common fixtures: user id/name, bucket name, object name, default `DBOpParams`, and `dpp` from `db->get_def_dpp()`.
- `DBGetDataCB` implements `RGWGetDataCB::handle_data()` to capture data returned by read iteration.
- `DBStoreTest::write_object()` exercises `DB::Object::Write`, preparing the write, setting metadata, object owner/category, head data, ACL attr, and calling `write_meta()`.
- The test body covers `db->ProcessOp()` commands including `InsertUser`, `GetUser`, `InsertBucket`, `GetBucket`, `PutObject`, `GetObject`, `ListVersionedObjects`, `PutObjectData`, and lifecycle-related calls.
- Typed APIs exercised include `store_user()`, `get_user()`, `create_bucket()`, `get_bucket_info()`, `list_buckets()`, `update_bucket()`, `remove_bucket()`, `remove_user()`, `DB::Object::{Read,Write,Delete}`, object omap helpers, and lifecycle table helpers.

## Control Flow

`main()` parses optional logfile/loglevel/tenant arguments, initializes GoogleTest, installs one global `Environment`, and runs all tests. The environment constructs one DB instance, so test order and persisted data are significant.

Fixture setup reinitializes `GlobalParams` before every test, but does not reset database state. The user tests first insert `user_id1`, then query by default key, email, access key, and typed API. `StoreUser` creates and updates a second user while validating object-version conflict handling. Later user removal tests depend on that second user state.

Bucket tests create `bucket1`, update attrs and info, read it back, create additional buckets through the higher-level API, list buckets with pagination markers, change ownership, and remove buckets. Object tests create simple objects, read state and attrs, write/read payloads through `DB::Object` operations, list bucket objects, delete one object, then exercise versioning flows with multiple object instances and delete-marker behavior.

The final sections test omap-style key/value storage on an object, separate object data part CRUD, lifecycle head/entry table operations, and cleanup of the original bucket/user before inserting a fixed "testid" user.

## State and Persistence Behavior

All state is persisted in the SQLite-backed DB namespace chosen by `Environment::tenant`. The default tenant is time-based (`default_ns_<time>`), so ordinary runs avoid reusing stale state. Tests rely on shared persisted state across cases: for example, `GetUser` assumes `InsertUser` ran first, `GetBucket` assumes bucket update tests have already executed, and object/versioning tests build on previously created bucket/user records.

The file verifies several persistence contracts:

- User info stores tenant, email, suspended/max bucket flags, placement tags, access keys, attrs, and version tracker fields.
- User updates enforce optimistic version checks, returning `-ECANCELED` when the read version is stale.
- Bucket info stores bucket identity, owner, marker, attrs, mtime, version/tag, placement rule, and creation time.
- Bucket listing uses markers and truncation.
- Object metadata stores category, storage class, head data, attrs, size, version instance, and delete-marker/current flags.
- Object data records store part number, offset, multipart part string, payload, and object mtime.
- Lifecycle tables persist `LCHead` and `LCEntry` records with put/get/update/list/remove behavior.

## Dependencies and Integration Points

The suite depends on GoogleTest, Ceph global initialization (`global_init()`), `SQLiteDB`, `dbstore.h`, RGW common types, Ceph clocks, and Ceph `bufferlist` encode/decode helpers. It is a direct integration point for the DBStore SAL/storage layer because it drives both DBStore operation dispatch and the lower-level nested object/bucket operation classes.

The tests also encode RGW-specific assumptions: `RGW_ATTR_ACL`, `RGW_ATTR_LC`, `RGW_ATTR_ETAG`, `RGWObjVersionTracker`, `RGWBucketInfo`, `RGWBucketEnt`, versioning constants, bucket/object keys, and lifecycle structs.

## Risks and Edge Cases

- The test suite is order-dependent because the single DB environment is shared and tests are not independent. Randomized test order or selective test execution can fail for reasons unrelated to the target API.
- Several assertions depend on map iteration order for access keys and attrs. `std::map` makes that deterministic by key, but future container changes would break assumptions.
- The tests mostly assert successful paths and selected stale-version failures; they do not deeply validate malformed input, missing records, concurrent updates, or rollback behavior.
- Debug `cout` output is noisy and could obscure real failures in automation logs.
- `DBStoreTest::write_object()` passes `b1.length()+1` to `write_meta()` while object state sizes are independently set, so the test encodes a specific backend expectation about stored encoded data length rather than raw logical size.
- Shared global `bucket_mtime` and `marker1` introduce hidden coupling between tests.

## Test Signals

This file itself is the test signal. It provides broad coverage of DBStore persistence and RGW-facing API shape, including version checks, pagination, object attributes, versioned object listing/read/delete, object data parts, omap helpers, lifecycle metadata, and backend cleanup. Its strongest signal is end-to-end integration with a real SQLite DBStore instance; its weakest signal is unit isolation.
