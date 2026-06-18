# Group Research: group_1778_stratisd_sources_block_storage_stratisd_src_dbus_pool_pool_3_8_prop_53f2b2d5cba8

Read scope: `Docs/research_subset_a.md`. Source tree `sources/block-storage/stratisd` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_8/props.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_8/props.rs

This file provides D-Bus property adapter functions for pool interface revision 3.8 encryption metadata. Each function takes a read guard over a `Pool` and converts engine-level state into zbus-friendly values.

Key behavior:
- `free_token_slots_prop()` exposes `Pool::free_token_slots()` as the project’s tuple-as-option convention, defaulting to `0`.
- `metadata_version_prop()` casts the pool metadata version to `u64`.
- `volume_key_loaded_prop()` calls `Pool::volume_key_is_loaded(pool_uuid)` and returns either a boolean `Value` or an error string `Value`.
- `key_descs_prop()` handles both modern `EncryptionInfo` and legacy `PoolEncryptionInfo`:
  - modern info returns a vector of `(token_slot, key_description)`;
  - legacy info returns a tuple-option around the single key description;
  - unencrypted pools return string `"Unencrypted"`.
- `clevis_infos_prop()` mirrors key description handling, returning modern per-slot Clevis `(pin, json)` records, legacy single Clevis info, or `"Unencrypted"`.

Important dependencies:
- Uses `either::Either` because `Pool::encryption_info()` can expose modern or legacy encryption info.
- Uses `option_to_tuple()` from D-Bus utilities to preserve D-Bus ABI representation of optional values.
- Uses `zbus::zvariant::Value` where the concrete D-Bus payload type varies by encryption state/version.

Role in architecture:
- This is a compatibility adapter, not business logic. Token state and encryption information are owned by the engine; this file only normalizes it for r8 D-Bus clients.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_8/props.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_9/methods.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_9/methods.rs

This file implements the new pool r9 D-Bus methods for online pool encryption lifecycle operations:
- `encrypt_pool_method`
- `reencrypt_pool_method`
- `decrypt_pool_method`

All methods follow the Stratis D-Bus return shape: operation result, `u16` return code, and return string.

`encrypt_pool_method()`:
- Parses key descriptions from D-Bus tuple-options into `Option<u32>` token slots.
- Parses Clevis JSON strings with `serde_json::from_str`.
- Builds `InputEncryptionInfo`; rejects calls with no unlock methods.
- Gets a mutable pool guard by UUID.
- Runs blocking engine operations inside `tokio::task::spawn_blocking`.
- Calls the engine/pool lifecycle:
  - `start_encrypt_pool()`
  - `do_encrypt_pool()` under downgraded read guard
  - `Engine::upgrade_pool()` back to write guard
  - `finish_encrypt_pool()`
- Emits keyring, Clevis, and encrypted-property D-Bus signals on successful creation.
- Returns identity success if the pool was already encrypted.

`reencrypt_pool_method()`:
- Gets a mutable pool guard by UUID.
- Runs `start_reencrypt_pool()`, `do_reencrypt_pool()`, and `finish_reencrypt_pool()` with the same downgrade/upgrade pattern.
- Emits `last_reencrypted_timestamp` signal when successful.

`decrypt_pool_method()`:
- Performs `decrypt_pool_idem_check()` first.
- If decryption is required, downgrades to read guard for `do_decrypt_pool()`, upgrades, then calls `finish_decrypt_pool()`.
- Emits keyring, Clevis, encrypted, and last-reencrypted signals after successful decryption.
- Returns identity success if already decrypted.

Concurrency pattern:
- Write lock is used for idempotence/setup and final state mutation.
- Long-running actual crypto/device work runs under read lock after `downgrade()`.
- `Engine::upgrade_pool()` is used to regain write access for finalization without losing the logical operation sequence.

Error handling:
- Engine and parsing errors are converted through `engine_to_dbus_err_tuple()`.
- Join errors from `spawn_blocking` are converted through `StratisError::from`.
- Missing pool is represented as `StratisError::Msg`.

