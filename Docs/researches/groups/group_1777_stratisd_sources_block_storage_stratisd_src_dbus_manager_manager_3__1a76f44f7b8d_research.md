# Group Research: Stratisd D-Bus Manager and Pool Interfaces, Subset A

Scope confirmed from `Docs/research_subset_a.md`: `sources/block-storage/stratisd` is included in subset A. Every source file listed in this work item was read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_3/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_3/mod.rs

Purpose: Defines the `org.storage.stratis3.Manager.r3` D-Bus interface implementation.

Key behavior:
- Registers `ManagerR3` at `consts::STRATIS_BASE_PATH`.
- Stores shared `Connection`, `Engine`, `Manager` path registry, and object-path counter.
- Exposes manager version, stopped pools, key management, pool creation/destruction, pool start/stop, refresh, and engine-state reporting.
- Reuses most behavior from `manager_3_0` and `manager_3_2`.

Version-specific note:
- `create_pool` still accepts a `redundancy: (bool, u16)` argument but ignores it.
- `start_pool` accepts only `pool_uuid: &str`, not a generic id/id_type pair.

Dependencies:
- `zbus::interface`, `Fd`, `ObjectPath`, `OwnedObjectPath`.
- Engine types: `Engine`, `KeyDescription`, `StoppedPoolsInfo`, `UnlockMethod`.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_3/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_4/methods.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_4/methods.rs

Purpose: Implements the r4 manager `start_pool_method`.

Key behavior:
- Accepts an `id` plus `id_type` string.
- Supports `id_type == "uuid"` via `PoolUuid::parse_str`.
- Supports `id_type == "name"` via `Name::new`.
- Rejects unknown id types with `DbusErrorEnum::ERROR`.
- Converts the optional unlock tuple into `TokenUnlockMethod`.
- Calls `engine.start_pool(..., None, false)`.

D-Bus object lifecycle:
- On `StartAction::Started`, fetches the pool, registers each filesystem, then registers the pool and block devices.
- Emits locked-pools signals for encrypted pools.
- Emits stopped-pools signals after successful start.
- Returns identity as OK with the default false/empty result.

Failure handling:
- Converts parsing, registration, and engine errors through `engine_to_dbus_err_tuple`.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_4/methods.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_4/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_4/mod.rs

Purpose: Defines the `org.storage.stratis3.Manager.r4` D-Bus interface.

Key behavior:
- Registers `ManagerR4` at the Stratis base object path.
- Reexports and uses local `start_pool_method`.
- Reuses key, create/destroy, stop, refresh, version, and engine-report helpers from earlier manager revisions.

Version-specific note:
- Changes `start_pool` ABI from r3 by accepting `id: &str` and `id_type: &str`.
- `stop_pool` still uses an object path and delegates to `manager_3_2::stop_pool_method`.
- `create_pool` still includes ignored `redundancy`.

Dependencies:
- `manager_3_0`, `manager_3_2`, local `methods`.
- Engine types include `UnlockMethod`, `StoppedPoolsInfo`, `KeyDescription`.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_4/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_5/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_5/mod.rs

Purpose: Defines the `org.storage.stratis3.Manager.r5` D-Bus interface.

Key behavior:
- Registers `ManagerR5` at the base path.
- Preserves r4 `start_pool` id/id_type behavior by importing `manager_3_4::start_pool_method`.
- Reuses stop/refresh/stopped-pools behavior from `manager_3_2`.
- Reuses key and report methods from `manager_3_0`.

Version-specific note:
- Removes the unused `redundancy` argument from `create_pool`.
- Otherwise closely mirrors r4.

Dependencies:
- `zbus` interface generation and object-path types.
- Shared `Manager` registry and `Engine` trait.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_5/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_6/methods.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_6/methods.rs

Purpose: Implements the r6 manager `stop_pool_method`.

Key behavior:
- Accepts `id` and `id_type`, supporting `uuid` and `name`.
- Captures blockdev and filesystem UUIDs before stopping.
- Calls `engine.stop_pool(id.clone(), true)`.
- After stop attempt, compares remaining devices/filesystems and unregisters removed D-Bus objects.
- On full or partial stop, unregisters the pool object and emits stopped-pools signals.
- Emits locked-pools signals when stopped-pool metadata indicates lock information is available.

