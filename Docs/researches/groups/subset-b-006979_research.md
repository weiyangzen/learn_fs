# subset-b-006979 research

This grouped report covers the Ceph RGW RADOS user, role, topic, shard I/O, sync fairness, and JWT base64 files assigned to subset-b-006979. Each section preserves the source path in its title and is intended to be split into the corresponding source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_user.cc -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_user.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_user.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_user.h

## Purpose
Declares RGW user administration types and RADOS/SAL-facing helper APIs. The header defines request-state carriers, user/key/subuser/cap pools, admin operation wrappers, and user-control service wrappers used by `rgw_user.cc` and the broader RGW admin and metadata stack.

## Important APIs, types, and functions
- Constants define key lengths, default anonymous id, random subuser length, and S3 XML namespace.
- Free functions declare secret/access key generation, stats sync, anonymous user setup, permission conversion, and tenant validation.
- `RGWUID` is an encodable UID wrapper with formatter and test instances.
- `bucket_meta_entry` models bucket usage summaries.
- Enums `ObjectKeyType`, `RGWKeyPoolOp`, and `RGWUserId` identify key/admin operation modes.
- `RGWUserAdminOpState` is the central mutable request object. It stores requested user fields, key/subuser/cap operations, quotas, rate limits, temp URL keys, MFA ids, placement, flags indicating which fields were explicitly specified, lookup result flags, and methods that set and query that state.
- `RGWAccessKeyPool`, `RGWSubUserPool`, and `RGWUserCapPool` expose public `add()`, `remove()`, and `modify()` contracts while hiding validation and persistence sequencing.
- `RGWUser` declares lifecycle and admin operations plus helper-pool members.
- `RGWUserAdminOp_User`, `_Subuser`, `_Key`, and `_Caps` declare static admin entry points that write formatter output.
- `RGWUserCtl` provides typed `GetParams`, `PutParams`, and `RemoveParams` option builders around `RGWSI_User`.

## Control flow
Callers build `RGWUserAdminOpState`, set requested fields using setters that also mark specification flags, initialize `RGWUser` with a SAL driver, then call an operation. Helper pools are initialized from the `RGWUserAdminOpState` after user lookup or user-info construction, so their maps point directly into `RGWUserInfo` owned by the state. Admin wrappers hide this setup for common REST operations.

## State and persistence behavior
The header itself does not persist, but it defines the state that drives persistence: object version trackers, old/new user ids, user attrs, quotas, rate limits, key maps, subusers, flags for generated credentials, purge behavior, and secondary lookup result flags. `RGWUserCtl` method signatures expose how user info and attrs are read, stored, and removed through `RGWSI_User`, optionally with version and mtime parameters.

## Dependencies and integration points
Includes Ceph encoding/types, RGW common/tool/string/format SAL forward declarations, formatter support, quotas/rate limits via included RGW common types, and metadata handler factory declarations. It is consumed by admin REST code, RADOS SAL services, metadata sync, and bucket/user stats helpers.

## Risks and edge cases
The state object contains many boolean flags that must stay consistent with values; callers can set conflicting combinations such as explicit key type plus subuser context. Getters expose mutable `RGWUserInfo` maps, making helper pools sensitive to initialization order. Several setters silently ignore empty input, which can make explicit clearing require separate `*_specified` flags. `get_attrs()` returns by value, while `set_attrs()` copies into the SAL user attrs.

## Test signals
Compile and unit coverage should verify flag-setting semantics, generated-key/subuser defaults, helper-pool initialization failures for anonymous/uninitialized users, `RGWUserCtl` parameter builders, and ABI/encoding compatibility for `RGWUID`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/role.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/role.cc

## Purpose
Implements v2 IAM role metadata storage on RADOS. It stores role records by globally unique id, maintains name and path/account indexes for lookup/listing, integrates with account resource lists, and exposes an RGW metadata handler for multisite metadata sync.