Role in architecture:
- This is the D-Bus orchestration layer for r9 encryption operations. It coordinates parsing, locking, lifecycle calls, and signals but delegates actual engine semantics to the `Pool` trait.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_9/methods.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_9/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_9/mod.rs

This file defines the `PoolR9` zbus interface implementation for `org.storage.stratis3.pool.r9`.

Structure:
- Holds shared service state:
  - `Arc<Connection>`
  - `Arc<dyn Engine>`
  - `Lockable<Arc<RwLock<Manager>>>`
  - object path counter
  - pool UUID
- Provides `new()`, `register()`, and `unregister()` helpers for object-server registration.
- Declares `methods` and `props` submodules.
- Re-exports r9 methods and `last_reencrypted_timestamp_prop`.

Interface composition:
- Most methods/properties are imported from earlier pool interface versions:
  - r0: core pool operations/properties such as create/destroy filesystems, add devices, name, size, used, encrypted.
  - r1: filesystem limit, overprovisioning, no allocation space.
  - r3: grow physical device.
  - r5: init cache.
  - r6: create filesystems.
  - r7: metadata and filesystem metadata.
  - r8: keyring/Clevis bind/rebind/unbind and token metadata.
- r9 adds:
  - `encrypt_pool`
  - `reencrypt_pool`
  - `decrypt_pool`
  - `last_reencrypted_timestamp`

D-Bus methods:
- Exposes filesystem creation/destruction/snapshot, device addition/cache init, naming, encryption token management, physical growth, metadata fetch, and r9 pool encryption lifecycle methods.
- Each method delegates to a free function with the shared engine/connection/manager/counter/UUID context.

D-Bus properties:
- `uuid` is const.
- Mutable/signaled pool properties include `name`, `encrypted`, `available_actions`, key descriptions, Clevis infos, cache state, physical sizes, allocation, filesystem limit, overprovisioning, no allocation space, free token slots, and last reencryption timestamp.
- `volume_key_loaded` uses `emits_changed_signal = "false"`.
- `metadata_version` is const.
- Setters for `fs_limit` and `overprovisioning` use `set_pool_prop()` with signal-on-change callbacks.

Role in architecture:
- This file is the versioned D-Bus facade for pool revision r9. It preserves backward-compatible behavior by reusing older revision implementations while adding online encryption/decryption operations and last reencryption timestamp visibility.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_9/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_9/props.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_9/props.rs

This file contains the r9-specific pool property adapter:
- `last_reencrypted_timestamp_prop()`

Behavior:
- Reads `Pool::last_reencrypt()` from a pool read guard.
- Converts `Option<DateTime<Utc>>` into D-Bus tuple-as-option form.
- Formats timestamps as RFC3339 with seconds precision and UTC `Z` formatting via `chrono::SecondsFormat::Secs`.
- Uses an empty string as the default value when no reencryption timestamp exists.

Role in architecture:
- This is the D-Bus representation layer for the r9 `last_reencrypted_timestamp` property. The timestamp is produced by engine/pool finalization logic; this file only formats it.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_9/props.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/shared.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/pool/shared.rs

This file provides shared D-Bus helper functions for reading and setting pool properties.

Key functions:
- `get_pool()`:
  - resolves a pool by UUID through `Engine::get_pool`;
  - returns a read guard or zbus FDO `Failed` error.
- `get_pool_mut()`:
  - resolves a mutable pool guard through `Engine::get_mut_pool`;
  - returns a write guard or zbus failure.
- `pool_prop()`:
  - generic read-property adapter;
  - gets a read guard and applies a supplied property function.
- `set_pool_prop()`:
  - generic write-property adapter;
  - gets a write guard, calls a supplied async setter, drops the guard, then emits a supplied signal only if the setter reported a change.

Important design point:
- `set_pool_prop()` releases the pool lock before sending D-Bus signals. This avoids holding engine/pool locks while performing object-server signaling work.

Role in architecture:
- This file removes repeated guard-resolution and signal-on-change boilerplate from versioned pool interfaces.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/shared.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/types.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/types.rs

This file defines D-Bus-facing wrapper types, signatures, and conversions for Stratis engine types.