Return semantics:
- `Identity`: OK with default result.
- `Stopped`: OK with stopped pool UUID string.
- `Partial`: error return string explaining some component devices were not torn down.
- `CleanedUp`: marked unreachable in this code path.
- Engine errors are converted to D-Bus error tuples.

Important detail:
- Cleanup logic runs for `Stopped`, `Partial`, and even `Err(_)` to remove objects that disappeared despite the final action status.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_6/methods.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_6/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_6/mod.rs

Purpose: Defines the `org.storage.stratis3.Manager.r6` D-Bus interface.

Key behavior:
- Registers `ManagerR6` at the Stratis base path.
- Reuses r4 `start_pool_method`.
- Reexports local r6 `stop_pool_method`.
- Reuses create/destroy/key/report helpers from prior revisions.

Version-specific note:
- Changes `stop_pool` ABI to accept `id: &str` and `id_type: &str`.
- `create_pool` remains the r5-style version without redundancy.
- `stopped_pools` still uses `types::ManagerR2<StoppedPoolsInfo>`.

Dependencies:
- Local `methods.rs`.
- `manager_3_4::start_pool_method`.
- `manager_3_2::refresh_state_method` and `stopped_pools_prop`.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_6/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_7/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_7/mod.rs

Purpose: Defines the `org.storage.stratis3.Manager.r7` D-Bus interface.

Key behavior:
- Registers `ManagerR7` at the base path.
- Reuses r4 start-by-id behavior and r6 stop-by-id behavior.
- Reuses create/destroy/key/refresh/report behavior from earlier revisions.

Version-specific note:
- No new local methods are introduced in this file.
- It appears to preserve the r6 ABI under a new revision name.

Dependencies:
- `manager_3_4::start_pool_method`.
- `manager_3_6::stop_pool_method`.
- `manager_3_0` and `manager_3_2` helper functions.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_7/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_8/methods.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_8/methods.rs

Purpose: Implements r8 manager `create_pool_method` and `start_pool_method`.

Create pool behavior:
- Accepts multiple key descriptions and Clevis entries with optional token slots.
- Parses Clevis JSON strings into `serde_json::Value`.
- Builds `InputEncryptionInfo`.
- Accepts integrity settings: journal size, integrity tag spec, and allocate-superblock flag.
- Calls `engine.create_pool` with an `IntegritySpec`.
- On creation, registers the pool and returns pool path plus blockdev paths.

Start pool behavior:
- Accepts id/id_type, nested optional unlock method, and optional key file descriptor.
- Converts zbus `Fd` into raw fd using `AsRawFd`.
- Calls `engine.start_pool(..., key_fd, false)`.
- Registers filesystems, pool, and block devices on success.
- Emits locked-pools and stopped-pools signals as appropriate.

Failure handling:
- Invalid UUID, unknown id type, bad JSON, invalid integrity tag spec, engine errors, and D-Bus registration errors are converted to D-Bus return tuples.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_8/methods.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_8/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_8/mod.rs

Purpose: Defines the `org.storage.stratis3.Manager.r8` D-Bus interface.

Key behavior:
- Registers `ManagerR8` at the base path.
- Exposes r8 `stopped_pools` wrapper type.
- Exposes r8 pool creation with multi-token encryption and integrity arguments.
- Exposes r8 pool start with optional key fd.
- Reuses r6 stop-by-id behavior.

Version-specific note:
- `stopped_pools` returns `types::ManagerR8<StoppedPoolsInfo>`, not `ManagerR2`.
- `create_pool` ABI now includes `journal_size`, `tag_spec`, and `allocate_superblock`.
- `start_pool` ABI now includes `key_fd`.

Dependencies:
- Local `methods.rs` and `props.rs`.
- Prior manager helpers for destroy/key/report/refresh/stop.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_8/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_8/props.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_8/props.rs

Purpose: Provides the r8 manager stopped-pools property adapter.

Key behavior:
- Calls `engine.stopped_pools().await`.
- Wraps the result in `dbus::types::ManagerR8<StoppedPoolsInfo>`.

Dependencies:
- `Arc<dyn Engine>`.
- `StoppedPoolsInfo`.
- `types::ManagerR8`.

