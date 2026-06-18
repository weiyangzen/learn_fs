# File Research: sources/cow-pools/openzfs/module/zfs/dsl_prop.c

## Summary
Implements OpenZFS DSL property lookup, inheritance, received-property handling, set/inherit sync tasks, property-change callbacks, all-property enumeration, and helpers for building property nvlists. Properties are stored in DSL dir or snapshot ZAP objects, with suffix keys for inherited, received, and newer index values.

## Main Responsibilities
- Resolves effective property values from snapshot props, local dir props, received props, inherited parent props, or defaults.
- Supports callback registration and notification for integer property changes.
- Predicts effective quota/reservation-style values before setting them.
- Sets, clears, inherits, and receives individual or batched properties through sync tasks.
- Stores special ignore-unknown-value entries for newer indexed property values while preserving compatibility with older ZFS versions.
- Enumerates local, received, inherited, and snapshot-valid properties into nvlists.
- Tracks whether a dataset has received properties using `ZPROP_HAS_RECVD`.

## Key APIs
- Lookup: `dsl_prop_get_dd()`, `dsl_prop_get_ds()`, `dsl_prop_get()`, `dsl_prop_get_integer()`, `dsl_prop_get_int_ds()`, `dsl_prop_get_all()`, `dsl_prop_get_received()`.
- Mutation: `dsl_prop_set_int()`, `dsl_prop_set_string()`, `dsl_prop_inherit()`, `dsl_props_set()`, `dsl_props_set_check()`, `dsl_props_set_sync()`, `dsl_props_set_sync_impl()`, `dsl_prop_set_sync_impl()`.
- Prediction and received tracking: `dsl_prop_predict()`, `dsl_prop_get_hasrecvd()`, `dsl_prop_set_hasrecvd()`, `dsl_prop_unset_hasrecvd()`.
- Callback lifecycle: `dsl_prop_init()`, `dsl_prop_fini()`, `dsl_prop_register()`, `dsl_prop_unregister()`, `dsl_prop_unregister_all()`, `dsl_prop_hascb()`, `dsl_prop_notify_all()`.
- Nvlist helpers: `dsl_prop_nvlist_add_uint64()`, `dsl_prop_nvlist_add_string()`.

## Important Behavior
Property keys use suffixes: `$inherit` for explicit inheritance, `$recvd` for received values, and `$iuv` for newer indexed values older implementations should ignore. `dsl_prop_get_dd()` checks `$iuv`, local, explicit inherit, received, parents, and finally default values.

`dsl_prop_get_ds()` handles snapshot property ZAPs first, then delegates to the containing dir. Snapshot properties require the snapshot props feature on old-version checks, and non-snapshot datasets use the dir's `dd_props_zapobj`.

`dodefault()` returns defaults for normal mutable properties and set-once properties, but not ordinary readonly properties. This lets initial values be supplied without treating readonly runtime stats as settable defaults.

`dsl_prop_predict()` is intentionally narrow and only predicts quota, reservation, refquota, and refreservation effective values. It models interactions between local and received values, plus pre-`SPA_VERSION_RECVD_PROPS` source translation.

Callbacks are stored per dir in `dsl_prop_record_t` lists and per dataset in `ds_prop_cbs`. Registration immediately invokes the callback with the current integer value. Notification walks inheritance descendants unless a local property blocks propagation.

Callback records do not hold datasets. Recursive notification paths use `dsl_dataset_try_add_ref()` before invoking callbacks for datasets that could have been evicted, especially snapshot callback records encountered while walking head datasets.

`dsl_prop_set_sync_impl()` creates snapshot props ZAPs lazily, applies source-specific ZAP changes, removes empty snapshot prop ZAPs, computes the new effective value, notifies callbacks for integer properties, and logs history. Source combinations cover clearing local, clearing received, clearing both, setting local, setting received, and explicit inheritance.

`dsl_prop_set_iuv()` stores new indexed values for `redundant_metadata=some/none` and `snapdir=disabled` in `$iuv` while writing the default numeric value to the base key for older-version compatibility.

`dsl_prop_get_all_impl()` iterates property ZAPs, filters suffix keys, suppresses overridden received values, skips incompatible inherited or snapshot properties, resolves strings by lookup when needed, and records each property as an nvlist with `ZPROP_VALUE` and `ZPROP_SOURCE`.

`dsl_prop_get_received()` returns true received properties only after `ZPROP_HAS_RECVD` exists; before that it treats local properties as the received set for compatibility with older pools.

## State and Synchronization
Callers must hold the DSL pool config lock for low-level lookup and callback operations. Callback list manipulation uses the containing dir's `dd_lock`. Sync-time mutation runs through `dsl_sync_task()` and uses MOS ZAP updates under assigned DMU transactions.

Snapshot property ZAPs are optional and destroyed when empty. Dir property ZAPs are permanent fields of `dsl_dir_phys_t`. Set operations estimate required blocks as two blocks per property unless only removing entries.

## Dependencies
Depends on DSL dirs and datasets, DMU transactions, ZAP cursors/lookups/updates, sync tasks, SPA version/feature behavior, ZFS property metadata from `zfs_prop.h`, nvlists, pool config locking, dataset eviction reference helpers, and spa history logging.

## Risks
Property source precedence is subtle. Incorrect handling of `$inherit`, `$recvd`, `$iuv`, snapshot props, or parent traversal can expose wrong effective values or wrong `setpoint` strings.

Callback notification is lifetime-sensitive because callback records intentionally avoid dataset holds. Missing `dsl_dataset_try_add_ref()` in recursive paths would risk use-after-free during eviction.

`dsl_prop_set_sync_impl()` must preserve compatibility with old pool versions and received-property semantics. Source bitmask mistakes can silently clear the wrong ZAP key or fail to restore local/received precedence.

All-property enumeration must avoid duplicate keys and skip compatibility helper keys. Returning `$iuv` or overridden `$recvd` values as ordinary properties would confuse `zfs get` and receive rollback paths.

String length and ZAP name/value limits are enforced in `dsl_props_set_check()`. New callers that bypass batched property setting need equivalent validation.
