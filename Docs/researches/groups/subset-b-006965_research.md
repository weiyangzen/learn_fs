# subset-b-006965

Grouped research for RGW RADOS driver account, bucket/account-resource, multisite config, OIDC, and bucket-logging persistence files.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/account.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/account.cc

Purpose: Implements RADOS-backed account metadata storage for RGW. It stores the primary `RGWAccountInfo` object in `zone.account_pool`, secondary redirect objects for account name and email lookup, resource-index object names for buckets/users/groups/roles/topics/OIDC providers, and the RGW metadata-handler adapter for metadata sync/list/get/put/remove.

Important APIs/types/functions: `get_*_obj()` returns well-known account-scoped cls_user resource objects. `RedirectObj` wraps a redirect object, target `RGWUID`, and `RGWObjVersionTracker`. `read()`, `read_by_name()`, and `read_by_email()` decode `RGWAccountInfo`; email lookup also rejects redirect ids that are not account ids. `write()` writes the account object and updates name/email redirects. `remove()` deletes account, redirect, and users objects. `resource_count()` decodes `cls_user_account_header` from an account-resource omap header. `MetadataHandler` exposes the `"account"` metadata type.

Control flow: Reads resolve a concrete object id, call `rgw_get_system_obj()`, decode, and verify the id matches the requested account id. Writes first compare `old_info` to the new info, read old redirects that may need removal, check that new name/email redirects are not already claimed, write the primary account object with requested exclusivity/versioning, then best-effort remove old redirects and create new redirects. Metadata put reads prior state, tolerates `-ENOENT`, and calls the same write path with nonexclusive overwrite.

State/persistence: Primary objects use keys `account.<id>`. Name redirect keys are `name.<tenant>$<name>` in `account_pool`; email redirect keys are lower-cased email addresses in `user_email_pool`, intentionally sharing that pool with user email indexes to enforce global uniqueness. Resource-list objects use `buckets.<id>`, `users.<id>`, `groups.<id>`, `roles.<id>`, `topics.<id>`, and `oidcs.<id>`. Writes to secondary redirect/index objects after the primary account write are non-fatal, so stale or missing lookup indexes are possible after partial failure.

Dependencies/integration: Uses `RGWSI_SysObj` system-object helpers, `RGWZoneParams` pool layout, `RGWObjVersionTracker`, RGW metadata sync interfaces, `cls_user` account-resource headers, account-id validation, and boost case-insensitive email/name handling. Other files use its resource-object helpers for account bucket/group/OIDC listings.

Risks: Multi-object updates are not atomic. A successful account write can leave old redirects, miss new redirects, or leave email/name indexes inconsistent. Email object namespace collides with user email indexes by design, so account-id validation is required on reads. Remove logs but ignores cleanup failures for secondary objects. Decode failures and id mismatch return `-EIO`, which is appropriate but indicates corrupt metadata.

Test signals: Cover create/update with name and email conflict (`-EEXIST`), rename/email-change cleanup, case-insensitive email reads, metadata sync put/remove id validation, missing index cleanup behavior, and `resource_count()` on missing, empty-header, and corrupt-header cls_user objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/account.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/account.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/account.h

Purpose: Declares the account RADOS persistence API used by RGW services and metadata sync. The header exposes account metadata CRUD, name/email lookup, resource-index object lookup, account resource count reading, and the account metadata handler factory.

Important APIs/types/functions: `create_metadata_handler()` creates the `"account"` RGW metadata handler. `get_buckets_obj()`, `get_users_obj()`, `get_groups_obj()`, `get_roles_obj()`, `get_topics_obj()`, and `get_oidcs_obj()` return `rgw_raw_obj` locations for account-scoped cls_user resource indexes. `read()`, `read_by_name()`, `read_by_email()`, `write()`, `remove()`, and `resource_count()` are the public entry points.

Control flow: Callers supply `DoutPrefixProvider`, `optional_yield`, `RGWSI_SysObj`, zone pools, and version trackers. The interface makes old account info explicit on writes so implementations can update secondary indexes safely relative to previous state.

State/persistence: The API is explicitly pool/object oriented through `rgw_raw_obj` and zone parameters. `write()` includes attrs, mtime, exclusivity, and objv so metadata sync and admin operations can preserve object metadata and concurrency semantics.

Dependencies/integration: Forward declarations keep compile dependencies low while coupling to RGW account info, bucket info, storage stats, metadata handler, sysobj, zone params, and librados. The resource-object helpers are integration points for bucket, group, role, topic, and OIDC listing modules.

Risks: The contract assumes callers pass an accurate `old_info` when updating mutable secondary-indexed fields. Passing null or stale old state can leave redirects or account-resource indexes inconsistent. The header does not document ownership/atomicity limits of multi-object writes, so users must know implementation behavior.