## Important APIs, types, and functions
- `read_by_id()` reads `RGWRoleInfo` from `roles.{id}` objects and optional tags from the raw `tagging` attr.
- `read_by_name()` resolves a name index object to a role id, then reads by id.
- `write()` writes or overwrites role info, updates name/path/account indexes, rolls back newly written indexes on failure, and records mdlog entries.
- `remove()` resolves by tenant/account/name and removes role info plus indexes.
- `list_tenant()` lists tenant path-index objects and reads each role by id.
- Internal `IndexObj`, `AccountIndex`, `NameIndex`, and `PathIndex` model system-object indexes and cls-user account resource indexes.
- `MetadataHandler` implements `get`, `put`, `remove`, and list operations for metadata type `roles`.

## Control flow
Writes first read existing role info when not exclusive, compare old/new name and path, gather old indexes that should be removed, write a new name object if needed, write a new path/account index, then write the main `roles.{id}` object. If the path or main write fails, it removes newly created indexes. After main write succeeds, old indexes are removed best-effort and mdlog completion is recorded. Removal performs the inverse: read by id, delete the main object with version tracking, delete name and path/account indexes best-effort, then mdlog.

## State and persistence behavior
Persistent objects live in `zone.roles_pool`: `roles.{id}` contains encoded `RGWRoleInfo`, tenant name indexes use `{tenant}role_names.{name}`, account name indexes use `{account}role_names.{lowercase_name}`, and tenant path indexes use `{tenant}role_paths.{path}roles.{id}`. Account roles are also indexed with `rgwrados::roles` in the account roles object. Tags are persisted as a system object attr named `tagging`. Version trackers guard main role objects and index writes generate write versions.

## Dependencies and integration points
Uses `RGWSI_SysObj`, `RGWSI_MDLog`, `RGWMetadataLister`, `RGWMetadataHandler`, `RGWRoleInfo`, `RGWNameToId`, `account::get_roles_obj()`, `rgwrados::roles` account-resource helpers, `librados::Rados`, and string utilities. It integrates with metadata sync via `create_metadata_handler()`.

## Risks and edge cases
Name handling differs for tenant and account roles: account names are lowercased for case-insensitive lookup, tenant names are not. Multi-object writes can leave stale name/path indexes if cleanup fails, though lookup reads the main object afterward. `write()` forbids role id mutation. `list_tenant()` may skip races where path index exists but main object is already deleted. Account path index removal is best-effort and uses role name, so stale account lists may survive partial failures.

## Test signals
Tests should cover exclusive create conflicts, overwrite rename/path changes, rollback when path or main write fails, account-role case-insensitive name lookup, tenant path-prefix listing, tag attr encode/decode, metadata handler put/remove/list, and deletion races during listing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/role.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/role.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/role.h

## Purpose
Declares the RADOS role metadata interface implemented by `role.cc`. It is the public boundary for reading, writing, removing, listing tenant roles, and constructing the metadata handler.

## Important APIs, types, and functions
- `read_by_id()` loads `RGWRoleInfo` by role id with optional mtime, version tracker, and cache info outputs.
- `read_by_name()` resolves tenant/account/name to role info.
- `write()` persists role info and updates name/path indexes, with `exclusive` controlling create-only behavior.
- `remove()` removes a role identified by tenant/account/name.
- `list_tenant()` returns paginated `RGWRoleInfo` entries for tenant roles filtered by path prefix.
- `create_metadata_handler()` returns an `RGWMetadataHandler` for role metadata sync.

## Control flow
The API separates id-based reads from name-based resolution and accepts all service dependencies explicitly: RADOS cluster handle, system object service, mdlog, and zone parameters. Callers provide `optional_yield` for coroutine-friendly RADOS operations.

## State and persistence behavior
The declarations expose optional version/mtime/cache outputs but hide object naming details. `write()` takes a mutable `RGWObjVersionTracker` and mtime, signaling optimistic write/version integration with metadata sync.

## Dependencies and integration points
Forward declares RADOS, metadata, mdlog, sysobj, zone, role info, cache, and account id types. It is used by RGW role administration, IAM-style account role code, and metadata replication.

## Risks and edge cases
Callers must pass the correct tenant/account pair for `read_by_name()` and `remove()`; the implementation stores account names differently from tenant names. `max_items` and path prefix behavior are implementation-defined and should be used consistently by admin list code.