Key definitions:
- `FilesystemSpec<'a>`:
  - D-Bus input type for filesystem creation specs: name plus optional size and optional size limit.
- `ManagerR2<T>` and `ManagerR8<T>`:
  - marker wrappers indicating which manager interface revision a value is returned from.
- `DbusErrorEnum`:
  - numeric method return code enum: `OK = 0`, `ERROR = 1`.

D-Bus type conversions:
- Implements `zvariant::Type` and `From<...> for Value` for:
  - `LockedPoolsInfo`
  - `ManagerR2<StoppedPoolsInfo>`
  - `ManagerR8<StoppedPoolsInfo>`
  - `PoolUuid`
  - `ActionAvailability`

Locked pool representation:
- Converts locked pools into a nested dictionary keyed by pool UUID.
- Per-pool dictionary includes:
  - key description result/option tuple
  - Clevis info result/option tuple
  - devices with devnode and device UUID
  - optional pool name

Stopped pool representation:
- Shared helper `stopped_pools_to_value()` includes stopped and partially constructed pools.
- Always includes devices and optional pool name.
- When metadata is requested, includes:
  - `metadata_version`
  - `features`, including encryption/key-description/Clevis flags when present.
- r2 conversion omits metadata/features.
- r8 conversion includes metadata/features.

Role in architecture:
- This file is the ABI conversion layer for complex manager-returned state. It preserves revision-specific D-Bus payload differences while deriving values from common engine structures.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/types.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/udev.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/udev.rs

This file defines `UdevHandler`, which bridges queued udev engine events into D-Bus registration and property signaling.

State held by `UdevHandler`:
- D-Bus connection.
- Engine reference.
- Manager lock.
- `UnboundedReceiver<UdevEngineEvent>`.
- Object path counter.

Main behavior:
- `process_udev_events()`:
  - waits for at least one event;
  - drains any immediately available additional events with `try_recv()`;
  - calls `Engine::handle_events(events)`;
  - registers any newly discovered pools returned by the engine;
  - sends blockdev new-physical-size signals for block devices whose size diff changed.
- `register_pool()`:
  - delegates to `dbus::pool::register_pool`.

Error handling:
- A closed event channel is converted to `StratisError::Msg`.
- Pool registration failures and missing blockdev object paths are logged as warnings rather than aborting the whole handler.

Role in architecture:
- This is the D-Bus side of udev reconciliation. The engine interprets events; this handler updates exported D-Bus objects and emits property-change notifications.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/udev.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/util.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/util.rs

This large utility file centralizes D-Bus ABI helpers, error conversion, and property-change signal fan-out across all versioned Stratis D-Bus interfaces.

General conversion helpers:
- `tuple_to_option()` converts `(bool, T)` into `Option<T>`.
- `option_to_tuple()` converts `Option<T>` into `(bool, T)` with a default.
- `result_option_to_tuple()` encodes both result success/failure and optional value state into D-Bus variant-compatible form.
- `engine_to_dbus_err_tuple()` maps `StratisError` into `(ERROR, description)`, unwrapping core device-mapper errors for clearer messages.

Signal infrastructure:
- Internal `send_signal!` macro:
  - retrieves a typed interface from the zbus object server;
  - calls the generated property change/invalidation signal method;
  - logs warning on lookup or send failure.
- The rest of the file is mostly explicit fan-out helpers that emit one logical property change to every D-Bus interface revision that exposes that property.

Pool signal helpers:
- `send_pool_background_signals()`:
  - uses pool diffs to emit allocated size, used size, and no allocation space changes for background event handling.
- `send_pool_foreground_signals()`:
  - emits allocated size, used size, total physical size, and no allocation space changes for foreground operations.
- Specific helpers fan out:
  - pool name changes, also invalidating filesystem devnodes;
  - overprovisioning;
  - filesystem limit;
  - Clevis info;
  - keyring/key descriptions;
  - free token slots;
  - action availability;
  - cache presence;
  - encrypted status, r9 only;
  - last reencryption timestamp, r9 only.