Test signals: Compile/link consumers against the declared API; exercise callers that use each `get_*_obj()` with cls_user helpers; verify metadata sync passes attrs/mtime/objv through `write()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/account.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/buckets.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/buckets.cc

Purpose: Implements bucket-list and bucket-stat operations for owners backed by the `cls_user` object class. The same helpers can manage bucket lists for users or accounts, depending on the `rgw_raw_obj` passed by the caller.

Important APIs/types/functions: Internal `set()` wraps `cls_user_set_buckets()`. `add()` converts `rgw_bucket` to `cls_user_bucket_entry` and sets creation time. `remove()` calls `cls_user_remove_bucket()`. `list()` pages through `cls_user_bucket_list()`. `write_stats()` updates an existing bucket entry. `read_stats()` and `read_stats_async()` read owner aggregate stats. `reset_stats()` loops over `reset_user_stats2` until not truncated. `complete_flush_stats()` marks stats sync complete.

Control flow: Most operations first resolve `rgw_raw_obj` to `rgw_rados_ref`, build an object-class read/write operation, and call `ref.operate()`. Listing repeatedly requests remaining capacity until the cls call is not truncated or `max` entries are collected, then sets `next_marker` only when more data remains.

State/persistence: State lives in cls_user omap entries and headers on the owner object. `add()` can create/update bucket entries; `write_stats()` passes `add=false`, so the bucket must already exist. Missing owner objects are treated as empty for list and stats reads. Reset recalculates aggregate stats over potentially truncated batches.

Dependencies/integration: Depends on librados, `cls/user/cls_user_client.h`, RGW bucket conversion, SAL `BucketList` and `ReadStatsCB`, `RGWStorageStats`, and `rgw_get_rados_ref()`. Account and user code provide the actual owner object.

Risks: `list()` computes `max - listing.buckets.size()`; callers should avoid passing `max=0` unless cls behavior is known. Async callback ownership depends on `headercb.release()` only after successful registration. `reset_stats()` returns the last cls return value and treats decode failure as `-EINVAL`; tests should ensure truncated loops converge.

Test signals: Add/remove/list pagination, empty owner object behavior, `write_stats()` on missing bucket, aggregate stats read including timestamps, async callback result propagation, reset over multiple truncated batches, and complete-flush timestamp updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/buckets.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/buckets.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/buckets.h

Purpose: Declares the generic owner-bucket cls_user interface used by user/account ownership code to maintain bucket listings and aggregate storage stats.

Important APIs/types/functions: `add()`, `remove()`, `list()`, `write_stats()`, `read_stats()`, `read_stats_async()`, `reset_stats()`, and `complete_flush_stats()` form a thin RADOS object-class API around a supplied `rgw_raw_obj`.

Control flow: The header makes all operations asynchronous-yield aware through `optional_yield`, except the callback-style `read_stats_async()`. Callers control the owner namespace by choosing the raw object and tenant passed to `list()`.

State/persistence: Functions manipulate cls_user bucket entries and header stats on a single RADOS object. `read_stats()` returns aggregate `RGWStorageStats` and optional sync/update timestamps.

Dependencies/integration: Coupled to librados forward declarations, Ceph time, boost intrusive pointer callbacks, `rgw_sal_fwd.h`, `rgw_bucket`, `RGWBucketEnt`, and `RGWStorageStats`.

Risks: The API does not distinguish user and account ownership; passing the wrong object corrupts the wrong owner list. `write_stats()` assumes the bucket entry exists.

Test signals: API consumers should validate correct owner object selection, pagination marker propagation, stats callback lifetime, and behavior against missing owner objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/buckets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/config/impl.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/config/impl.cc

Purpose: Provides the low-level RADOS implementation used by `RadosConfigStore` for realm, period, zonegroup, zone, and period-config metadata. It centralizes pool selection, object read/write/remove, version tracking, and notification.

Important APIs/types/functions: `ConfigImpl::ConfigImpl()` resolves root pools from config with defaults to `rgw.root`. `read()` initializes an ioctx and reads the full object, preparing objv reads when supplied. `write()` applies `Create` semantics (`MustNotExist`, `MayExist`, `MustExist`), prepares object-version assertions, writes full content, and applies the write version. `remove()` does versioned delete. `notify()` sends RADOS notify payloads.

Control flow: Every operation opens an ioctx with `rgw_init_ioctx()`, builds a librados operation, optionally inserts version-tracker assertions, and delegates to `rgw_rados_operate()` or `rgw_rados_notify()`. Successful writes/removes call `objv->apply_write()` to advance local version state.

State/persistence: The class does not define object schemas; it persists already-encoded bufferlists or templated encoded objects into the configured root pools. Pool names are immutable members derived at construction.

Dependencies/integration: Depends on librados, RGW pool initialization helpers, `RGWObjVersionTracker`, `ConfigProxy`, and object encoding. Higher-level config files call it for all RADOS-backed SAL config-store operations.

Risks: Each call initializes a fresh ioctx, so failures in pool configuration surface on every operation. `Create::MayExist` overwrites full objects. Decode failures are handled in the templated header method, not here. Notification timeout handling is delegated to RADOS.

Test signals: Validate default and overridden pool names, create-mode error behavior (`-EEXIST`/`-ENOENT`), version conflict handling (`-ECANCELED`), full-object overwrite semantics, and notify delivery to realm watchers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/config/impl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/config/impl.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/config/impl.h

Purpose: Declares `ConfigImpl`, the shared low-level RADOS utility for the config store, plus create-mode semantics and templated encode/decode/list helpers.

Important APIs/types/functions: `enum class Create` documents create preconditions. `ConfigImpl` owns a librados client and root pools for realms, periods, zonegroups, and zones. Templated `read<T>()` decodes from a bufferlist with `-EIO` on decode error. Templated `write<T>()` encodes data before write. `list()` scans pool object names from a RADOS cursor and applies a caller-supplied oid-to-entry filter.

Control flow: `list()` parses the marker into `librados::ObjectCursor`, iterates `nobjects_begin()` until the output span is full or the pool ends, filters oids, and returns entries as a subspan plus a next cursor string.

State/persistence: The header defines no schema but establishes full-object encoded persistence and object-name listing as the abstraction for all config metadata.

Dependencies/integration: Includes librados, RGW basic types/tools, SAL config interfaces, `std::span`, and C++20 concepts for `std::regular_invocable`. It is included by all config entity implementation files.

Risks: `list()` advances the cursor on every object, including filtered-out ones; callers with sparse prefixes may need repeated calls to fill pages. Bad marker strings return `-EINVAL`. Any exception from object iteration is collapsed to `-EIO`.

Test signals: Unit tests should cover bad markers, sparse filtering, empty pages with nonempty next cursors, decode corruption, and all `Create` modes through the concrete implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/config/impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/config/period.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/config/period.cc

Purpose: Implements period object storage for multisite configuration, including epoch-specific period objects, latest-epoch tracking, deletion, and listing of period ids.

Important APIs/types/functions: `period_oid()` maps period id/epoch to `periods.<id>.<epoch>`, except staging ids ending `:staging` omit epoch. `latest_epoch_oid()` builds the latest-epoch object name. `update_latest_epoch()` atomically advances the latest epoch with retries. `create_period()`, `read_period()`, `delete_period()`, and `list_period_ids()` implement the SAL config-store period API.

Control flow: `read_period()` reads latest epoch first when no epoch is supplied, then reads the period object. `update_latest_epoch()` loops up to 20 times, reading current latest, rejecting non-increasing epochs with `-EEXIST`, using exclusive create for initial write, and retrying on `-EEXIST` or version conflict. `delete_period()` reads latest epoch, removes epochs from 0 through latest, then removes the latest-epoch object.

State/persistence: Period data lives in `impl->period_pool`. Latest epoch state is encoded `RGWPeriodLatestEpochInfo`; period objects are encoded `RGWPeriod`. Listing period ids scans latest-epoch objects, not period data objects, so a period without latest-epoch metadata is invisible to list.

Dependencies/integration: Uses `RadosConfigStore`, `ConfigImpl`, RGW period types, `RGWObjVersionTracker`, and configurable latest-epoch suffix from Ceph config.

Risks: Deletion assumes epoch range is dense from 0 to latest and treats missing objects as ignorable. Staging period oid behavior differs from normal periods and must not collide with epoch objects. Concurrent latest-epoch updates can fail after retry exhaustion with `-ECANCELED`.

Test signals: Exercise initial latest-epoch create races, non-increasing update rejection, reading explicit vs latest epoch, staging oid behavior, deletion with missing epoch objects, and listing only latest-epoch-backed ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/config/period.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/config/period_config.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/config/period_config.cc

Purpose: Stores and reads `RGWPeriodConfig` objects in the period root pool by realm id, with a default object name when no realm id is supplied.

Important APIs/types/functions: `period_config_oid()` returns `period_config.<realm_id>` or `period_config.default`. `read_period_config()` decodes an `RGWPeriodConfig`. `write_period_config()` writes it with exclusive or overwrite create semantics.

Control flow: Both public methods compute the oid and call `ConfigImpl` against `impl->period_pool`; no secondary indexes or metadata log operations are involved.

State/persistence: Period config is a single encoded object per realm/default under the period pool. Empty realm id aliases to `default`.

Dependencies/integration: Depends on `RGWPeriodConfig`, `RadosConfigStore`, and `ConfigImpl`. It is part of the SAL config-store interface implemented in `store.h`.

Risks: Empty realm id is special and can hide accidental omission of a realm id. There is no version tracker or read-modify-write protection here.

Test signals: Verify default and realm-specific oid selection, exclusive create errors, overwrite behavior, and decode failure on corrupt objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/config/period_config.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/config/realm.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/config/realm.cc

Purpose: Implements RADOS storage for realm metadata, default realm id, realm name lookup, realm writer operations, notification control objects, and realm listing.

Important APIs/types/functions: Realm objects use `realms.<id>`, name indexes use `realms_names.<name>`, control objects use `realms.<id>.control`, and default id uses configured/default `default.realm`. `RadosRealmWriter` implements write/rename/remove with objv. `create_realm()`, `read_realm_by_id()`, `read_realm_by_name()`, `read_default_realm()`, `read_realm_id()`, `realm_notify_new_period()`, and `list_realm_names()` implement the SAL API.

Control flow: Create validates nonempty id/name, writes info, writes name->id, then creates the control object, rolling back prior objects on failure. Rename first creates the new name index exclusively, updates the info object with `MustExist`, removes the new name on failure, then best-effort removes the old name. Remove deletes info with versioning, then best-effort deletes name and control. Notifications encode `ZonesNeedPeriod`, the period, then `Reload`, and notify the realm control object.

State/persistence: Realm state spans info, name index, optional default-id object, and control object in the realm pool. Writer objects capture the objv from read/create to protect later mutations.

Dependencies/integration: Uses `RGWRealm`, `RGWNameToId`, `RGWDefaultSystemMetaObjInfo`, `RGWRealmNotify`, `ConfigImpl`, SAL writer interfaces, and `RadosRealmWatcher` consumers.

Risks: Multi-object create/rename/remove rollback is best effort; stale name indexes or control objects may remain. Rename mutates the caller's `RGWRealm& info` before the final old-name cleanup. Notification payload ordering must match watcher decoding expectations.

Test signals: Validate create rollback at each failure point, rename conflict and rollback, writer id/name immutability checks, default realm read/write/delete, realm notification decode by watcher, and list prefix filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/config/realm.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/config/realm_watcher.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/config/realm_watcher.cc

Purpose: Implements a RADOS watch-backed `RGWRealmWatcher` that listens on a realm control object and dispatches decoded realm notifications to registered watcher handlers.

Important APIs/types/functions: `RadosRealmWatcher` constructor starts the watch unless the realm id is empty. `handle_notify()` acknowledges notifications and decodes a sequence of `RGWRealmNotify` messages from the payload. `handle_error()` restarts the watch. `watch_start()`, `watch_restart()`, and `watch_stop()` manage librados `watch2`/`unwatch2`. `RadosConfigStore::create_realm_watcher()` constructs it.

Control flow: Startup opens an ioctx for `realm.get_pool(cct)`, registers `watch2()` on `realm.get_control_oid()`, and stores the oid/handle. Notifications with nonmatching cookies are ignored; matching notifications are acked then decoded until payload end, dispatching by notification enum. Watch errors trigger unwatch and re-watch on the same oid.

State/persistence: This file does not persist data, but it holds live watcher state: `pool_ctx`, `watch_handle`, and `watch_oid`. The watched object is the control object created by realm storage code.

Dependencies/integration: Depends on librados `WatchCtx2`, `RGWRealmWatcher` base dispatch map, realm pool/control oid helpers, `ConfigImpl`-owned Rados client, and RADOS notify payloads emitted by `realm_notify_new_period()`.

Risks: Startup failures call `rados.shutdown()` on the shared client in some paths, which is sensitive if the client is used elsewhere. Dispatch stops at the first unknown notification. Restart clears the watch on failure and does not schedule later retries. Notify ack errors are ignored.

Test signals: Cover empty realm id disabling, successful watch/notify dispatch, unknown notify handling, corrupt payload decode, cookie mismatch, watch restart success/failure, and shutdown unwatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/config/realm_watcher.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/config/realm_watcher.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/config/realm_watcher.h

Purpose: Declares the RADOS-specific realm watcher type used by the config store for dynamic RGW realm reconfiguration.

Important APIs/types/functions: `RadosRealmWatcher` derives from `RGWRealmWatcher` and `librados::WatchCtx2`. Public overrides are `handle_notify()` and `handle_error()`. Private helpers are `watch_start()`, `watch_restart()`, and `watch_stop()`.

Control flow: Construction receives a `DoutPrefixProvider`, `CephContext`, librados client, and realm. The class stores one ioctx, watch handle, and oid, and the destructor stops the watch.

State/persistence: The class is live state only; it watches a persistent realm control object but does not encode or write metadata itself.

Dependencies/integration: Includes `rgw_realm_watcher.h` and librados. It is constructed from `RadosConfigStore` and receives notifications emitted by realm config writes.

Risks: The class owns watch lifecycle but not the Rados client. Lifetime ordering must ensure the shared Rados client and `CephContext` outlive the watcher.

Test signals: Compile-time interface compatibility with `WatchCtx2`; runtime tests for destructor cleanup and callback dispatch through the base watcher registry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/config/realm_watcher.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/config/store.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/config/store.cc

Purpose: Provides construction and destruction for `RadosConfigStore`, including initialization of the underlying librados client used by all config-store operations.

Important APIs/types/functions: `RadosConfigStore::RadosConfigStore()` stores a `unique_ptr<ConfigImpl>`. The destructor is defaulted. `create_config_store()` allocates `ConfigImpl`, calls `rados.init_with_context()`, connects, and returns the store or null on failure.

Control flow: Factory reads config from `dpp->get_cct()`, initializes the client, logs connection failures, and only exposes a store after a successful `rados.connect()`.

State/persistence: The file does not write config objects directly. It establishes the long-lived librados connection held by `ConfigImpl` and later used for realm/period/zone operations and watchers.

Dependencies/integration: Depends on librados, `ConfigImpl`, `store.h`, `DoutPrefixProvider`, and Ceph error formatting.

Risks: On `connect()` failure after successful init, the partially initialized `ConfigImpl` is destroyed; callers must handle null. There is no retry/backoff in the factory.

Test signals: Simulate init/connect failures, verify null return and logging, and verify a successful store can perform subsequent config operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/config/store.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/config/store.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/config/store.h

Purpose: Declares `RadosConfigStore`, the RADOS-backed implementation of `sal::ConfigStore` for RGW multisite realms, periods, zonegroups, zones, period config, and realm watchers.

Important APIs/types/functions: The class overrides default-id read/write/delete for realms, zonegroups, and zones; create/read/list operations for realms, periods, zonegroups, and zones; writer factory returns through SAL writer pointers; `realm_notify_new_period()` and `create_realm_watcher()` handle dynamic reconfiguration; `read_period_config()` and `write_period_config()` handle period config. `create_config_store()` is the factory.

Control flow: The header defines the high-level SAL contract; implementation is split across entity-specific `.cc` files that share one private `ConfigImpl`.

State/persistence: All persistent state is behind `ConfigImpl` and stored in configured RADOS root pools. The class owns exactly one `unique_ptr<ConfigImpl>`.

Dependencies/integration: Includes `rgw_common.h` and `rgw_sal_config.h`, tying this implementation to SAL config abstractions and RGW metadata types such as `RGWRealm`, `RGWPeriod`, `RGWZoneGroup`, `RGWZoneParams`, and `RGWPeriodConfig`.

Risks: Because implementation is distributed across many files, interface changes in `sal::ConfigStore` require synchronized updates. The class exposes multi-object entity operations that are only partially transactional in implementations.

Test signals: Compile all overrides against SAL, exercise each factory/writer path through the interface, and verify persistence layout with integration tests against a RADOS cluster or mock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/config/store.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/config/zone.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/config/zone.cc

Purpose: Implements RADOS storage for zone parameters, default zone id per realm, zone name lookup, zone writer operations, and zone name listing.

Important APIs/types/functions: Zone info oids are `zone_info.<id>`, name oids are `zone_names.<name>`, and default-zone oids are `<rgw_default_zone_info_oid>.<realm_id>`. `RadosZoneWriter` implements versioned write/rename/remove. Public methods include `write_default_zone_id()`, `read_default_zone_id()`, `delete_default_zone_id()`, `create_zone()`, `read_zone_by_id()`, `read_zone_by_name()`, `read_default_zone()`, and `list_zone_names()`.

Control flow: Create validates id/name, writes info, writes name index, and rolls back info on name failure. Writer `write()` rejects direct id/name changes. Rename creates the new name exclusively, updates the info object, removes the new name on update failure, then best-effort removes the old name. Reads by name/default resolve id first, then read info with objv for writer creation.

State/persistence: Zone metadata spans info, name index, and realm-scoped default id objects in `impl->zone_pool`. Writer instances carry the version tracker from the info read/create.

Dependencies/integration: Uses `RGWZoneParams`, `RGWNameToId`, `RGWDefaultSystemMetaObjInfo`, SAL `ZoneWriter`, `ConfigImpl`, and Ceph config default oid settings.

Risks: `default_zone_oid()` formats `conf->rgw_default_zone_info_oid` directly; unlike zonegroup/realm, it does not call `name_or_default()`, so empty config would produce `.realm`. Multi-object update rollback is best effort and can leave stale name indexes.

Test signals: Validate default oid construction, create rollback, rename conflict/rollback, writer immutability, default-zone lookup by realm, and list prefix filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/config/zone.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/config/zonegroup.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/config/zonegroup.cc

Purpose: Implements RADOS storage for zonegroup metadata, default zonegroup id per realm, zonegroup name lookup, writer operations, and name listing.

Important APIs/types/functions: Zonegroup info oids are `zonegroup_info.<id>`, names are `zonegroups_names.<name>`, and default objects are `<default.zonegroup or configured prefix>.<realm_id>`. `RadosZoneGroupWriter` provides versioned write/rename/remove. Public methods include default-id CRUD, create/read by id/name/default, and `list_zonegroup_names()`.

Control flow: Create validates id/name, writes info, writes name index, and removes info on name failure. Rename creates the new name index first, updates info with `MustExist`, rolls back new name on failure, then best-effort removes old name. Remove deletes info with objv then best-effort deletes name.

State/persistence: State lives in `impl->zonegroup_pool` across info object, name index, and realm-scoped default object. Writer objects remember id/name and objv to guard subsequent mutations.

Dependencies/integration: Uses `RGWZoneGroup`, `RGWNameToId`, `RGWDefaultSystemMetaObjInfo`, SAL `ZoneGroupWriter`, `ConfigImpl`, and config option `rgw_default_zonegroup_info_oid`.

Risks: Multi-object operations can leave stale name/default indexes. Rename mutates caller state before old-name cleanup. Listing scans all pool objects and filters by prefix, so sparse pools may require repeated calls.

Test signals: Exercise create exclusive conflicts, rollback on name write failure, rename to existing name, remove cleanup, default zonegroup per realm, and paginated listing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/config/zonegroup.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/group.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/group.cc

Purpose: Implements RADOS-backed IAM/group metadata for RGW, including primary group info objects, case-insensitive account/name indexes, per-group user resource objects, account group-list linkage, and the RGW metadata handler.

Important APIs/types/functions: Group info keys are `info.<group_id>`, name keys are `name.<account_id>$<lower_name>`, and per-group user-list keys are `users.<group_id>`. `NameObj` is the redirect equivalent. `read()`, `read_by_name()`, `write()`, and `remove()` are the main CRUD APIs. `create_metadata_handler()` returns the `"group"` metadata handler.

Control flow: Reads decode and verify `RGWGroupInfo.id`. Writes compare `old_info`, read old name object for removal, check new name uniqueness, write the primary group object, then best-effort remove old name/account-list entry and write new name/account-list entry. Removes delete the primary object first, then best-effort delete name, per-group users object, and account group-list entry. Metadata put mirrors account handling by reading old state and calling `write()` nonexclusively.

State/persistence: Group metadata lives in `zone.group_pool`; account linkage uses `account::get_groups_obj()` and `groups::add/remove()` in the account pool/account object. Name matching is lower-cased, giving case-insensitive names per account.

Dependencies/integration: Depends on `RGWSI_SysObj`, librados, account resource object helpers, `groups.cc` cls_user account-resource helpers, RGW metadata sync, `RGWGroupInfo`, and boost lowercase conversion.

Risks: Account linkage and name redirects are not atomic with primary group writes. Failures linking/unlinking account lists are logged but non-fatal, so list-by-account may diverge from group objects. The remove error message says "account obj" for a group object, which may confuse logs.

Test signals: Create/update/remove with name changes, case-insensitive name conflicts, account group list consistency, metadata sync put/remove, missing secondary object cleanup, and corrupt decode/id mismatch handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/group.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/group.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/group.h

Purpose: Declares the RADOS-backed group metadata API and metadata-handler factory.

Important APIs/types/functions: `create_metadata_handler()` creates the group metadata handler. `get_users_obj()` returns the per-group user-list object. `read()`, `read_by_name()`, `write()`, and `remove()` expose group CRUD with attrs, mtime, version tracking, sysobj, rados, and zone parameters.

Control flow: The API requires both `RGWSI_SysObj` and `librados::Rados` for writes/removes because group updates touch system objects and cls_user account-resource indexes.

State/persistence: The contract covers primary group info, name lookup, and per-group user tracking in `zone.group_pool`, plus account group listing through implementation dependencies.

Dependencies/integration: Forward declares RGW group info, metadata handler, objv, sysobj, zone params, and librados. Includes buffer and time types for attrs/mtime.

Risks: Callers must pass correct old group state for update operations and the correct Rados client for cls_user linkage; mistakes can leave indexes stale.

Test signals: Compile consumers, verify metadata-handler registration, and run integration tests for account group listings after group create/update/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/group.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/groups.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/groups.cc

Purpose: Implements account-scoped group listing helpers using the `cls_user_account_resource` object-class API.

Important APIs/types/functions: `add()` encodes `resource_metadata{group_id}` into a cls resource named by group name with path from `RGWGroupInfo`. `remove()` removes a resource by name. `list()` pages resource entries by marker/path prefix and returns decoded group ids. `resource_metadata::dump()` and `generate_test_instances()` support JSON/encoding tests.

Control flow: Each operation resolves the supplied `rgw_raw_obj` to `rgw_rados_ref`, builds a cls_user account-resource op, and operates on the object. Listing treats missing objects as empty, decodes metadata for each returned entry, and clears `next_marker` when not truncated.

State/persistence: Group references are stored as cls_user account resources on an account's groups object, usually from `account::get_groups_obj()`. The resource name is the group name; encoded metadata carries the stable group id.

Dependencies/integration: Depends on librados, `cls/user/cls_user_client.h`, `RGWGroupInfo`, SAL forward types, and Ceph encoding/JSON helpers. `group.cc` calls these helpers when linking groups to accounts.

Risks: Since removal is by name, stale resources can remain if old names are not removed during rename. Decode failure in metadata aborts listing with `-EIO`. The `exclusive` and `limit` parameters are delegated to cls_user and need caller-chosen semantics.

Test signals: Add/remove/list pagination, path-prefix filtering, limit enforcement, missing object as empty list, corrupt resource metadata, and rename cleanup through `group.cc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/groups.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/groups.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/groups.h