## Test signals
Compile coverage should catch signature drift with `role.cc`; integration tests should exercise each declared operation under tenant and account contexts and verify version tracker propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/role.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/roles.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/roles.cc

## Purpose
Implements account role list/index operations using the `cls_user_account_resource` object class. It stores role names/paths in account resource objects and encodes role ids as per-resource metadata.

## Important APIs, types, and functions
- `add()` builds a `cls_user_account_resource` from `RGWRoleInfo::name` and `path`, encodes `resource_metadata{role_id}`, and calls `cls_user_account_resource_add()`.
- `get()` reads a resource by name and decodes the role id from metadata.
- `remove()` removes a resource by name.
- `list()` lists resources by marker/path prefix and decodes each role id.
- `resource_metadata` supports Ceph encode/decode, JSON dump, and test instances.

## Control flow
Each operation resolves `rgw_raw_obj` to a `rgw_rados_ref`, prepares a librados read or write operation with cls_user helpers, executes through `ref.operate()`, then handles both transport errors and cls return codes.

## State and persistence behavior
State is stored inside a RADOS object using the user/account resource cls schema. The visible resource key is the role name, the sortable/listable path is the role path, and encoded metadata carries the actual role id. Missing list objects are treated as empty lists.

## Dependencies and integration points
Depends on `librados`, `cls/user/cls_user_client.h`, `rgw_sal.h`, `RGWRoleInfo`, and `rgw_get_rados_ref()`. Called from `role.cc` for account role path indexes and from account role listing code.

## Risks and edge cases
Metadata decode failures return `-EIO`, so corrupt account-resource metadata can break get/list. `add()` honors an exclusive flag and limit but leaves conflict/limit semantics to the cls method. List pagination depends on cls-provided `next_marker` and `truncated`.

## Test signals
Tests should cover add/get/remove/list round trips, exclusive duplicate behavior, path-prefix list filtering, missing object list behavior, limit enforcement, and corrupt metadata decode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/roles.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/roles.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/roles.h

## Purpose
Declares account role resource-list helpers and the role-specific metadata payload used by `roles.cc`.

## Important APIs, types, and functions
- `add()`, `get()`, `remove()`, and `list()` operate on a caller-provided `rgw_raw_obj` account resource object.
- `resource_metadata` stores `role_id`, implements Ceph encoding version 1, formatter dump, and test instance generation.

## Control flow
The API is intentionally small: callers supply RADOS, the target object, role/name/list parameters, and yield context. `list()` returns decoded role ids and a next marker.

## State and persistence behavior
Only the metadata schema is declared here. Encoded `role_id` must remain compatible with resources already stored in RADOS account objects.

## Dependencies and integration points
Forward declares RADOS, raw object, role info, and formatter types. It is integrated by `role.cc` and any account role listing implementation needing role ids from account-resource entries.

## Risks and edge cases
Changing `resource_metadata` encoding would affect existing account role indexes. Callers must pass the same object naming convention as account metadata helpers, otherwise indexes fragment.

## Test signals
Encoding round-trip tests for `resource_metadata` and compile-level tests of all helper signatures are the most direct signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/roles.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/shard_io.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/shard_io.h

## Purpose
Provides reusable Boost.Asio coroutine algorithms for concurrent operations across sharded RADOS objects. It supports normal writes, revertible writes with rollback on error/cancellation, and reads that abort outstanding requests on first error.

## Important APIs, types, and functions
- `Result { Success, Retry, Error }` classifies each shard completion.
- Abstract interfaces `RevertibleWriter`, `Writer`, and `Reader` define async operation initiation and completion classification.
- `async_writes(RevertibleWriter&)` applies writes with bounded concurrency and reverts completed writes if a failure or cancellation occurs.
- `async_writes(Writer&)` applies writes with bounded concurrency, retry support, and best-effort completion of other shards after errors.
- `async_reads(Reader&)` issues bounded concurrent reads and terminal-cancels outstanding operations after an error.
- RADOS adapters `RadosRevertibleWriter`, `RadosWriter`, and `RadosReader` convert `prepare_*()` methods into `librados::async_operate()` calls.
- Internal handlers manage intrusive shard lists, cancellation slots, waiter wakeups, and retry/revert scheduling.