Filesystem signal helpers:
- Background filesystem diffs emit size and used changes.
- Dedicated helpers emit size, used, origin, size limit, merge scheduled, and name/devnode invalidation signals across the revisions that expose each property.

Manager signal helpers:
- `send_locked_pools_signals()` emits on manager r0 and r1.
- `send_stopped_pools_signals()` emits on manager r2 through r9.

Blockdev signal helpers:
- Emit new physical size, user info, and total physical size across appropriate blockdev revisions.

Compatibility behavior:
- Older pool r0-r7 clients see singular `key_description`/`clevis_info` signals only when the changed token is the lowest/legacy slot.
- r8/r9 clients always receive plural `key_descriptions`/`clevis_infos` signals.
- r9-only additions are deliberately not fanned out to older revisions.

Role in architecture:
- This file is the D-Bus notification backbone. It keeps the versioned ABI consistent by making every state-changing path call one shared signal helper instead of duplicating revision fan-out logic.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/util.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/engine.rs -->
# File Research: sources/block-storage/stratisd/src/engine/engine.rs

This file defines the central engine traits and contracts used by both the real Stratis engine and the simulator.

Constants:
- `DEV_PATH = "/dev/stratis"`.
- `MAX_STRATIS_PASS_SIZE = 64` bytes, the maximum pool passphrase size stored in the kernel keyring.

Traits:
- `KeyActions`:
  - abstract keyring operations: set, list, unset.
  - uses idempotent mapping actions to distinguish identity, creation, and value changes.
- `Report`:
  - exposes JSON reports for engine state and selected report types.
- `Filesystem`:
  - common filesystem view: devnode, creation time, mount path, used/size, size limit, origin, merge scheduling.
- `BlockDev`:
  - common block device view: devnode, metadata path, user/hardware info, initialization time, size/new size, metadata version.
- `Pool`:
  - the main pool behavior contract.
  - includes filesystem, blockdev, cache, encryption-token, metadata, grow, size, overprovisioning, merge, volume-key, and online encryption lifecycle APIs.
- `Engine`:
  - async top-level engine contract for pool creation/destruction/rename/unlock/start/stop, event handling, locking, reports, key handler access, and state refresh.
- `StateDiff` and `DumpState`:
  - generic state-diffing contracts for change detection.

Important `Pool` encryption lifecycle methods:
- `start_encrypt_pool()`
- `do_encrypt_pool()`
- `finish_encrypt_pool()`
- `start_reencrypt_pool()`
- `do_reencrypt_pool()`
- `finish_reencrypt_pool()`
- `decrypt_pool_idem_check()`
- `do_decrypt_pool()`
- `finish_decrypt_pool()`
- `last_reencrypt()`

Concurrency contract:
- `Engine::upgrade_pool()` explicitly supports operations that begin under one lock mode, run long work under another, then finalize with write access.

Role in architecture:
- This is the core abstraction boundary. D-Bus code, simulator code, and real engine code all meet at these traits, which define the behavior and idempotence semantics for Stratis operations.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/engine.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/macros.rs -->
# File Research: sources/block-storage/stratisd/src/engine/macros.rs

This file defines shared macros used across engine implementations and tests.

Lock/table convenience:
- `get_pool!` and `get_mut_pool!` wrap async pool table read/write access.
- Rename precheck macros implement common idempotent rename logic for pools and filesystems:
  - source missing;
  - same name identity;
  - target name conflict.

User info:
- `set_blockdev_user_info!` updates user info only when changed.

Error message construction:
- `device_list_check_num!` formats singular/plural device-list messages.
- `create_pool_generate_error_string!` builds detailed idempotent create-pool conflict errors.
- `init_cache_generate_error_string!` builds detailed cache-initialization mismatch errors.

Conversion helpers:
- `convert_int!` returns `StratisError` on fallible integer conversion.
- `convert_const!` is for compile-time-known safe conversions.
- `uuid_to_string!` formats UUIDs for names/signatures.

Encryption helper:
- `pool_enc_to_enc!` converts legacy pool encryption info into modern `EncryptionInfo`.