Purpose: Declares account group-list helper APIs and the encoded metadata payload stored with each cls_user account resource.

Important APIs/types/functions: `add()`, `remove()`, and `list()` manipulate group resources on a supplied `rgw_raw_obj`. `resource_metadata` encodes/decodes `group_id`, dumps JSON, and has test instances; `WRITE_CLASS_ENCODER` registers encoding helpers.

Control flow: Callers provide marker/path-prefix/max for paginated listing and receive ids plus `next_marker`.

State/persistence: The metadata schema is versioned with `ENCODE_START(1, 1)` and stores only `group_id`; the cls_user resource itself stores name/path.

Dependencies/integration: Uses librados forward declarations, Ceph encoding, SAL forward declarations, `DoutPrefixProvider`, and `RGWGroupInfo`.

Risks: Schema currently stores minimal metadata; future list consumers needing more fields require versioned changes. Remove-by-name inherits rename consistency risks.

Test signals: Encoder round-trip, JSON dump, generated test instances, and API consumers preserving pagination markers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/groups.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/oidc.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/oidc.cc

Purpose: Implements RADOS-backed OIDC provider metadata for RGW, including provider object CRUD, tenant/account listing, account-resource linkage, metadata sync handler, and metadata-key conversion.

Important APIs/types/functions: Provider objects use oid `{tenant}oidc_url.{url_without_prefix}` in `zone.oidc_pool`. Metadata keys use `{tenant}${url}`. `get_oidc_metadata_key()` and `parse_oidc_metadata_key()` translate metadata keys. `read()`, `write()`, `remove()`, `list()`, `list_oidc_urls()`, and `list_account_oidcs()` implement public behavior. `MetadataHandler` exposes metadata type `"oidc"` and calls mdlog completion.