## Control flow
Each algorithm converts the input map of shard id to object name into stable `Shard` records and maintains `sending`, `outstanding`, and sometimes `completed` lists. It sends work until `max_concurrent` is reached, awaits a wakeup, then reacts to completions. `on_complete()` returning `Retry` pushes the shard back to `sending`; `Error` records the first failure. Revertible writes move completed shards into a revert send list after failure and switch cancellation handling so only terminal cancellation stops reverts.

## State and persistence behavior
This header does not define a concrete persistent schema, but it executes RADOS object operations prepared by subclasses. Revertible writers are expected to provide inverse operations that restore pre-write state. Cancellation signals are per-shard and forwarded to underlying async RADOS operations through associated cancellation slots.

## Dependencies and integration points
Depends on Boost.Asio composed operations/cancellation/deferred tokens, Boost.Intrusive lists, `librados_asio`, Ceph logging, and RADOS operation types. Consumers subclass the abstract interfaces to implement cls or object operations for sharded RGW metadata/data structures.

## Risks and edge cases
`max_concurrent` must be nonzero; zero would cause the coroutine to wait without outstanding operations. Retry classification can loop forever if callers return `Retry` without backoff or attempt limits. Revert failures are logged but the original failure is returned. The algorithms assume the input map outlives operation initiation because shards hold iterators into it through the composed operation call. Reentrant cancellation handling is carefully staged; changes here are high risk.