Test-only helpers:
- `strs_to_paths!`
- `convert_test!`
- `retry_operation!`
- `generate_events!`, which scans initialized udev devices for Stratis/crypto signatures.

Role in architecture:
- These macros consolidate repeated idempotence, validation, conversion, and test patterns used by both simulator and real engine code.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/macros.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/mod.rs -->
# File Research: sources/block-storage/stratisd/src/engine/mod.rs

This is the public module facade for the `engine` subsystem.

Exports:
- Core traits:
  - `BlockDev`
  - `Engine`
  - `Filesystem`
  - `KeyActions`
  - `Pool`
  - `Report`
- Shared helpers:
  - `total_allocated`
  - `total_used`
- Simulator:
  - `SimEngine`
- Real Stratis engine items:
  - process/keyring/device-mapper setup helpers;
  - static header types;
  - `StratEngine`, `StratKeyActions`, `StratPool`;
  - constants and cache/integrity helpers.
- Lock/table structures:
  - read/write guards, shared/exclusive guards, `Table`.
- Engine action/type vocabulary:
  - UUIDs, identifiers, action enums, diffs, encryption info, integrity specs, stopped/locked pool info, udev events, unlock methods, and defaults.

Module declarations:
- Imports macros with `#[macro_use]`.
- Defines internal modules:
  - `engine`
  - `shared`
  - `sim_engine`
  - `strat_engine`
  - `structures`
  - `types`

Role in architecture:
- This file is the stable import surface for the rest of stratisd. Most callers use `crate::engine::{...}` re-exports rather than reaching into submodules directly.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/shared.rs -->
# File Research: sources/block-storage/stratisd/src/engine/shared.rs

This file contains shared engine helper functions used by both real and simulated implementations.

Pool/cache idempotence:
- `create_pool_idempotent_or_err()`:
  - compares requested data blockdev paths with existing data-tier devices.
  - returns identity if identical, otherwise a detailed conflict error.
- `init_cache_idempotent_or_err()`:
  - compares requested cache paths with existing cache devices.
  - returns empty set-create action if identical, otherwise conflict error.

Key reading:
- `read_key_shared()`:
  - reads key material from a raw file descriptor into a provided buffer.
  - enforces `MAX_STRATIS_PASS_SIZE`.
  - checks for extra data with `poll()` when the buffer fills exactly.
  - avoids closing the passed fd by converting it back with `into_raw_fd()`.

Validation:
- `validate_name()` rejects:
  - empty names;
  - NUL/control characters;
  - `.` and `..`;
  - names over 255 bytes;
  - leading/trailing whitespace;
  - characters not allowed in udev symlinks;
  - absolute paths or multi-component paths.
- `validate_paths()` requires absolute paths.
- `validate_filesystem_size()`:
  - validates max representable size;
  - requires sector alignment;
  - enforces minimum thin device size.
- `validate_filesystem_size_specs()` validates and normalizes filesystem specs, defaulting unspecified size to 1 TiB.

Metadata aggregation:
- `gather_encryption_info()` ensures all devices in a pool are consistently encrypted or unencrypted and builds `PoolEncryptionInfo`.
- `gather_pool_name()` gathers optional names and marks inconsistent names.

Diff helpers:
- `total_used()` combines thin-pool used bytes and metadata size diffs.
- `total_allocated()` combines allocated size and metadata size diffs.

Time helpers:
- `unsigned_to_timestamp()` converts seconds/nanoseconds into `DateTime<Utc>`.
- `now_to_timestamp()` returns current UTC truncated to seconds.

Tests:
- Focus on name validation edge cases, including path-like values, whitespace, control characters, special punctuation, and unicode.

Role in architecture:
- This file holds cross-engine policy: validation, idempotence comparison, size normalization, key length enforcement, and diff arithmetic.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/shared.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/sim_engine/blockdev.rs -->
# File Research: sources/block-storage/stratisd/src/engine/sim_engine/blockdev.rs

This file defines the simulated block device implementation `SimDev`.

State:
- `devnode`
- optional `user_info`
- optional `hardware_info`
- `initialization_time`

