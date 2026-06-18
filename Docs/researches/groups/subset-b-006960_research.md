# subset-b-006960 research

Grouped research report for the subset B item covering RGW DBStore tests, immutable/json config stores, Motr SAL, and the POSIX bucket cache translation unit. Each section is delimited for reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/tests/dbstore_tests.cc -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/tests/dbstore_tests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/immutable_config/store.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/immutable_config/store.cc

## Purpose

This file implements `ImmutableConfigStore`, a read-only `ConfigStore` that serves one preconstructed `RGWZoneGroup`, one `RGWZoneParams`, and one `RGWPeriodConfig`. It is used when RGW wants config-store semantics without a mutable persistent config backend.

The implementation returns read-only errors for mutating operations, `-ENOENT` for unsupported realm/period lookups, and returns the configured zonegroup/zone/period config for the small subset of reads needed by a single-zone immutable setup.

## Important APIs, Types, and Functions

- `ImmutableConfigStore::ImmutableConfigStore()` copies the supplied zonegroup, zone, and period config into const members.
- Realm methods reject writes with `-EROFS`, return `-ENOENT` for reads, return an empty list for `list_realm_names()`, and return `nullptr` for watchers.
- Period methods reject create/delete/latest-epoch updates with `-EROFS`, return `-ENOENT` for period reads, and list no period ids.
- `ImmutableZoneGroupWriter` and `ImmutableZoneWriter` implement writer interfaces whose `write()`, `rename()`, and `remove()` all return `-EROFS`.
- Zonegroup read methods return the stored zonegroup by id, name, or default access, and can provide an immutable writer wrapper.
- Zone read methods return the stored zone by id, name, or default access, and can provide an immutable writer wrapper.
- `read_period_config()` returns the stored period config for empty realm id.
- `create_immutable_config_store()` constructs the concrete store behind a `std::unique_ptr<ConfigStore>`.

## Control Flow

Construction captures immutable snapshots of the input config objects. Each API method then either rejects mutation, checks whether the requested id/name matches the stored object, or emits a short list result.

The zonegroup path accepts an empty realm id as the implicit realm. `read_default_zonegroup_id()` returns `zonegroup.id` only when `realm_id` is empty, and `read_default_zonegroup()` always returns the stored zonegroup. The zone path is asymmetric: `read_default_zone_id()` returns `zone.id` only when `realm_id` is non-empty, while `read_default_zone()` returns the stored zone only when `realm_id` is empty.

List methods implement marker-based single-entry listing. If the marker sorts before the stored name, they write the name into `entries[0]`, set `result.next`, and expose one entry; otherwise they return an empty span.

## State and Persistence Behavior

There is no external persistence. All state lives in the store object as const value copies:

- `zonegroup`
- `zone`
- `period_config`

No method mutates those members. Mutating calls consistently return `-EROFS` except realm period notification, which returns `-ENOTSUP`, and create watcher, which returns `nullptr`.

## Dependencies and Integration Points

The implementation depends on `rgw_sal_config.h` through the header, `rgw_zone.h` types, and `rgw_realm_watcher.h` for the watcher return type. It implements the `ConfigStore` interface used by RGW realm/zone/period configuration code and is used by the JSON config store factory after JSON parsing and normalization.

## Risks and Edge Cases

- List methods write `entries[0]` without checking whether the provided span is empty. Callers must supply capacity for at least one entry.
- Realm and period support is intentionally absent. Code paths requiring real realm or period records will see `-ENOENT`/empty lists even though zonegroup and zone reads work.
- The realm-id handling is inconsistent between `read_default_zonegroup_id()`, `read_default_zone_id()`, and `read_default_zone()`, which can surprise callers expecting one implicit realm convention.
- Writer objects are returned even though writes always fail. That is consistent with read-only semantics but can defer failures until later writer use.

## Test Signals

No direct tests are in this file. Coverage is likely indirect through config-store users and JSON config store creation. Useful tests would assert mutation failures, id/name lookup behavior, marker listing, empty-span safety, and the realm-id conventions for default zonegroup/zone reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/immutable_config/store.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/immutable_config/store.h -->
# sources/distributed-fs/ceph/src/rgw/driver/immutable_config/store.h

## Purpose

This header declares `rgw::sal::ImmutableConfigStore`, a read-only implementation of the RGW `ConfigStore` abstraction. It exposes a full override surface for realm, period, zonegroup, zone, and period-config operations while documenting that the store serves a given default zonegroup and zone.

## Important APIs, Types, and Functions