Control flow: `write()` removes URL scheme prefix, writes the provider object, links it to an account OIDC list if `tenant` is an account id, then completes mdlog when supplied. `remove()` deletes the object, unlinks account index if applicable, then completes mdlog. `list()` chooses the account-index path for account tenants; otherwise it scans `zone.oidc_pool` by tenant prefix and decodes each object. Metadata get parses the metadata key, reads the object, and wraps it as `MetadataObject`; metadata put writes nonexclusively and returns `STATUS_APPLIED` on success.

State/persistence: Primary provider state is the encoded `RGWOIDCProviderInfo` object. Account tenants also have a cls_user account-resource list under `account::get_oidcs_obj()`. Metadata sync state is recorded through `RGWSI_MDLog::complete_entry()`.

Dependencies/integration: Depends on account helpers, `oidcs.cc` account-resource helpers, `RGWOIDCProviderInfo`, `url_remove_prefix()`, RGW metadata lister/handler, mdlog service, sysobj, and librados.

Risks: Link/unlink failures to account indexes are non-fatal, so account-optimized listing can miss existing providers or include deleted ones; `list_account_oidcs()` skips stale `-ENOENT` entries. Metadata listing scans all oidc-pool objects with empty prefix and filters oids containing `oidc_url.`, which may be expensive. Metadata key parsing uses the first `$`; URLs containing `$` remain in the url part, but tenants cannot contain this separator safely.