Trait implementation:
- Implements `BlockDev`.
- `devnode()` and `metadata_path()` both return the simulated path.
- `size()` always reports 1 GiB.
- `new_size()` always returns `None`.
- `metadata_version()` always returns `StratSigblockVersion::V2`.

Construction and mutation:
- `SimDev::new()` creates a new random `DevUuid` and records timestamp using `now_to_timestamp()`.
- `set_user_info()` uses the shared macro to update only on change.

Serialization:
- Converts `&SimDev` into JSON containing path and size.

Role in architecture:
- This is the simulator’s minimal `BlockDev` implementation. It provides stable, fake blockdev metadata sufficient for tests and D-Bus/report behavior without touching real devices.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/sim_engine/blockdev.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/sim_engine/engine.rs -->
# File Research: sources/block-storage/stratisd/src/engine/sim_engine/engine.rs

This file implements `SimEngine`, an in-memory implementation of the `Engine` trait.

State:
- `pools`: active pools in an `AllOrSomeLock` table.
- `key_handler`: simulated keyring.
- `stopped_pools`: locked table of stopped pools.

Reporting:
- Converts active and stopped pools into JSON arrays.
- `engine_state_report()` returns full simulator state.
- `get_report(StoppedPools)` returns stopped pool state only.

Core engine behavior:
- `create_pool()`:
  - validates name and paths;
  - validates integrity spec;
  - converts input encryption info, checking simulated keyring when available;
  - returns identity for identical existing pool specs;
  - requires at least one blockdev;
  - deduplicates input blockdev paths.
- `destroy_pool()`:
  - refuses to destroy pools with filesystems;
  - removes active pool and calls `destroy()`;
  - returns identity for absent pool.
- `rename_pool()`:
  - uses shared rename precheck;
  - removes and reinserts pool under new name.
- `unlock_pool()`:
  - returns empty success; simulator has no real locked-device setup.
- `start_pool()`:
  - returns identity for already active pools after validating unlock/passphrase consistency.
  - moves stopped pools back to active.
  - can clear cache when `remove_cache` is requested.
- `stop_pool()`:
  - returns identity if already stopped.
  - moves active pool to stopped table.
  - errors if missing.
- Event/diff methods return empty sets/maps because the simulator has no real udev/device-mapper events.
- `refresh_state()` is a no-op.
- `is_sim()` returns true.

Stopped pool metadata:
- `stopped_pools()` builds `StoppedPoolsInfo` from stopped simulator pools, including devices, metadata version v2, and feature flags derived from encryption state.

Locking:
- Implements trait guard methods by converting simulator guards into dyn `Pool` guards.
- `upgrade_pool()` delegates to table upgrade logic.

Tests:
- Cover missing pool lookups, destroy behavior, create idempotence/conflicts, duplicate devices, and rename cases.

Role in architecture:
- `SimEngine` lets D-Bus and higher-level logic exercise the real `Engine` contract without requiring real block devices, cryptsetup, or device-mapper state.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/sim_engine/engine.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/sim_engine/filesystem.rs -->
# File Research: sources/block-storage/stratisd/src/engine/sim_engine/filesystem.rs

This file defines the simulator filesystem model.

Persistent/save shape:
- `FilesystemSave` records:
  - name
  - UUID
  - size
  - creation timestamp
  - optional size limit
  - optional origin
  - merge scheduled flag

Runtime type:
- `SimFilesystem` holds:
  - random number for synthetic devnode;
  - creation time;
  - size;
  - optional size limit;
  - optional origin filesystem UUID;
  - merge scheduled state.

Construction and mutation:
- `new()` rejects size limits smaller than filesystem size.
- `set_size_limit()` rejects limits below current size and returns whether the value changed.
- `set_origin()` updates origin and returns whether it changed.
- `set_merge_scheduled()`:
  - no-ops if unchanged;
  - rejects scheduling merge when there is no origin;
  - otherwise updates state.
- `record()` produces `FilesystemSave`.