- `ImmutableConfigStore` derives from `ConfigStore`.
- The constructor accepts `const RGWZoneGroup&`, `const RGWZoneParams&`, and `const RGWPeriodConfig&`.
- Realm API overrides cover default realm id read/write/delete, realm create/read by id/read by name/read default/read id, period notification, watcher creation, and realm-name listing.
- Period API overrides cover create/read/delete/list/update latest epoch.
- ZoneGroup API overrides cover default zonegroup id read/write/delete, create/read by id/read by name/read default, and list names.
- Zone API overrides cover default zone id read/write/delete, create/read by id/read by name/read default, and list names.
- PeriodConfig API overrides cover read and write.
- Private state is three const value members: `zonegroup`, `zone`, and `period_config`.
- `create_immutable_config_store()` is the public factory returning `std::unique_ptr<ConfigStore>`.

## Control Flow

The header describes the contract implemented in the `.cc`: callers interact through the generic `ConfigStore` interface, while construction fixes the only zonegroup, zone, and period config available. Optional writer out-parameters are supported by the signatures, allowing immutable writer wrappers to be returned where reads succeed.

## State and Persistence Behavior

The declared state is immutable after construction and has no persistent backing store. Because the members are const value copies, callers cannot observe later changes to the original objects passed into the constructor.

## Dependencies and Integration Points

The header depends on `rgw_sal_config.h` for `ConfigStore`, writer interfaces, `ListResult`, and `optional_yield`; and `rgw_zone.h` for `RGWZoneGroup`, `RGWZoneParams`, `RGWPeriod`, `RGWRealm`, and `RGWPeriodConfig`. It is consumed by the implementation and by `json_config/store.h` as the factory target for parsed JSON config.

## Risks and Edge Cases

- The class advertises the entire `ConfigStore` surface, but the implementation intentionally supports only a narrow single-zone subset. Callers must be prepared for `-EROFS`, `-ENOENT`, or `-ENOTSUP`.
- Value-copying potentially makes large config structures more expensive but keeps lifetime simple.
- Because private members are const, runtime reconfiguration requires constructing a new store.

## Test Signals

The header has no standalone tests. Its testability hinges on interface-conformance builds and behavioral tests against the factory and read-only methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/immutable_config/store.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/json_config/store.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/json_config/store.cc

## Purpose

This file implements a JSON-backed factory for creating an immutable RGW config store. The intended flow is to read a JSON file containing `zonegroup`, `zone`, and `period_config`, decode those into RGW structures, normalize missing defaults, validate that the config describes a single-zone deployment, then return an `ImmutableConfigStore`.

## Important APIs, Types, and Functions

- `DecodedConfig` holds `RGWZoneGroup zonegroup`, `RGWZoneParams zone`, and `RGWPeriodConfig period_config`; its `decode_json()` method decodes those named JSON fields.
- `parse_config()` reads a file into a `bufferlist`, parses JSON with `JSONParser`, decodes into `DecodedConfig`, logs failures, and throws `std::system_error` on read/parse/decode errors.
- `sanity_check_config()` fills default ids/names/api name, adds default placement, initializes zone pool names, validates or creates the zonegroup zone entry, enables supported zone features for generated zone entries, and sets default placement target.
- `create_json_config_store()` creates a `DecodedConfig`, invokes parsing and sanity checks, then delegates to `create_immutable_config_store()`.

## Control Flow

The intended factory sequence is:

1. Read the JSON file.
2. Parse it.
3. Decode `zonegroup`, `zone`, and `period_config`.
4. Normalize empty zonegroup and zone identifiers to `"default"`.
5. Ensure `zone.placement_pools` has `"default-placement"` with `STANDARD`.
6. Run `rgw::init_zone_pool_names()` to populate pool names.
7. If a zonegroup already has one zone, verify that its id/name/master zone match the decoded zone.
8. If the zonegroup has no zones, call `rgw::add_zone_to_group()` with all supported zone features enabled.
9. Add `"default-placement"` to zonegroup placement targets and default placement.
10. Construct an immutable config store.

## State and Persistence Behavior

The JSON file is read once during factory creation. No live file watching or persistence is performed after the immutable store is created. Normalized config lives as value state in the returned `ImmutableConfigStore`.

Error handling is exception-based within parse/sanity helpers: file read failures throw system errors using the negated Ceph errno, parse/decode failures throw invalid-argument system errors, and helper failures throw the underlying errno.

## Dependencies and Integration Points