Test signals: CRUD with mdlog completion, account and non-account tenant listing, stale account index entries, URL prefix normalization, metadata key parse/format round trip, corrupt provider decode, and metadata lister filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/oidc.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/oidc.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/oidc.h

Purpose: Declares the OIDC provider RADOS persistence and metadata sync API.

Important APIs/types/functions: `read()`, `write()`, `remove()`, `list()`, `list_oidc_urls()`, `list_account_oidcs()`, `create_metadata_handler()`, `get_oidc_metadata_key()`, and `parse_oidc_metadata_key()` form the public interface.

Control flow: The API separates direct provider CRUD from account-index listing. Optional mdlog and objv parameters allow the same functions to serve admin paths and metadata sync.

State/persistence: Provider data is stored in zone OIDC pool objects; account provider URL indexes are stored via cls_user helpers; metadata keys use tenant/url conversion.

Dependencies/integration: Forward declares sysobj, mdlog, objv, zone params, provider info, metadata handler, and librados. Includes Ceph time for mtime.

Risks: Callers must pass normalized URLs consistently. Account vs non-account behavior depends on tenant string satisfying account-id validation.

Test signals: API-level tests should cover optional objv/mdlog use, URL listing pagination, account/non-account tenant split, and metadata key conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/oidc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/oidcs.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/oidcs.cc