Role in API evolution:
- Separates r8 stopped-pools serialization from older `ManagerR2` serialization.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_8/props.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_9/methods.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_9/methods.rs

Purpose: Implements r9 manager `start_pool_method`.

Key behavior:
- Extends r8 start behavior with `remove_cache: bool`.
- Supports `uuid` and `name` id types.
- Accepts optional nested unlock method and optional key fd.
- Calls `engine.start_pool(..., key_fd, remove_cache)`.
- Registers filesystems first, then pool and blockdevs.
- Emits locked-pools signals for encrypted pools and stopped-pools signals after start.

Version-specific note:
- The only visible r9 method change here is exposing `remove_cache` through D-Bus start-pool semantics.

Failure handling:
- Unknown id types, UUID parse failures, missing newly started pool, registration failures, and engine errors return structured D-Bus tuples.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_9/methods.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_9/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_9/mod.rs

Purpose: Defines the `org.storage.stratis3.Manager.r9` D-Bus interface.

Key behavior:
- Registers `ManagerR9` at the base path.
- Reuses r8 create-pool and stopped-pools behavior.
- Reuses r6 stop-by-id behavior.
- Adds r9 `start_pool` signature with `remove_cache`.

Version-specific note:
- `start_pool` arguments are `id`, `id_type`, `unlock_method`, `key_fd`, and `remove_cache`.
- Other methods remain aligned with r8.

Dependencies:
- `manager_3_8::{create_pool_method, stopped_pools_prop}`.
- Local `methods::start_pool_method`.
- Prior manager helpers for key, destroy, refresh, report, and stop.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/manager_3_9/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/mod.rs

Purpose: Central manager module for Stratis D-Bus object-path bookkeeping and manager/report interface registration.

Key structures:
- `Manager` stores bidirectional maps for pool, filesystem, and blockdev object paths to UUIDs.
- Provides add/get/remove helpers for each object category.
- Add helpers permit exact duplicate path/UUID pairs, warn for some path conflicts, and error for conflicting UUID-to-path mappings.

Registration behavior:
- Imports and reexports Manager r0 through r9.
- Imports and reexports Report r0 through r9.
- `register_manager` registers every manager and report revision at `STRATIS_BASE_PATH`.
- Also registers `zbus::fdo::ObjectManager` at the base path.

Important role:
- This file is the shared registry used by manager, pool, filesystem, blockdev, and udev D-Bus code to translate engine UUIDs into stable exported object paths.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/report_3_0/methods.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/report_3_0/methods.rs

Purpose: Implements report retrieval for Report r0 and all later report revisions.

Key behavior:
- Converts a report name string into `ReportType`.
- Returns an error tuple if the report name is not understood.
- Calls `engine.get_report(report_type)`.
- Serializes the report to JSON with `serde_json::to_string`.
- Returns `(json, OK, OK_STRING)` on success.

Failure handling:
- Report name errors and serialization errors are converted with `engine_to_dbus_err_tuple`.

Dependencies:
- `Engine`, `ReportType`, `StratisError`.
- `DbusErrorEnum` and `OK_STRING`.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/report_3_0/methods.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/report_3_0/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/report_3_0/mod.rs

Purpose: Defines `org.storage.stratis3.Report.r0`.

Key behavior:
- Holds an `Arc<dyn Engine>`.
- Registers at `STRATIS_BASE_PATH`.
- Exposes `get_report(name)` with D-Bus out args `result`, `return_code`, and `return_string`.
- Delegates behavior to local `get_report_method`.

D-Bus note:
- Interface disables generated introspection docs with `introspection_docs = false`.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/report_3_0/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/report_3_1/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/report_3_1/mod.rs

Purpose: Defines `org.storage.stratis3.Report.r1`.

Key behavior:
- Holds an `Arc<dyn Engine>`.
- Registers at `STRATIS_BASE_PATH`.
- Exposes `get_report(name)`.
- Reuses `report_3_0::get_report_method`.

Version-specific note:
- No behavior change from r0; only the interface revision name changes.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/report_3_1/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/report_3_2/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/report_3_2/mod.rs

Purpose: Defines `org.storage.stratis3.Report.r2`.