The implementation depends on Ceph `bufferlist`, `common/errno.h`, `common/ceph_json.h`, RGW zone helpers (`rgw_zone.h`, `rgw::init_zone_pool_names()`, `rgw::add_zone_to_group()`), and the immutable config store factory. It integrates with RGW deployments that want to bootstrap a static single-zone config from a JSON document.

## Risks and Edge Cases

- High risk: `parse_config()` currently returns `void` and decodes into a local `DecodedConfig config`; `create_json_config_store()` creates a separate default-constructed `DecodedConfig config`, calls `parse_config(dpp, filename.c_str())`, and then sanity-checks the still-empty local object. As written, successfully parsed JSON content is discarded, so the returned store is based on defaults rather than file content.
- `parse_config()` should likely return `DecodedConfig` or accept an output reference.
- `sanity_check_config()` unconditionally `emplace()`s `"default-placement"` into `zone.placement_pools` and zonegroup placement targets; existing entries are preserved, but incompatible existing definitions are not reconciled.
- The single-zone validator rejects zonegroups with more than one zone and requires exact id/name/master-zone matches for a one-zone group.
- `rgw_pool pool` is default-constructed, so correct pool naming depends on `init_zone_pool_names()` filling names later.
- Exceptions propagate from the factory; callers must expect construction-time throws rather than error-code returns.

## Test Signals