Trait implementation:
- `devnode()` returns synthetic `/stratis/random-<n>`.
- `path_to_mount_filesystem()` returns synthetic `/somepath/<pool>/<fs>`.
- `used()` reports half the filesystem size.
- `size()`, `size_limit()`, `origin()`, and `merge_scheduled()` expose stored state.

Serialization:
- Converts to JSON with size, used, size limit, and origin strings.

Role in architecture:
- This is the simulator’s `Filesystem` implementation, modeling enough size/origin/merge behavior to test pool and D-Bus workflows.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/sim_engine/filesystem.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/sim_engine/keys.rs -->
# File Research: sources/block-storage/stratisd/src/engine/sim_engine/keys.rs

This file implements simulated keyring operations through `SimKeyActions`.

State:
- A `Mutex<HashMap<KeyDescription, Vec<u8>>>` stores key material in memory.

Internal behavior:
- `contains_key()` checks whether a key description exists.
- `read()` clones stored key bytes into `SafeMemHandle` and returns `SizedKeyMemory`.

`KeyActions` implementation:
- `set()`:
  - reads key material from a file descriptor using shared `read_key_shared()`;
  - returns identity when same key material already exists;
  - updates and returns value-changed when description exists with different bytes;
  - inserts and returns created when absent.
- `list()` returns all stored key descriptions.
- `unset()` removes a key or returns identity if absent.

Security/behavioral note:
- This is not a secure persistent keyring. It is a simulator implementation, but it still reuses the real passphrase size/FD reading logic to match engine behavior.

Role in architecture:
- Provides the simulator’s `KeyActions` implementation so encrypted pool creation can validate key descriptions without kernel keyring access.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/sim_engine/keys.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/sim_engine/mod.rs -->
# File Research: sources/block-storage/stratisd/src/engine/sim_engine/mod.rs

This module file defines the simulator engine submodule layout.

Public exports:
- Re-exports `SimEngine`.

Internal modules:
- `blockdev`
- `engine`
- `filesystem`
- `keys`
- `pool`
- `shared`

Role in architecture:
- Keeps the simulator implementation private except for the `SimEngine` entry point exposed by `crate::engine`.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/sim_engine/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/sim_engine/pool.rs -->
# File Research: sources/block-storage/stratisd/src/engine/sim_engine/pool.rs

This file implements `SimPool`, the simulator’s in-memory implementation of the `Pool` trait.

State:
- data block devices
- cache block devices
- filesystem table
- filesystem limit
- overprovisioning flag
- optional modern `EncryptionInfo`
- validated integrity spec
- optional last reencryption timestamp

Construction/reporting:
- `new()` deduplicates input paths, creates simulated data devices, sets default fs limit to 10 and overprovisioning enabled.
- JSON conversion reports available actions, fs limit, filesystems, data devices, and cache devices.
- `record()` returns a save-shaped `PoolSave`.

Filesystem behavior:
- `create_filesystems()`:
  - enforces fs limit;
  - validates sizes and names;
  - treats duplicate same-name/same-size specs idempotently;
  - rejects conflicting existing sizes.
- `destroy_filesystems()`:
  - refuses destruction when target snapshots or dependent snapshots have scheduled reverts;
  - removes existing requested filesystems;
  - rewires snapshot origins when an origin is removed.
- `rename_filesystem()` uses shared idempotent rename precheck.
- `snapshot_filesystem()`:
  - enforces fs limit;
  - validates snapshot name;
  - returns identity if existing target has matching size;
  - creates a new filesystem with origin set to source UUID.

Blockdev/cache behavior:
- `init_cache()`:
  - validates absolute paths;
  - rejects cache on encrypted pools when unsupported;
  - requires at least one cache path on first initialization;
  - is idempotent for matching existing cache devices.
- `add_blockdevs()`:
  - validates paths;
  - requires cache initialization before adding cache devices;
  - rejects adding a path already present in the opposite tier;
  - filters duplicates/already-present devices in the same tier.
- `set_blockdev_user_info()` validates user info as a Stratis name and returns rename-style action.
- `grow_physical()` always returns identity in simulator.