Key behavior:
- Registers a report interface at the base path.
- Exposes the same `get_report(name)` method as earlier revisions.
- Delegates all behavior to `report_3_0::get_report_method`.

Version-specific note:
- Revision wrapper only; no unique logic.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/report_3_2/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/report_3_3/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/report_3_3/mod.rs

Purpose: Defines `org.storage.stratis3.Report.r3`.

Key behavior:
- Holds the engine reference.
- Registers at `STRATIS_BASE_PATH`.
- Exposes `get_report(name)` through the shared report method.

Version-specific note:
- ABI-compatible wrapper around the r0 report implementation.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/report_3_3/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/report_3_4/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/report_3_4/mod.rs

Purpose: Defines `org.storage.stratis3.Report.r4`.

Key behavior:
- Registers the r4 report interface at the base path.
- Delegates `get_report` to the shared r0 implementation.
- Uses the same out args and return tuple shape as other report revisions.

Version-specific note:
- Revision-only module with no behavior delta.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/report_3_4/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/report_3_5/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/report_3_5/mod.rs

Purpose: Defines `org.storage.stratis3.Report.r5`.

Key behavior:
- Stores `Arc<dyn Engine>`.
- Registers at `STRATIS_BASE_PATH`.
- Exposes `get_report(name)`.
- Uses `report_3_0::get_report_method`.

Version-specific note:
- No independent report logic in this revision.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/report_3_5/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/report_3_6/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/report_3_6/mod.rs

Purpose: Defines `org.storage.stratis3.Report.r6`.

Key behavior:
- Registers the report interface at the base object path.
- Exposes `get_report`.
- Delegates to the r0 report method.

Version-specific note:
- Thin compatibility wrapper for the r6 report interface name.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/report_3_6/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/report_3_7/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/report_3_7/mod.rs

Purpose: Defines `org.storage.stratis3.Report.r7`.

Key behavior:
- Holds the engine.
- Registers on the base path.
- Exposes `get_report(name)` using the shared method.

Version-specific note:
- Revision-only report interface; no unique behavior.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/report_3_7/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/report_3_8/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/report_3_8/mod.rs

Purpose: Defines `org.storage.stratis3.Report.r8`.

Key behavior:
- Registers at `STRATIS_BASE_PATH`.
- Exposes `get_report`.
- Uses the same implementation as r0.

Version-specific note:
- No behavior delta; preserves report API under r8 interface name.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/report_3_8/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/report_3_9/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/manager/report_3_9/mod.rs

Purpose: Defines `org.storage.stratis3.Report.r9`.

Key behavior:
- Registers the r9 report interface at the base path.
- Exposes `get_report(name)`.
- Delegates to `report_3_0::get_report_method`.

Version-specific note:
- Latest wrapper in this group; report behavior remains centralized in r0 methods.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/manager/report_3_9/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/mod.rs

Purpose: Top-level D-Bus module for stratisd.

Key behavior:
- Declares D-Bus submodules: macros, blockdev, consts, filesystem, manager, pool, types, udev, and util.
- Reexports core D-Bus entry points and helpers: blockdev/filesystem registration, `Manager`, `UdevHandler`, and background signal helpers.
- `create_dbus_handler` creates the system-bus connection, requests the Stratis service name, registers manager/report interfaces, and constructs the udev handler.

Runtime wiring:
- Creates a shared atomic object-path counter.
- Creates a shared `Lockable<Arc<RwLock<Manager>>>` registry.
- Returns `(Connection, UdevHandler, Manager)` for daemon integration.

Dependencies:
- `zbus::connection::Builder`.
- Tokio `UnboundedReceiver` and `RwLock`.
- Engine event type `UdevEngineEvent`.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/pool/mod.rs

Purpose: Central pool D-Bus registration and unregistration module.

Key behavior:
- Declares pool revision modules r0 through r9 plus shared helpers.
- Reexports `PoolR0` through `PoolR9`.
- `register_pool` allocates a unique object path under `STRATIS_BASE_PATH` using the atomic counter.
- Registers every pool interface revision on that path.
- Adds the pool UUID/path mapping to `Manager`.
- Registers existing filesystems and block devices belonging to the pool.
- Returns the pool path and blockdev paths.