## Test signals
Unit tests should use fake Writer/Reader implementations to verify bounded concurrency, retry scheduling, first-error behavior, cancellation propagation, revert ordering, terminal cancellation during revert, empty input, `max_concurrent` limits, and RADOS adapter invocation of `prepare_*()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/shard_io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/sync_fairness.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/sync_fairness.cc

## Purpose
Implements a RADOS watch/notify based fairness protocol for RGW sync shard processing. Each gateway generates random bids per replication log shard, exchanges bids with peers, and processes only shards where it holds the highest known bid.

## Important APIs, types, and functions
- Encoded `BidRequest` and `BidResponse` carry bid vectors.
- `apply_notify_responses()` decodes watch notify replies and timeout lists into a peer bid map.
- `Watcher` owns a librados `watch2()` registration on a control object, creates the object if missing, responds to peer bid notifications, and restarts on watch errors.
- `NotifyCR` wraps `RGWRadosNotifyCR` to broadcast this gateway's bids and feed responses back into the manager.
- `RadosBidManager` implements `BidManager`, `Server`, and `DoutPrefix`; it stores local bids and peer bids under a mutex.
- `create_rados_bid_manager()` returns the concrete manager.

## Control flow
On construction, `RadosBidManager` fills a vector with shard indices and shuffles it, producing a unique bid ordering. `start()` registers the watcher. Incoming notifications decode peer bids, update `all_bids`, and reply with local bids. `notify_cr()` snapshots local bids into a coroutine request; completion decodes responders and timeouts, clears previous peer bids, and installs the latest response set. `is_highest_bidder(index)` compares the local bid against each peer's bid at the same index.

## State and persistence behavior
The durable/control object is only used as a watch/notify rendezvous point in RADOS. Bid state is in memory: `my_bids` and `all_bids`. Peer entries are removed when notify responses report timeouts, and the response path clears all peer bids before applying the latest replies.

## Dependencies and integration points
Depends on librados watch/notify, `RGWRadosNotifyCR`, `rgw::sal::RadosStore`, Ceph encoding, logging, random shuffle, and coroutine macros. It integrates with RGW sync logic through the `BidManager` interface in `sync_fairness.h`.

## Risks and edge cases
`is_highest_bidder()` uses `vector::at()` for local and peer bids, so mismatched shard counts throw exceptions. Clearing `all_bids` on notify response can drop newer bids that raced with the outgoing notify, as noted in the code. Ties favor the local gateway because only strictly greater peer bids win. Watch restart failures close the ioctx. Decode failures return `-EIO` but notification handler only logs bad requests.

## Test signals
Tests should cover bid encode/decode, timeout removal, highest-bid comparison, equal-bid tie behavior, mismatched bid vector size handling, watcher creation when object is absent, notify response races, and restart after watch error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/sync_fairness.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/sync_fairness.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/sync_fairness.h

## Purpose
Declares the sync fairness abstraction used by RGW sync code and the RADOS-backed factory.

## Important APIs, types, and functions
- `BidManager` defines `start()`, `is_highest_bidder(index)`, and `notify_cr()`.
- `create_rados_bid_manager()` constructs a RADOS watch/notify implementation for a given control object and shard count.

## Control flow
Consumers create a bid manager, call `start()` to establish watch state, periodically run the coroutine returned by `notify_cr()`, and gate shard work with `is_highest_bidder()`.

## State and persistence behavior
The interface hides all state. Implementations may keep bid maps in memory and use a RADOS object for peer notification.

## Dependencies and integration points
Forward declares `RadosStore`, `rgw_raw_obj`, and `RGWCoroutine`. It is integrated by RGW multisite sync scheduling code that needs distributed shard ownership fairness.

## Risks and edge cases
The interface does not specify exception behavior for invalid shard indexes or ownership when no notify exchange has completed. Callers need to handle `start()` failures and coroutine ownership of the raw pointer returned by `notify_cr()`.

## Test signals
Mock implementations can test sync scheduler behavior; RADOS implementation tests should validate factory construction and lifecycle through the declared interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/sync_fairness.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/topic.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/topic.cc

## Purpose
Implements v2 pubsub topic metadata storage in RADOS, including read/write/remove, bucket links per topic, account topic indexes, persistent notification queue setup/removal, cache integration, and metadata sync handling.

## Important APIs, types, and functions
- `read()` loads a topic by metadata key from `topic.{key}` in `zone.topics_pool`, using `RGWChainedCacheImpl<cache_entry>` when possible.
- `write()` stores encoded `rgw_pubsub_topic`, links account-owned topics through `rgwrados::topics::add()`, and records mdlog completion.
- `remove()` deletes topic info, deletes the related `buckets.{key}` omap object, unlinks account topics, and records mdlog.
- `link_bucket()`, `unlink_bucket()`, and `list_buckets()` maintain an omap set of bucket keys associated with a topic.
- `MetadataHandler` implements metadata sync type `topic`, including persistent queue creation/deletion for persistent push topics.

## Control flow
Read first checks chained cache; on miss it reads the system object, decodes, stores cache entry with cache invalidation metadata, and returns optional mtime/version data. Write encodes the topic, writes the main object, optionally adds account index, then completes mdlog. Metadata `put()` calls write and then ensures persistent queues exist when required. Metadata `remove()` reads the topic to discover destination properties, removes topic metadata, and then best-effort removes persistent queues.

## State and persistence behavior
Topic info is stored in `zone.topics_pool` under `topic.{metadata_key}`. Bucket associations are stored as omap keys in `buckets.{metadata_key}`. Account topic indexes use `account::get_topics_obj()` with `rgwrados::topics`. Persistent queues are stored in `zone.notif_pool` through `rgw::notify`. Read caching uses `RGWChainedCacheImpl<cache_entry>` and `RGWSI_SysObj_Cache`.

## Dependencies and integration points
Depends on RGW pubsub structures, account helpers, notification queue helpers, metadata services, system object cache, RADOS refs, mdlog, zone params, and `topics.cc` account-topic helpers. It integrates with bucket notification APIs and multisite metadata replication.

## Risks and edge cases
Account link/unlink failures are logged and non-fatal, risking stale or missing account topic lists. Deleting the buckets object is also non-fatal. Persistent queue cleanup failures other than `-ENOENT` are logged but not fatal during metadata remove. Cache returns move object/version data out of the cache entry copy; cache semantics must ensure this is safe. `mutate()` is unsupported.

## Test signals
Tests should cover cached and uncached reads, exclusive write conflicts, account-owned topic link/unlink, bucket link/unlink/list pagination, missing buckets object listing, persistent queue create/remove during metadata sync, mdlog completion, and corrupt topic decode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/topic.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/topic.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/topic.h

## Purpose
Declares the RADOS v2 topic metadata interface and cache entry type used by `topic.cc`.

## Important APIs, types, and functions
- `cache_entry` stores topic info, object version tracker, and mtime.
- `read()`, `write()`, and `remove()` manage topic metadata.
- `link_bucket()`, `unlink_bucket()`, and `list_buckets()` manage bucket membership for a topic.
- `create_metadata_handler()` constructs the metadata sync handler.

## Control flow
Callers provide sysobj/cache/mdlog/RADOS/zone dependencies explicitly and pass topic metadata keys rather than raw object names. Bucket association APIs operate by topic key plus bucket key and support marker-based listing.

## State and persistence behavior
The header exposes that topic reads can return mtime/version and use a chained cache, while writes/removes use version trackers and mdlog.

## Dependencies and integration points
Includes RADOS forwards, Ceph time, and `rgw_pubsub.h`; forward declares metadata, sysobj/cache, zone, and chained cache types. It is consumed by pubsub admin paths, bucket notification code, account topic listing, and metadata sync.

## Risks and edge cases
Callers must pass canonical topic metadata keys from `get_topic_metadata_key()` or reads/writes will target different objects. `list_buckets()` max and marker behavior depends on RADOS omap ordering.

## Test signals
Compile tests plus integration tests should cover all declared APIs with a real or mocked sysobj/RADOS layer and chained cache.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/topic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/topic_migration.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/topic_migration.cc

## Purpose
Migrates legacy v1 pubsub topic and bucket notification metadata to the v2 metadata layout introduced for the Squid release once the notification_v2 feature is enabled.

## Important APIs, types, and functions
- `deconstruct_topics_oid()` parses legacy bucket notification oids of the form `pubsub.{tenant}.bucket.{name}/{marker}`.
- `migrate_notification()` migrates one bucket notification object into the bucket's `RGW_ATTR_BUCKET_NOTIFICATION` attr, merging with existing v2 notification config and then removing the v1 object.
- `migrate_topics()` migrates one tenant topics object into v2 topic metadata through `driver->write_topic_v2()` and then removes the v1 tenant topics object.
- Public `migrate()` lists legacy `pubsub.` objects from the log pool, migrates bucket notifications first, then tenant topic objects.

## Control flow
`migrate()` initializes an ioctx on the zone log pool and pages through objects with the legacy pubsub prefix. Objects containing the bucket infix are migrated immediately; other topic oids are queued and migrated after all bucket notifications. Bucket notification migration reads v1 topics through `RadosBucket::read_topics()`, loads the bucket by tenant/name/marker, merges topics into existing v2 attrs, retries attr storage up to 15 times on `-ECANCELED`, then deletes the v1 object. Tenant topic migration reads v1 topics, skips auto-generated topics where `topic.name != topic.dest.arn_topic`, writes v2 topics exclusively, tolerates `-EEXIST`, then removes v1 topics.

## State and persistence behavior
Reads legacy metadata from the zone log pool and bucket topic objects. Writes v2 bucket notification state into bucket instance attrs under `RGW_ATTR_BUCKET_NOTIFICATION`; writes v2 topic objects via the driver. Deletes v1 bucket/tenant topic objects with version trackers so repeated runs become mostly idempotent.

## Dependencies and integration points
Depends on `RadosStore`, `RadosBucket`, zone service, RADOS pool listing, pubsub structures, cluster log warnings, bucket attr merge/store, and v2 topic writer/remover driver methods. It is intended to run during gateway startup feature migration.

## Risks and edge cases
Parsing is strict and logs cluster warnings on unexpected oid shapes. Migration can be partial: some bucket notifications or topics may migrate before a later error aborts. The bucket attr merge does not override existing v2 topics with the same keys. If the bucket is deleted or marker changes, migration skips directly to deleting the legacy object. After 15 `-ECANCELED` retries it returns the error for a later retry. In `migrate()`, per-object errors are logged but the loop continues and later topic migration overwrites `r`; final return is always 0 after the loops, so some individual failures may not propagate.

## Test signals
Tests should cover oid parsing, empty v1 notifications, merge with existing v2 attrs, deleted bucket, marker mismatch, repeated `-ECANCELED`, corrupt v2 attr decode, tenant topic skip for generated topics, exclusive v2 topic conflict, removal idempotence, listing pagination, and failure propagation expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/topic_migration.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/topic_migration.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/topic_migration.h

## Purpose
Declares the startup migration entry point for converting v1 pubsub topic/notification metadata to v2 format.

## Important APIs, types, and functions
- `migrate(const DoutPrefixProvider*, rgw::sal::RadosStore*, boost::asio::io_context&, boost::asio::yield_context)` runs the migration.

## Control flow
The declaration indicates coroutine/yield-based execution under Boost.Asio. Callers supply the RADOS store and logging prefix; the io context parameter is currently part of the API boundary.

## State and persistence behavior
The header documents that this migration is tied to enabling notification_v2 and runs on startup. Concrete state movement is implemented in `topic_migration.cc`.

## Dependencies and integration points
Includes Boost.Asio io_context/spawn and forward declares `RadosStore`. Used by RGW RADOS initialization code that gates feature migrations.

## Risks and edge cases
Callers need to ensure the migration runs only when the feature transition requires it and that repeated startup invocations are acceptable. API exposes a raw store pointer and coroutine yield context, so lifetime must exceed migration.

## Test signals
Integration tests should invoke this declared entry point with fixture legacy metadata and verify idempotent completion across repeated startup-style calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/topic_migration.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/topics.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/topics.cc

## Purpose
Implements account topic list/index operations using the `cls_user_account_resource` object class. Unlike roles/users, only topic names are stored; no extra metadata payload is encoded.

## Important APIs, types, and functions
- `add()` inserts a `cls_user_account_resource` with `resource.name = topic.name`.
- `remove()` removes an account topic resource by name.
- `list()` pages topic resources and returns names plus next marker.

## Control flow
Each function resolves the target raw object to a RADOS ref, creates an object-class operation, executes through `ref.operate()`, and handles RADOS and cls return codes. Listing treats `-ENOENT` as an empty list.

## State and persistence behavior
Account topic membership is stored in caller-provided account topic resource objects, typically from `account::get_topics_obj()`. Resource names are topic names; path prefix is unused for list.

## Dependencies and integration points
Depends on `librados`, `cls_user_account_resource_*`, `rgw_pubsub_topic`, `rgw_sal.h`, and RADOS ref helpers. Called by `topic.cc` when account-owned topics are written or removed and by account topic list paths.

## Risks and edge cases
No metadata is stored, so lookup by id is not supported here. Duplicate behavior and limits are delegated to cls add. Listing order and pagination follow cls resource ordering. Missing account topic objects appear as empty lists, which can hide index-loss failures.

## Test signals
Tests should cover add/list/remove, duplicate exclusive behavior, limit handling, missing object list, and pagination next marker clearing when not truncated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/topics.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/topics.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/topics.h

## Purpose
Declares account topic list helpers implemented by `topics.cc`.

## Important APIs, types, and functions
- `add()` inserts a topic into an account topic resource object with exclusivity and limit controls.
- `remove()` removes a topic name.
- `list()` returns paginated topic names and a next marker.

## Control flow
The API takes explicit RADOS, raw object, marker, and max item parameters. It is intentionally resource-object oriented and does not know account ids directly.

## State and persistence behavior
Persistent state is the account topic resource object selected by the caller. The header does not define additional encoding beyond resource names.

## Dependencies and integration points
Forward declares RADOS, raw object, topic, and yield/logging types. It is consumed by topic metadata and account APIs.

## Risks and edge cases
Callers must choose stable object names and consistent topic names. Since the interface has no `get()`, callers needing existence must infer from add/list/remove behavior.

## Test signals
Compile and integration tests should validate that declared list pagination and add/remove signatures match account topic behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/topics.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/users.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/users.cc

## Purpose
Implements account user list/index operations using the `cls_user_account_resource` object class. It maps display names and paths to encoded user ids for account-scoped user listing and lookup.

## Important APIs, types, and functions
- `add()` builds a resource from `RGWUserInfo::display_name` and `path`, encodes `resource_metadata{user_id}`, and inserts it with optional exclusivity/limit.
- `get()` reads a resource by display name and decodes the stored user id.
- `remove()` removes a resource by name.
- `list()` lists resources by marker/path prefix and decodes user ids.
- `resource_metadata` encodes/decodes a single `user_id` string and supports formatter dump/test instances.

## Control flow
The functions mirror `roles.cc`: resolve RADOS ref, prepare cls read/write operation, execute, check both operation and cls ret code, then decode metadata for get/list.

## State and persistence behavior
Account user resources are stored in a caller-provided raw object. The resource name is display name, path is user path, and metadata stores canonical user id. Missing list objects are treated as empty lists.

## Dependencies and integration points
Depends on `librados`, `cls/user/cls_user_client.h`, `RGWUserInfo`, `rgw_common.h`, and `rgw_sal.h`. It integrates with account IAM-style user management and any code that lists users under an account.

## Risks and edge cases
Display name is used as the resource name, so rename/display-name changes must update this index elsewhere. Decode corruption returns `-EIO`. Listing by path prefix depends on the path stored during add. A typo leaves a double semicolon in test instance construction but has no behavior impact.

## Test signals
Tests should cover add/get/remove/list, path-prefix filtering, display-name duplicate conflicts, missing object listing, corrupt metadata decode, and user id encoding compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/users.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/users.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/users.h

## Purpose
Declares account user resource-list helpers and the user-specific metadata payload used by `users.cc`.

## Important APIs, types, and functions
- `add()`, `get()`, `remove()`, and `list()` operate on a caller-provided account resource object.
- `resource_metadata` stores `user_id`, implements Ceph encoding version 1, formatter dump, and test instance generation.

## Control flow
Callers supply RADOS, raw object, user/name/list parameters, and yield context. `get()` resolves a name to a user id and `list()` returns decoded ids.

## State and persistence behavior
The encoded `resource_metadata` is part of the durable account user index schema. It must remain compatible with existing RADOS resource objects.

## Dependencies and integration points
Forward declares RADOS, raw object, user info, formatter, and yield/logging types. Used by account user management and possibly IAM-style list APIs.

## Risks and edge cases
Changing the encoded structure or resource naming convention would orphan existing account user indexes. Callers must keep display name/path updates synchronized with add/remove.

## Test signals
Encoding round-trip tests and account user resource integration tests are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/users.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/jwt-cpp/base.h -->
# sources/distributed-fs/ceph/src/rgw/jwt-cpp/base.h

## Purpose
Provides a small header-only base64/base64url encoder and decoder used by the embedded `jwt-cpp` code. It defines alphabets and templated public encode/decode entry points over a common implementation.

## Important APIs, types, and functions
- `jwt::alphabet::base64` exposes the standard `A-Z a-z 0-9 + /` alphabet and `=` fill string.
- `jwt::alphabet::base64url` exposes the URL-safe `A-Z a-z 0-9 - _` alphabet and `%3d` fill string.
- `jwt::base::encode<T>()` encodes binary strings with alphabet `T`.
- `jwt::base::decode<T>()` decodes strings with alphabet `T` and validates padding.

## Control flow
Encoding processes complete 3-byte groups into four sextets, then handles 1- or 2-byte tails by emitting fill strings. Decoding strips up to two trailing fill strings, validates total group length, decodes complete 4-character groups with a linear alphabet lookup, and handles the final padded group according to fill count.

## State and persistence behavior
No persistent state exists. Alphabet arrays and fill strings are function-local statics shared for the process lifetime.

## Dependencies and integration points
Depends only on `<string>` and `<array>` in this file, but throws `std::runtime_error` without including `<stdexcept>` locally, so inclusion may rely on transitive headers. Used by JWT token encoding/decoding paths in RGW.

## Risks and edge cases
`base64url::fill()` uses the percent-encoded string `%3d` rather than raw `=`, so interoperability depends on callers expecting URL-encoded padding. Decoder rejects more than two fill strings and invalid lengths. Alphabet lookup is O(64) per character. Decode output size reserve does not include padded tail bytes, but string growth handles it. Missing `<stdexcept>` is a compile fragility if transitive includes change.

## Test signals
Tests should cover RFC base64 vectors, base64url vectors with `%3d` padding, invalid characters, invalid length, excessive fill, empty string, 1- and 2-byte tails, binary bytes with high bits set, and compile isolation of this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/jwt-cpp/base.h -->