Purpose: Implements account-scoped OIDC provider URL listing helpers using the `cls_user_account_resource` object-class API.

Important APIs/types/functions: `add()` stores a resource named by `url_remove_prefix(info.provider_url)`. `remove()` deletes a resource by provider URL string. `list()` pages resources and returns provider URL names.

Control flow: Operations resolve the supplied account OIDC object to `rgw_rados_ref`, build cls_user account-resource add/remove/list operations, and operate with optional yield. Listing treats missing objects as empty, returns cls errors, and appends resource names to `provider_urls`.

State/persistence: Account OIDC indexes live on the `account::get_oidcs_obj()` object. Unlike group resources, no custom metadata payload is encoded; the resource name is the URL.

Dependencies/integration: Depends on librados, cls_user client, `RGWOIDCProviderInfo`, `url_remove_prefix()`, and RGW account OIDC object helpers. `oidc.cc` calls these functions during provider write/remove/list.

Risks: `remove()` expects the same normalized URL form that `add()` stored; callers passing a provider URL with scheme can fail to remove the entry. Listing does not clear `next_marker` when not truncated in this file, so callers should rely on cls output or ensure empty marker semantics.

Test signals: Add/remove/list with normalized and unnormalized URLs, missing object listing, pagination markers, limit enforcement, and stale-index behavior with `oidc.cc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/oidcs.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/oidcs.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/oidcs.h

Purpose: Declares account OIDC provider URL index helper APIs.

Important APIs/types/functions: `add()`, `remove()`, and `list()` manage provider URL resources on a supplied `rgw_raw_obj`, with exclusive/limit support for add and marker/max pagination for list.

Control flow: Callers choose the account index object and pass optional-yield context. Returned `provider_urls` and `next_marker` drive higher-level provider reads.

State/persistence: The API manipulates cls_user account-resource entries; resource names are provider URLs.

Dependencies/integration: Uses librados forward declarations, SAL forward types, `RGWOIDCProviderInfo`, and `DoutPrefixProvider`.

Risks: URL normalization is not encoded in the type system; add/remove/list callers must agree on whether scheme prefixes are stripped.

Test signals: Compile consumer paths, pagination propagation, exclusive add conflicts, limit behavior, and URL normalization through the higher-level OIDC API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/oidcs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_bl_rados.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_bl_rados.cc

Purpose: Implements the RADOS-backed bucket logging commit manager. It records pending temporary log objects in per-target commit-list objects, maintains a global list of commit-list objects, and runs a background manager that claims lists with cls_lock, commits pending logs to target buckets, and cleans up after deleted buckets.

Important APIs/types/functions: `COMMIT_LIST_OBJECT_NAME` is the global list object. `add_commit_target_entry()` writes an omap entry `{obj_name -> tail_obj_name}` to a target list and adds that list to the global object; it also stores `TEMP_POOL_ATTR` with the temp pool. `list_pending_commit_objects()` lists pending keys for a target. `BucketLoggingManager` owns the worker io_context/thread, lock cookie, timers, global-list processing, per-list processing, and shutdown. `init()`/`shutdown()` manage a singleton manager.

Control flow: Writers add entries to the target commit list then global list. The manager periodically reads the global list, tries to acquire/renew an exclusive cls lock on each commit-list object, and spawns a coroutine per owned list. Per-list processing asserts lock ownership, reads up to 1024 omap entries and temp pool xattr, loads the destination bucket, calls `commit_logging_object()` for each entry, removes processed omap keys, sleeps when idle, and removes the whole list/global entry when the bucket is deleted and pending objects were cleaned. Shutdown flips `m_shutdown`, drops the work guard, joins the worker with a timeout, and can stop the io_context.

State/persistence: Persistent state lives in the RGW logging pool: a global omap object keyed by commit-list name, per-target commit-list omap objects keyed by log object name with values containing temp object names, a temp-pool xattr, and cls_lock state on each list object. Temporary log objects live in the encoded temp pool until committed or deleted.

Dependencies/integration: Depends on boost.asio coroutines/timers, cls_lock, librados operations, RGW RadosStore, SAL Bucket `commit_logging_object()`, bucket loading, sysobj deletion, Ceph perf/logging context, zone features, and RGW logging pool context.

Risks: Multi-object add is not atomic; a target list can exist without a global entry if the second write fails. Per-list coroutine mutates shared `remove_entries`, `is_idle`, `stop_processing`, and deletion flags from spawned child coroutines without explicit synchronization on those variables. Removing processed entries after committing logs is critical; failure logs possible log-record loss. `parse_list_name()` cannot represent slashes in tenant/bucket/id components. Lock loss during entry removal is tolerated by design, but can race with another daemon. Singleton init rejects double init but does not recover a failed worker thread.

Test signals: Add/list pending entries, global-list discovery, lock acquisition/renewal/failover, successful commit removes entries, commit failure leaves entries, deleted bucket cleanup removes temp objects and commit list, malformed list names, missing/corrupt temp-pool xattr, shutdown while lists are active, and multi-daemon lock contention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_bl_rados.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_bl_rados.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_bl_rados.h

Purpose: Declares the RADOS bucket logging commit-manager API.

Important APIs/types/functions: `init()` starts the singleton commit manager for a `RadosStore` and `SiteConfig`. `shutdown()` stops it. `add_commit_target_entry()` records a pending log object for a target bucket/prefix and temp pool. `list_pending_commit_objects()` lists pending entries for a target bucket/prefix.

Control flow: Callers add commit targets during bucket logging write paths; the background manager later processes them. Listing is a diagnostic/helper path over the same commit-list object.

State/persistence: The API exposes persistent commit-list manipulation in the logging pool while hiding manager internals.

Dependencies/integration: Forward declares `SiteConfig`, SAL `RadosStore`, `DoutPrefixProvider`, and uses RGW pool and yield types through included project headers.

Risks: Header formatting leaves `list_pending_commit_objects()` less indented than the namespace block but functionally valid. The singleton lifecycle means tests and daemon startup/shutdown must avoid double init or leaked manager state.

Test signals: Link callers against the header, initialize/shutdown idempotency behavior, add/list consistency, and integration with bucket logging commit paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_bl_rados.h -->