Unregistration:
- Looks up and removes the pool path/UUID mapping from `Manager`.
- Removes every pool revision interface from the object server.
- Returns the pool UUID.

Important detail:
- Registration failures for individual interface revisions are warnings, not fatal.
- Failure to find the pool after engine start is fatal.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_0/methods.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_0/methods.rs

Purpose: Implements the base pool r0 method behavior reused by many later pool interfaces.

Major capabilities:
- Create filesystems, limited to one filesystem per call.
- Destroy filesystems and unregister their D-Bus objects.
- Snapshot a filesystem and register the snapshot object.
- Add data devices.
- Initialize cache and add cache devices.
- Rename pool.
- Bind, rebind, and unbind Clevis and keyring encryption metadata.

Common pattern:
- Looks up mutable pool guard from the engine by `PoolUuid`.
- Uses `tokio::task::spawn_blocking` for blocking engine/pool operations.
- Wraps engine actions with `handle_action!`.
- Converts results into D-Bus `(result, return_code, return_string)` tuples.
- Registers new blockdev/filesystem D-Bus objects after successful engine changes.
- Emits property change signals for affected pool/filesystem/blockdev properties.

Notable details:
- Filesystem sizes are accepted as strings and parsed into `u128` byte counts.
- Destroying filesystems emits origin update signals for affected origins.
- Rename emits pool name changes and filesystem devnode invalidation signals.
- Encryption bind/unbind operations track free token slot changes and emit keyring/Clevis/free-slot signals.
- r0 encryption methods use `OptionalTokenSlotInput::Legacy`.

Failure handling:
- Engine absence, parsing failures, join errors, and engine errors are converted to D-Bus error tuples.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_0/methods.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_0/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_0/mod.rs

Purpose: Defines the `org.storage.stratis3.pool.r0` D-Bus interface.

Key behavior:
- Registers/unregisters `PoolR0` instances at per-pool object paths.
- Stores connection, engine, manager registry, object-path counter, and pool UUID.
- Exposes r0 pool methods from local `methods.rs`.

Exposed methods:
- Filesystem create/destroy/snapshot.
- Data/cache device add and cache initialization.
- Pool rename.
- Clevis/keyring bind, rebind, and unbind.

Exposed properties:
- `uuid`, `name`, `encrypted`, `available_actions`.
- `key_description`, `clevis_info`, `has_cache`.
- `total_physical_size`, `total_physical_used`, `allocated_size`.

Implementation note:
- Property getters use shared `pool_prop` to fetch a read guard and map missing pools to D-Bus errors.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_0/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_0/props.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_0/props.rs

Purpose: Implements r0 pool property adapters.

Properties:
- `name_prop`: extracts engine pool name.
- `size_prop`: total physical size as decimal string.
- `used_prop`: optional total used as `(bool, String)`.
- `allocated_prop`: allocated size as decimal string.
- `encrypted_prop`: encryption status.
- `avail_actions_property`: available action flags.
- `key_description_property`: legacy and newer encryption key description shape.
- `clevis_info_property`: legacy and newer Clevis info shape.
- `has_cache_property`: cache presence.

Important detail:
- Handles both legacy encryption info and newer per-token encryption info through `Either`.
- Uses D-Bus option encoding helpers to represent optional nested values.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_0/props.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_1/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_1/mod.rs

Purpose: Defines `org.storage.stratis3.pool.r1`.

Key behavior:
- Registers/unregisters `PoolR1` on per-pool object paths.
- Reuses r0 methods and properties.
- Adds r1 property support from local `props.rs`.

Version-specific additions:
- `fs_limit` readable/writable property.
- `overprovisioning` readable/writable property.
- `no_alloc_space` readable property.

Implementation note:
- Mutable properties use `set_pool_prop`, which obtains a write guard, applies the setter, and emits the corresponding signal on change.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_1/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_1/props.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_1/props.rs

Purpose: Implements r1 pool property adapters and setter signal hooks.

Properties:
- `fs_limit_prop`: returns pool filesystem limit.
- `enable_overprovisioning_prop`: returns overprovisioning mode.
- `no_alloc_space_prop`: returns whether the pool is out of allocation space.