No tests are in this file. Important tests would include successful parsing with non-default ids/names, invalid JSON, missing file, one-zone mismatch errors, multi-zone rejection, generated single-zone defaults, and a regression that proves decoded JSON is actually passed into `create_immutable_config_store()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/json_config/store.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/json_config/store.h -->
# sources/distributed-fs/ceph/src/rgw/driver/json_config/store.h

## Purpose

This header declares the JSON config store factory for RGW SAL configuration. It is a small public entry point that converts a JSON file path into a `std::unique_ptr<ConfigStore>`, implemented as an immutable config store.

## Important APIs, Types, and Functions

- Includes `driver/immutable_config/store.h`, making the immutable store and `ConfigStore` abstraction available.
- Declares `rgw::sal::create_json_config_store(const DoutPrefixProvider* dpp, const std::string& filename) -> std::unique_ptr<ConfigStore>`.

## Control Flow

Consumers call the factory with a logging prefix provider and JSON filename. The implementation handles file IO, JSON parsing, config normalization, and immutable store construction.

## State and Persistence Behavior

The header declares no state. The returned store is expected to contain a snapshot of decoded file state, with no runtime persistence or update mechanism.

## Dependencies and Integration Points

This is the integration point for code that wants `ConfigStore` semantics from a JSON file rather than RADOS or another mutable config backend. It relies on immutable config store declarations and RGW SAL config types.

## Risks and Edge Cases

- The header documentation says the factory parses zonegroup and zone from the given JSON filename; the implementation also decodes `period_config`.
- The API uses exceptions indirectly through the implementation, despite returning a pointer rather than an error-code wrapper.
- There is no schema type exposed here, so callers must know the expected JSON keys out of band.

## Test Signals

No direct tests exist here. Interface coverage is compile-time; behavioral coverage belongs to the `.cc` factory tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/json_config/store.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/motr/rgw_sal_motr.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/motr/rgw_sal_motr.cc

## Purpose

This file implements the CORTX Motr RGW SAL backend. It maps RGW users, buckets, objects, multipart uploads, metadata caches, and store-driver operations onto Motr indices and Motr objects. The implementation is a proof-of-concept style backend: the main object/user/bucket/multipart paths are present, while many RGW features return success without real work or return not-supported/not-found placeholders.

## Important APIs, Types, and Functions

- `MotrMetaCache::{get,put,remove,invalid}` wraps RGW `ObjectCache` for metadata blobs. Distribution/watch hooks are placeholders.
- `MotrStore::list_buckets()` scans a per-user Motr index named `motr.rgw.user.info.<user>` and fills RGW `BucketList`.
- `MotrUser::{load_user_from_idx,load_user,store_user,remove_user,create_bucket}` persists `MotrUserInfo` in the global users index, manages access-key/email indices, creates per-user bucket-list indices, and creates buckets.
- `MotrBucket::{put_info,load_bucket,link_user,unlink_user,list,remove,create_bucket_index,create_multipart_indices}` persists `MotrBucketInfo`, manages bucket indices, links bucket entries to users, lists objects, and removes bucket structures.
- `MotrObject::{load_obj_state,get_obj_attrs,get_bucket_dir_ent,create_mobj,open_mobj,write_mobj,read_mobj,delete_mobj,update_version_entries}` bridges RGW object metadata with Motr object IO.
- `MotrAtomicWriter` implements normal object PUT by accumulating data, creating/writing a Motr object, and then publishing metadata in the bucket index.
- `MotrMultipartUpload` and `MotrMultipartWriter` implement multipart setup, part writing, part listing, completion, abort, and part deletion using bucket multipart and object parts indices.
- Motr index helpers include `index_name_to_motr_fid()`, `create_motr_idx_by_name()`, `delete_motr_idx_by_name()`, `do_idx_op_by_name()`, `do_idx_op()`, `do_idx_next_op()`, and `next_query_by_name()`.
- `newMotrStore()` is the extern "C" plugin factory that reads Motr config options, initializes `m0_client`, container, UFID generator, and global indices.

## Control Flow

Store creation starts in `newMotrStore()`: a `MotrStore` is allocated, Motr endpoints/fids/profile are read from Ceph config, tracing is configured, `m0_client_init()` opens the Motr client, the uber container is initialized, UFID generation is initialized, and global indices are created.

User creation/update loads the existing user from `motr.rgw.users`, checks optimistic version state, encodes `MotrUserInfo`, writes it back, stores one access key in `motr.rgw.accesskeys`, stores email mapping in `motr.rgw.emails`, creates the per-user bucket index, and updates cache. User lookup by access key/email first reads the secondary index, then loads the user record.

Bucket creation through `MotrUser::create_bucket()` checks existence, fills `RGWBucketInfo`, writes bucket instance metadata to `motr.rgw.bucket.instances`, creates `motr.rgw.bucket.index.<bucket>`, creates `motr.rgw.bucket.<bucket>.multiparts`, and links a `RGWBucketEnt` into the owner index. Bucket listing and object listing use `next_query_by_name()` over Motr sorted index keys with marker/prefix/delim support.

Normal object PUT uses `MotrAtomicWriter`. `prepare()` allocates Motr IO vectors and detects an old object. `process()` accumulates up to 32 MiB before flushing. `write()` creates/opens a Motr object, computes optimal block size from Motr layout/pool attributes, and issues synchronous `M0_OC_WRITE` operations. `complete()` encodes `rgw_bucket_dir_entry`, attrs, and `MotrObject::Meta` into the bucket index and updates metadata cache; versioned writes first clear old current flags through `update_version_entries()`.

GET/read uses `MotrReadOp::prepare()` to load metadata, enforce conditional headers, open the Motr object or multipart part objects, and set attrs/size/mtime. `iterate()` reads object data synchronously via `read_mobj()` or assembled multipart reads. `read()` itself is a stub returning 0.

DELETE loads the bucket-dir entry, removes metadata cache and bucket-index entry, and deletes the Motr object or multipart part objects. Versioning/delete-marker behavior is noted as TODO and not implemented like RADOS.

Multipart init creates a unique upload id and records a metadata entry in the bucket multipart index, then creates `motr.rgw.object.<bucket>.<oid>.parts`. Each part is a separate Motr object and part metadata entry. Completion validates part count/order/etag/min-size, computes multipart ETag, writes a final bucket-index object entry with `MultiMeta` semantics, caches it, and removes the multipart-index entry.

## State and Persistence Behavior

Persistent state is stored mostly in Motr DIX indices:

- Global indices: `motr.rgw.users`, `motr.rgw.bucket.instances`, `motr.rgw.bucket.headers`, `motr.rgw.accesskeys`, `motr.rgw.emails`.
- Per-user bucket lists: `motr.rgw.user.info.<user-id>`.
- Per-bucket object index: `motr.rgw.bucket.index.<bucket-name>`.
- Per-bucket multipart in-progress index: `motr.rgw.bucket.<bucket-name>.multiparts`.
- Per-object multipart parts index: `motr.rgw.object.<bucket-name>.<object>.parts`.

Object payloads are stored as Motr objects. The bucket index value for a normal object encodes `rgw_bucket_dir_entry`, attrs, and `MotrObject::Meta`, where `Meta` contains the Motr object id, pver, and layout id needed to reopen/delete/read the Motr object.

Metadata cache state is local process memory using `ObjectCache`. Cache invalidation is local only because `distribute_cache()` and `watch_cb()` are placeholders. This creates eventual consistency risk across RGW instances.

## Dependencies and Integration Points

The file depends on Motr C headers (`motr/config.h`, `motr/client.h`, `motr/layout.h`, helper UFID APIs), Ceph/RGW SAL types, RGW compression, bucket/object/common utilities, MD5 helpers, Ceph logging, and RGW config values such as `motr_my_endpoint`, `motr_ha_endpoint`, `motr_profile_fid`, and tracing flags.

It integrates with RGW through `StoreDriver`, `StoreUser`, `StoreBucket`, `StoreObject`, `StoreWriter`, `StoreMultipartUpload`, `StoreNotification`, `StoreLuaManager`, placement/zone abstractions, and plugin loading via `newMotrStore()`.

## Risks and Edge Cases

- Many methods are stubs returning 0 or null: stats, usage, quota, lifecycle, restore, append writer, bucket chown, ACL persistence, object attrs mutation, omap, sync policy, metadata listing, notifications, service-map registration, and more. Returning success can mask unsupported behavior.
- Several apparent compile/integration hazards exist in this source as read: `MotrStore::get_lua_manager()` calls a constructor signature not declared in the header, OIDC methods are defined as `DaosStore::...` inside the Motr file, `MotrAtomicWriter::complete()` and `MotrMultipartWriter::complete()` signatures appear inconsistent with the header's checksum-bearing overrides, and multipart completion references identifiers such as `obj_part` and `etag_bl` that are not defined in the shown scope.
- Bucket removal references `forward_to_master`, `bucket_version`, and `req_info` without visible local definitions in the function, suggesting stale code copied from another backend or macro/member assumptions.
- Versioned object updates lack distributed locking, and the code explicitly documents a race that can leave two current versions.
- Cache invalidation is not distributed; multi-RGW deployments can read stale user, bucket, or object metadata.
- Index names are converted to Motr FIDs with MD5, with a comment noting collision risk.
- Several operations are synchronous and block on `M0_TIME_NEVER`; hung Motr operations can hang RGW request paths.
- Object write pads data to optimal block sizes; logical size is tracked separately, so read paths must consistently limit callback length to the requested actual bytes.
- Multipart completion stores a dummy `MotrObject::Meta` for the final composed object and relies on part metadata for reads/deletes.
- Access-key storage only stores the first key from `info.access_keys` during user store, while deletion logic tracks sets; multi-key users may be incomplete.

## Test Signals

No tests are in this file. Nearby DBStore tests do not exercise Motr. Meaningful validation would require a Motr-backed integration environment covering plugin initialization, global/per-user/per-bucket index creation, user lookup by id/email/access key, bucket list pagination, object PUT/GET/DELETE, conditional GET, versioned write races, multipart init/upload/list/complete/read/abort, and unsupported-feature error behavior. Build tests are especially important because several definitions appear inconsistent with declarations or current SAL interfaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/motr/rgw_sal_motr.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/motr/rgw_sal_motr.h -->
# sources/distributed-fs/ceph/src/rgw/driver/motr/rgw_sal_motr.h

## Purpose

This header declares the CORTX Motr implementation of the RGW Store Abstraction Layer. It defines the Motr-backed store, user, bucket, object, writer, multipart, zone, notification, Lua, cache, and helper types that the implementation uses to map RGW operations onto Motr indices and objects.

## Important APIs, Types, and Functions

- Global index names define the persistent Motr metadata roots for users, bucket instances, bucket headers, access keys, and emails.
- `MotrMetaCache` wraps `ObjectCache` and declares metadata cache get/put/remove/invalid plus placeholder distribution/watch callbacks.
- `MotrUserInfo`, `MotrEmailInfo`, and `MotrAccessKey` are encoded records for Motr user metadata and secondary lookup indices.
- `MotrNotification` is a minimal `StoreNotification` implementation whose publish methods return success.
- `MotrUser` derives from `StoreUser` and declares user load/store/remove, bucket creation, attrs/stats/usage operations, MFA verification, and helpers for user-info indices.
- `MotrBucket` derives from `StoreBucket`; it embeds encoded `MotrBucketInfo`, object listing, removal, bucket info persistence, owner linking, multipart listing, ACLs, stats/quota/check methods, and bucket cloning.
- `MotrPlacementTier`, `MotrZoneGroup`, and `MotrZone` adapt RGW placement and zone abstractions to the Motr store.
- `MotrLuaManager` declares script/package methods for Lua manager integration.
- `MotrObject` derives from `StoreObject`; it contains encoded `Meta` for Motr object id/pver/layout, nested read/delete ops, object attrs/state/copy/delete methods, omap methods, Motr object open/create/read/write/delete helpers, multipart part helpers, and version-entry update.
- `MPMotrSerializer` is a placeholder multipart lock with no real locking.
- `MotrAtomicWriter` and `MotrMultipartWriter` declare normal object and multipart part write flows.
- `MotrMultipartPart` and `MotrMultipartUpload` model multipart uploaded parts and the multipart upload lifecycle.
- `MotrStore` derives from `StoreDriver` and declares the main RGW backend API plus Motr-specific index helpers, secondary-index helpers, metadata cache initialization, and Motr client/container state.
- `obj_time_weight` implements timestamp comparison logic for conditional request checks.

## Control Flow

The declarations show RGW SAL ownership relationships: `MotrStore` creates users, buckets, objects, writers, notifications, zones, and multipart uploads; `MotrUser` creates buckets; `MotrBucket` creates objects and multipart uploads; `MotrObject` creates read/delete operations and writers manipulate `MotrObject` payload/metadata.

The persistent metadata path is declared as encoded C++ structs written into Motr indices. The object data path is declared through `MotrObject::Meta` plus `m0_obj` handles, with `MotrAtomicWriter` and `MotrMultipartWriter` responsible for publishing metadata after data IO.

## State and Persistence Behavior

`MotrStore` owns process state for Motr: `CephContext`, `m0_client`, `m0_container`, config structures, and three metadata caches. It also owns a `MotrZone` and sync module reference.

Persistent metadata structures are all Ceph-encoded into `bufferlist` values. `MotrObject::Meta` is the bridge from RGW metadata entries to actual Motr object payloads. Per-object open state is represented by `struct m0_obj* mobj`, which is closed by the object destructor or explicit close.

## Dependencies and Integration Points

The header has a hard dependency on Motr C client/config headers inside `extern "C"`, and on RGW headers including `rgw_sal_store.h`, `rgw_rados.h`, `rgw_notify.h`, `rgw_role.h`, `rgw_multi.h`, and `rgw_putobj_processor.h`. It integrates deeply with RGW SAL virtual interfaces and Ceph encoding macros.

## Risks and Edge Cases

- The header exposes a large surface where many methods are later implemented as placeholders. Callers may receive success from unsupported features.
- `MotrObject::delete_object()` declaration appears to contain typos (`td::list`, `GWObjVersionTracker`) rather than standard/RGW types, which is a build risk unless hidden by conditional compilation or stale code paths.
- `MotrZone` allocates realm/zone/period objects with `new` in constructors but its destructor is defaulted, implying leaks.
- `MotrStore` destructor deletes cache pointers that are not visibly initialized to null in the header constructor, so construction failure or missing `init_metadata_cache()` could make deletion unsafe.
- `MPMotrSerializer` does not enforce locking, so multipart serialization is not safe across concurrent clients.
- `obj_time_weight::init(RGWObjState*)` references `dpp` in an error log without a visible parameter/member in the struct, another build or stale-code risk.
- Several override signatures need to track the exact current RGW SAL interface; any drift produces compile failures.

## Test Signals

There are no tests in the header. Compile coverage against current RGW SAL interfaces is essential. Runtime tests should focus on object lifecycle, index persistence, multipart locking semantics, cache initialization/destruction, and unsupported method behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/motr/rgw_sal_motr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/posix/bucket_cache.cpp -->
# sources/distributed-fs/ceph/src/rgw/driver/posix/bucket_cache.cpp

## Purpose

This translation unit currently only includes `bucket_cache.h` after editor modelines. It exists to provide a compilation unit for the POSIX driver bucket cache declarations or future out-of-line definitions.

## Important APIs, Types, and Functions

No functions, classes, or variables are defined in this file. The only functional line is:

- `#include "bucket_cache.h"`

## Control Flow

There is no runtime control flow in this file.

## State and Persistence Behavior

No state is declared or persisted here. Any bucket-cache state lives in the included header or other POSIX driver files.

## Dependencies and Integration Points

The file depends entirely on `bucket_cache.h`. Its integration value is build-system oriented: if compiled, it forces the header to parse as a standalone include and can host future non-inline bucket cache definitions without changing build lists.

## Risks and Edge Cases

- Because it has no out-of-line definitions, it may be redundant unless the build system expects the object file.
- Any substantive bucket-cache behavior must be researched in `bucket_cache.h`, not this file.

## Test Signals

The only signal is compile coverage that `bucket_cache.h` can be included from a `.cpp` file. There is no behavioral test surface in this translation unit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/posix/bucket_cache.cpp -->