Encryption token behavior:
- `bind_clevis()` and `bind_keyring()` require encrypted pool state.
- Both enforce token-slot limits and distinguish:
  - explicit token slot;
  - automatic free slot;
  - legacy single-token behavior.
- They return identity for identical existing bindings and errors for slot/type conflicts.
- `unbind_keyring()` and `unbind_clevis()` prevent removing the last unlock method.
- Rebind methods reject empty slots and wrong mechanism types.
- Simulated Clevis rebind does not regenerate token data; it validates and returns success action.

Online encryption lifecycle:
- `start_encrypt_pool()`:
  - identity if already encrypted;
  - otherwise converts input encryption info and stores it;
  - returns dummy sector/key info.
- `do_encrypt_pool()` and `finish_encrypt_pool()` are no-ops.
- `start_reencrypt_pool()` errors if unencrypted; otherwise returns empty key info.
- `do_reencrypt_pool()` is a no-op.
- `finish_reencrypt_pool()` sets `last_reencrypt = Some(Utc::now())` and returns `ReencryptedDevice`.
- `decrypt_pool_idem_check()` returns identity if unencrypted or deleted action if encrypted.
- `do_decrypt_pool()` is a no-op.
- `finish_decrypt_pool()` clears encryption info and last reencryption timestamp.

Properties and metadata:
- Physical size is simulated as very large, allocated size as fixed, used as zero.
- `metadata_version()` returns v2.
- Current/last pool and filesystem metadata are serialized JSON from simulator state.
- `free_token_slots()` derives from encryption info.
- `volume_key_is_loaded()` and `load_volume_key()` always return false.
- `avail_actions()` is always full.
- `out_of_alloc_space()` is always false.
- `set_fs_limit()` only allows increasing the limit.
- `set_overprov_mode()` stores the requested value.

Merge scheduling:
- `set_fs_merge_scheduled()` validates origin presence and prevents ambiguous chained or competing scheduled reverts before updating the filesystem flag.

Tests:
- Cover filesystem rename, destroy, create, duplicates, and device addition behavior.

Role in architecture:
- This is the main behavioral simulator for pool operations. It mirrors real engine idempotence and validation semantics where practical, while stubbing actual storage, crypto, and device-mapper operations.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/sim_engine/pool.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/sim_engine/shared.rs -->
# File Research: sources/block-storage/stratisd/src/engine/sim_engine/shared.rs

This file provides simulator-specific shared encryption conversion.

Function:
- `convert_encryption_info()`

Behavior:
- Converts optional `InputEncryptionInfo` into optional modern `EncryptionInfo`.
- Iterates each supplied unlock mechanism and token slot.
- Uses supplied token slot when present, otherwise chooses the next free token slot.
- For key-description mechanisms, optionally checks the simulated key handler to ensure the key exists.
- Adds each unlock mechanism into `EncryptionInfo`.
- Propagates token conflicts or missing-key errors.

Role in architecture:
- This helper lets `SimEngine` and `SimPool` share the same input-to-runtime encryption conversion logic while optionally enforcing simulated keyring presence.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/sim_engine/shared.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/backstore/backstore/mod.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/backstore/backstore/mod.rs

This file defines the common internal backstore module interface for the real Stratis engine.

Module layout:
- Public submodules:
  - `v1`
  - `v2`

Trait:
- `InternalBackstore`

Required behavior:
- `device()` returns the current device-mapper device used by this tier, if any.
- `datatier_allocated_size()` returns currently allocated data-tier sectors.
- `datatier_usable_size()` returns total usable data-tier sectors.
- `available_in_backstore()` returns total unallocated usable sectors, including capped-but-unallocated and not-yet-added capacity.
- `alloc(pool_uuid, sizes)` tries to allocate multiple requested segments exactly:
  - returns `None` if the request cannot be satisfied exactly;
  - returns ordered `(start, length)` segment pairs otherwise;
  - documents metadata-changing semantics and pre/postconditions around allocation cursor bounds and contiguity.

Role in architecture:
- This is the abstraction boundary between higher-level pool logic and versioned real backstore implementations. It defines allocation and capacity semantics shared by backstore v1 and v2.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/backstore/backstore/mod.rs -->