Setters:
- `set_fs_limit_prop` calls `p.set_fs_limit(&name, uuid, fs_limit)`.
- `set_enable_overprovisioning_prop` calls `p.set_overprov_mode(&name, enable_overprov)`.

Signal hooks:
- `send_fs_limit_signal_on_change` emits the fs-limit property signal for the pool path.
- `send_enable_overprovisioning_signal_on_change` emits overprovisioning change signal.
- Missing pool path is logged as a warning.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_1/props.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_2/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_2/mod.rs

Purpose: Defines `org.storage.stratis3.pool.r2`.

Key behavior:
- Registers/unregisters `PoolR2`.
- Reuses r0 methods and r1 mutable property behavior.
- Exposes the same method/property set as r1 in this file.

Version-specific note:
- No local methods or props are introduced.
- This is a compatibility revision wrapper over r1 behavior.

Dependencies:
- r0 method/property helpers.
- r1 property and setter helpers.
- Shared `pool_prop` and `set_pool_prop`.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_2/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_3/methods.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_3/methods.rs

Purpose: Implements r3 `grow_physical_device_method`.

Key behavior:
- Parses block device UUID from string.
- Looks up mutable pool by UUID.
- Calls `pool.grow_physical(&name, pool_uuid, dev)`.
- Runs the engine action through `handle_action!`.
- Sends pool foreground diff signals when a diff is returned.
- Emits blockdev physical-size signal for the grown device.

Return semantics:
- Changed action returns `(true, OK, OK_STRING)`.
- Identity/no-change returns `(false, OK, OK_STRING)`.
- Parse, engine, and task errors are converted to D-Bus error tuples.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_3/methods.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_3/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_3/mod.rs

Purpose: Defines `org.storage.stratis3.pool.r3`.

Key behavior:
- Registers/unregisters `PoolR3`.
- Reuses r0 pool lifecycle/encryption methods.
- Reuses r1 properties.
- Adds `grow_physical_device(dev)` using local r3 method implementation.

Version-specific addition:
- Public D-Bus method for growing a physical device by device UUID string.

Dependencies:
- `pool_3_3::methods::grow_physical_device_method`.
- r0 and r1 helper functions.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_3/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_4/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_4/mod.rs

Purpose: Defines `org.storage.stratis3.pool.r4`.

Key behavior:
- Registers/unregisters `PoolR4`.
- Reuses r0 methods and properties.
- Reuses r1 filesystem-limit and overprovisioning properties.
- Reuses r3 physical-device growth method.

Version-specific note:
- No new local methods or properties are introduced.
- r4 preserves the r3 interface surface under a new revision name.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_4/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_5/methods.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_5/methods.rs

Purpose: Implements r5 `init_cache_method`.

Key behavior:
- Looks up mutable pool by UUID.
- Converts supplied `PathBuf` devices to borrowed paths.
- Calls `pool.init_cache(pool_uuid, name, devices, true)`.
- Emits has-cache signal on successful cache initialization.
- Registers new cache blockdev objects and returns their paths.

Version-specific note:
- Differs from r0 `init_cache_method`, which calls `pool.init_cache(..., false)`.
- This revision changes engine behavior while keeping the D-Bus method result shape.

Failure handling:
- Missing pool, engine errors, and task join errors become D-Bus error tuples.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_5/methods.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_5/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_5/mod.rs

Purpose: Defines `org.storage.stratis3.pool.r5`.

Key behavior:
- Registers/unregisters `PoolR5`.
- Reuses most r0 methods.
- Uses local r5 `init_cache_method`.
- Reuses r1 properties and r3 physical growth.

Version-specific addition:
- `init_cache` now delegates to the r5 implementation, which passes `true` to the engine cache initialization call.

Dependencies:
- `pool_3_5::methods::init_cache_method`.
- r0/r1/r3 helper functions.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_5/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_6/methods.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_6/methods.rs

Purpose: Implements r6 `create_filesystems_method`.

Key behavior:
- Accepts `FilesystemSpec`, whose entries include name, optional size, and optional size limit.
- Still rejects creation of more than one filesystem per call.
- Parses size and size-limit strings to `u128` and wraps them in `Bytes`.
- Calls `pool.create_filesystems` with `(name, size, size_limit)` tuples.
- Registers created filesystems on D-Bus.

Version-specific note:
- Adds filesystem size-limit support compared with r0.
- If filesystem D-Bus registration fails after engine creation, it logs a warning but continues returning success with whatever paths were registered.

Failure handling:
- Invalid size strings return D-Bus error status.
- Engine and task errors are converted through `engine_to_dbus_err_tuple`.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_6/methods.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_6/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_6/mod.rs

Purpose: Defines `org.storage.stratis3.pool.r6`.

Key behavior:
- Registers/unregisters `PoolR6`.
- Uses r6 `create_filesystems` with size-limit capable `FilesystemSpec`.
- Reuses r0 destroy/snapshot/add/rename/encryption methods.
- Uses r5 cache initialization.
- Reuses r1 properties and r3 grow method.

Version-specific addition:
- D-Bus create-filesystems signature changes from `Vec<(&str, (bool, &str))>` to `FilesystemSpec<'_>`.

Dependencies:
- `dbus::types::FilesystemSpec`.
- `pool_3_6::methods::create_filesystems_method`.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_6/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_7/methods.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_7/methods.rs

Purpose: Implements r7 metadata retrieval methods.

Methods:
- `metadata_method(engine, pool_uuid, current)`.
- `filesystem_metadata_method(engine, pool_uuid, fs_name, current)`.

Key behavior:
- Looks up pool by UUID with read access.
- Runs metadata access in `spawn_blocking`.
- `current == true` returns current metadata.
- `current == false` returns last metadata.
- Filesystem metadata accepts optional filesystem name.

Return semantics:
- Returns metadata JSON/string with OK status on success.
- Missing pool, engine metadata errors, and join errors are converted to D-Bus error tuples.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_7/methods.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_7/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_7/mod.rs

Purpose: Defines `org.storage.stratis3.pool.r7`.

Key behavior:
- Registers/unregisters `PoolR7`.
- Reuses r6 filesystem creation, r5 cache initialization, r3 grow, r1 properties, and r0 base methods.
- Adds `metadata(current)` and `filesystem_metadata(fs_name, current)` methods.

Version-specific addition:
- Read-only pool and filesystem metadata inspection becomes available over D-Bus.

Dependencies:
- `pool_3_7::{metadata_method, filesystem_metadata_method}`.
- `FilesystemSpec`.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_7/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_8/methods.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_8/methods.rs

Purpose: Implements token-slot aware r8 encryption methods.

Methods:
- `bind_clevis_method`
- `bind_keyring_method`
- `rebind_clevis_method`
- `rebind_keyring_method`
- `unbind_clevis_method`
- `unbind_keyring_method`

Key behavior:
- Accepts optional token-slot tuples for bind/rebind/unbind operations.
- For omitted token slots, chooses `Legacy` for metadata version V1 and `None` for metadata version V2.
- Tracks free token slots before and after modifications.
- Tracks the lowest legacy token slot and whether encryption info is the newer per-token representation.
- Emits Clevis/keyring property signals only when the externally visible property should change.
- Emits free-token-slots signals when token slot availability changes.

Failure handling:
- Bad Clevis JSON, missing pool, engine errors, and task join errors convert to D-Bus error tuples.
- Rebinding keyring with no source returns a specific D-Bus error string.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_8/methods.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_8/mod.rs -->
# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_8/mod.rs

Purpose: Defines `org.storage.stratis3.pool.r8`.

Key behavior:
- Registers/unregisters `PoolR8`.
- Reuses r6 filesystem creation, r5 cache initialization, r7 metadata methods, r3 grow, and r1 properties.
- Uses local r8 token-slot aware encryption methods.

Version-specific additions:
- Encryption methods accept optional token-slot parameters.
- Replaces older `key_description` and `clevis_info` properties with richer `key_descriptions` and `clevis_infos` zvariant values.
- Adds `free_token_slots`, `volume_key_loaded`, and `metadata_version` properties.
- `volume_key_loaded` emits no changed signal.
- `metadata_version` is const.

Dependencies:
- Local `methods.rs` and `props.rs`.
- `zbus::zvariant::Value` for richer property payloads.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/dbus/pool/pool_3_8/mod.rs -->