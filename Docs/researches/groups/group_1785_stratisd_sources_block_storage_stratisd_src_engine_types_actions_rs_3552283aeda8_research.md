# Group Research: group_1785_stratisd_sources_block_storage_stratisd_src_engine_types_actions_rs_3552283aeda8

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/block-storage/stratisd`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/types/actions.rs -->
# File Research: sources/block-storage/stratisd/src/engine/types/actions.rs

## Purpose

Defines idempotent action result types used across the Stratis engine, pool, filesystem, blockdev, encryption, key, and property APIs. The file centralizes the contract that an operation can succeed while either changing state or proving the requested state was already true.

## Main Types and Behavior

- `EngineAction` is the shared trait for action results. It exposes `is_changed()` and consuming `changed()` so callers can decide whether an operation had an externally reportable effect.
- `CreateAction<T>` represents single-object creation as `Created(T)` or `Identity`.
- `MappingCreateAction<T>` adds `ValueChanged(T)` for key-value stores where the key may exist but the value changes.
- `MappingDeleteAction<T>` and `DeleteAction<T>` represent idempotent removals.
- `SetUnlockAction<T>`, `SetCreateAction<T>`, and `SetDeleteAction<T, U>` model multi-item changes and return vectors only when non-empty.
- `RenameAction<T>` distinguishes `Identity`, `Renamed(T)`, and `NoSource`.
- `StartAction<T>`, `StopAction<T>`, and `GrowAction<T>` model lifecycle and resize outcomes.
- `PropChangeAction<T>` represents property update idempotency, with `ToDisplay` helpers for optional and boolean values.
- Marker structs `Key`, `Clevis`, `EncryptedDevice`, `ReencryptedDevice`, and `RegenAction` provide typed return payloads and user-facing formatting for encryption/key operations.

## Integration Points

The JSON-RPC server and engine code use `EngineAction::is_changed()` heavily to convert engine results into boolean IPC status values. Display implementations provide CLI/API messages for pool creation/deletion, filesystem/snapshot creation, device add/grow, pool start/stop, encryption/decryption, keyring/Clevis binding, and property changes.

## Notable Semantics

`SetUnlockAction::Started(Vec<T>)` can mean the pool started even when no individual devices are newly reported; in that case `is_changed()` is false if the vector is empty. `StopAction::is_changed()` only returns true for `Stopped(_)`, not `CleanedUp(_)` or `Partial(_)`, which is a subtle contract for callers interpreting stop results.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/types/actions.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/types/diff.rs -->
# File Research: sources/block-storage/stratisd/src/engine/types/diff.rs

## Purpose

Provides generic and Stratis-specific structures for reporting state differences between old and new engine snapshots.

## Main Types and Behavior

- `Compare` is implemented for any `PartialEq + Clone` type and returns `Diff::Changed(new)` or `Diff::Unchanged(new)`.
- `Diff<T>` stores the current value in both variants, supports `is_changed()`, `changed()`, `Deref`, and `DerefMut`.
- `ThinPoolDiff` tracks thin pool `allocated_size` and `used`.
- `StratPoolDiff` tracks pool physical size, metadata size, and allocation-space exhaustion.
- `StratFilesystemDiff` tracks filesystem size and used space.
- `PoolDiff` groups thin-pool and pool-level diffs.
- `StratBlockDevDiff` tracks block device size changes.

## Integration Points

These types are used by background event processing and IPC notification paths to determine whether pool, filesystem, or blockdev attributes need to be reported.

## Notable Semantics

`Diff<T>` keeps the updated value even when unchanged, allowing downstream calculations to use a uniform dereference path without separately carrying a current-state value.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/types/diff.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/types/keys.rs -->
# File Research: sources/block-storage/stratisd/src/engine/types/keys.rs

## Purpose

Defines encryption, unlock, token-slot, and key-description data structures used by Stratis pool encryption metadata and unlock operations.

## Main Types and Behavior

- `SizedKeyMemory` wraps `libcryptsetup_rs::SafeMemHandle` with an explicit size and exposes only the active byte slice.
- `UnlockMechanism` is either `KeyDesc(KeyDescription)` or `ClevisInfo(ClevisInfo)`, with accessors and type predicates.
- `InputEncryptionInfo` stores user-supplied encryption/unlock mechanisms with optional token slots. It supports legacy fixed-token construction, validation against duplicate explicit token slots, and conversion into grouped parts.
- `EncryptionInfo` stores actual token-slot-to-unlock-mechanism mappings. It supports adding, setting, removing, listing, finding free slots, counting free token slots, diffing token-slot presence, JSON conversion, and display formatting.
- `PoolEncryptionInfo` summarizes key/Clevis encryption information across pool devices, preserving inconsistency using `MaybeInconsistent`.
- `KeyDescription` validates kernel keyring descriptions by rejecting semicolons, because semicolons conflict with kernel describe-string parsing.
- `VolumeKeyKeyDescription` reserves a key description namespace for pool volume keys.
- `UnlockMethod`, `OptionalTokenSlotInput`, and `TokenUnlockMethod` model legacy unlock choices, optional explicit token slot assignment, and unlock token selection.

## Integration Points

This file bridges CLI/API encryption arguments, on-disk metadata compatibility, libcryptsetup token slots, pool encryption state, and keyring/Clevis unlock flows. JSON-RPC client/server pool methods pass `InputEncryptionInfo`, `OptionalTokenSlotInput`, `TokenUnlockMethod`, and `KeyDescription`.

## Notable Semantics

Legacy metadata requires fixed token slots for keyring and Clevis. Newer paths allow optional or explicit slots. `PoolEncryptionInfo::from` over multiple `EncryptionInfo` values marks fields inconsistent when devices disagree, preventing callers from silently treating mixed metadata as authoritative.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/types/keys.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/types/mod.rs -->
# File Research: sources/block-storage/stratisd/src/engine/types/mod.rs

## Purpose

Acts as the public type hub for engine-wide Stratis identifiers, action result types, diff types, encryption/key types, udev event wrappers, pool discovery records, and integrity configuration.

## Main Types and Behavior

- Re-exports action, diff, key, engine state, lockable, and error/result types.
- Defines typed UUID wrappers with the `uuid!` macro: `DevUuid`, `FilesystemUuid`, and `PoolUuid`.
- `StratisUuid` unifies device, filesystem, and pool UUIDs behind `Deref<Target = Uuid>` and `Display`.
- `Name` wraps pool/filesystem names and supports string borrowing, display, hashing, and serde.
- `ReportType` currently exposes `StoppedPools`.
- `PoolDevice`, `LockedPoolInfo`, `LockedPoolsInfo`, `StoppedPoolInfo`, `StoppedPoolsInfo`, and `Features` represent discovered locked/stopped pool state.
- `UdevEngineEvent` and `UdevEngineDevice` snapshot libudev event/device data into sendable engine-owned structures.
- `DevicePath` canonicalizes and wraps a device path.
- `ActionAvailability` models increasingly restrictive pool action states.
- `MaybeInconsistent<T>` represents metadata disagreement across devices.
- `PoolIdentifier<U>` supports name-or-UUID lookup and display.
- `UuidOrConflict` handles ambiguous name-to-UUID mappings.
- `StratSigblockVersion` validates V1/V2 metadata versions.
- `IntegrityTagSpec`, `IntegritySpec`, and `ValidatedIntegritySpec` define and validate dm-integrity metadata defaults.

## Integration Points

This module is imported widely by engine, JSON-RPC, D-Bus, and daemon runtime code. It is the type-level contract between Stratis engine internals and IPC layers.

## Notable Semantics

`UuidOrConflict` maintains an invariant that conflict sets have more than one UUID and collapses back to a single UUID when removals leave one member. `ValidatedIntegritySpec` enforces 4096-byte journal-size alignment and fills defaults for tag spec, block size, and superblock allocation.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/types/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/client/client.rs -->
# File Research: sources/block-storage/stratisd/src/jsonrpc/client/client.rs

## Purpose

Implements the minimal Unix-socket JSON-RPC client transport used by `stratis-min`.

## Main Types and Behavior

- `send_request` serializes a request to JSON, optionally sends one file descriptor with `SCM_RIGHTS`, reads up to 65536 bytes of response data, and deserializes it.
- `StratisClient` wraps a `UnixStream`.
- `StratisClient::connect` connects to the configured socket path.
- `StratisClient::request` sends a `StratisParams` request and returns an `IpcResult<StratisRet>`.

## Integration Points

The request macros in `client/utils.rs` use `StratisClient` for all key, pool, filesystem, and report operations. FD passing supports keyfile/passphrase transfer.

## Notable Semantics

Responses are read with a fixed 64 KiB buffer and one read call, so this protocol assumes responses fit in one read.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/client/client.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/client/filesystem.rs -->
# File Research: sources/block-storage/stratisd/src/jsonrpc/client/filesystem.rs

## Purpose

Provides client-side wrappers for `stratis-min filesystem` commands.

## Main Types and Behavior

- `filesystem_create`, `filesystem_destroy`, and `filesystem_rename` use `do_request_standard!` and require a changed result.
- `filesystem_list` requests `FsList`, formats used bytes, device paths, UUIDs, and prints a table.
- `filesystem_origin` requests `FsOrigin`, converts nonzero return codes to `StratisError`, and returns `"None"` when no origin exists.

## Integration Points

Maps CLI-style filesystem operations to `StratisParamType::Fs*` requests and presents response tuples in terminal-friendly output.

## Notable Semantics

A missing `used` value is displayed as `FAILURE`, preserving partial list output while signaling a failed usage query.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/client/filesystem.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/client/key.rs -->
# File Research: sources/block-storage/stratisd/src/jsonrpc/client/key.rs

## Purpose

Implements client-side key management commands for setting, unsetting, and listing kernel key descriptions.

## Main Types and Behavior

- `key_set` either opens a provided keyfile or prompts for a verified passphrase.
- Prompted passphrases are written into a pipe and the read file descriptor is sent over JSON-RPC.
- The return value is `Option<bool>`: `None` means no effect, `Some(false)` means newly created, and `Some(true)` means changed existing value.
- `key_unset` uses standard changed-result handling.
- `key_list` prints key descriptions in a table.

## Integration Points

Uses `KeyDescription`, password prompting from `client/utils.rs`, FD passing from request macros, and server-side `key_set`.

## Notable Semantics

For interactive `key_set`, empty password input is rejected before any request is sent.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/client/key.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/client/mod.rs -->
# File Research: sources/block-storage/stratisd/src/jsonrpc/client/mod.rs

## Purpose

Declares and exports the JSON-RPC client module tree.

## Main Types and Behavior

- Exposes macro-bearing `utils`.
- Declares `client`, `filesystem`, `key`, `pool`, and `report`.
- Re-exports `StratisClient`.

## Integration Points

Used by the min JSON-RPC frontend and request macros.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/client/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/client/pool.rs -->
# File Research: sources/block-storage/stratisd/src/jsonrpc/client/pool.rs

## Purpose

Provides client-side wrappers for `stratis-min pool` operations.

## Main Types and Behavior

- Supports pool create, start, stop, cache initialization, rename, data/cache add, destroy, list, encryption-state queries, and keyring/Clevis bind/unbind/rebind.
- `pool_start` can prompt for a password and pass it through a pipe FD.
- `pool_list` formats physical size as total/used/free and prints property flags for cache/encryption.
- Query helpers return booleans after checking JSON-RPC return codes.

## Integration Points

Maps CLI operations to `StratisParamType::Pool*` variants using shared request macros. Encryption operations use `PoolIdentifier`, `OptionalTokenSlotInput`, `KeyDescription`, `TokenUnlockMethod`, and JSON Clevis config.

## Notable Semantics

`properties_string` uses compact `Ca/~Ca` and `Cr/~Cr` flags for cache and encryption. `size_string` displays `FAILURE` when used/free values are unavailable.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/client/pool.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/client/report.rs -->
# File Research: sources/block-storage/stratisd/src/jsonrpc/client/report.rs

## Purpose

Provides the client-side report request.

## Main Types and Behavior

- `report()` sends `Report` and returns a `serde_json::Value`.

## Integration Points

Used by min JSON-RPC clients that need the engine state report directly as JSON.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/client/report.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/client/utils.rs -->
# File Research: sources/block-storage/stratisd/src/jsonrpc/client/utils.rs

## Purpose

Contains JSON-RPC client request macros, table formatting macros, byte-size formatting, and passphrase prompting utilities.

## Main Types and Behavior

- `do_request!` connects to the RPC socket, builds `StratisParams`, optionally attaches an FD, checks response variant matching, and returns the typed payload.
- `do_request_standard!` expects `(changed, rc, rs)` tuples and converts nonzero return codes or unchanged results into `StratisError`.
- `left_align!`, `right_align!`, `align!`, and `print_table!` format aligned terminal tables.
- `to_suffix_repr` formats byte counts using binary suffixes down to two decimal places.
- `get_pass` disables terminal echo for TTY input, restores terminal settings, trims trailing newline, and returns `None` for empty input.
- `prompt_password` optionally verifies two passphrase entries.

## Integration Points

All client pool/filesystem/key wrappers depend on these macros and helpers.

## Notable Semantics

The table macro enforces equal-length columns. `to_suffix_repr` intentionally truncates/rounds down two decimal places to avoid misleading unit promotion near boundaries.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/client/utils.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/consts.rs -->
# File Research: sources/block-storage/stratisd/src/jsonrpc/consts.rs

## Purpose

Defines constants for the min JSON-RPC protocol.

## Main Types and Behavior

- `OP_OK` is `0`.
- `OP_ERR` is `1`.
- `OP_OK_STR` is `"OK"`.
- `RPC_SOCKADDR` is `/run/stratisd/stratisd-min-jsonrpc`.

## Integration Points

Used by client/server utilities and socket listener setup.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/consts.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/interface.rs -->
# File Research: sources/block-storage/stratisd/src/jsonrpc/interface.rs

## Purpose

Defines the serialized request and response protocol between min JSON-RPC client and server.

## Main Types and Behavior

- `PoolListType` and `FsListType` are tuple aliases for list responses.
- `StratisParamType` enumerates all supported key, pool, filesystem, and report requests.
- `StratisParams` combines a serialized request type with an optional received file descriptor.
- `IpcResult<T>` is `Result<T, String>`.
- `StratisRet` enumerates all response variants and their payload tuple shapes.

## Integration Points

Both client macros and server dispatch pattern-match these variants. The request and response variant names must stay synchronized.

## Notable Semantics

File descriptors are intentionally not serialized; `StratisParams` carries `fd_opt` out-of-band after socket ancillary-data handling.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/interface.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/mod.rs -->
# File Research: sources/block-storage/stratisd/src/jsonrpc/mod.rs

## Purpose

Declares the JSON-RPC module tree and public exports.

## Main Types and Behavior

- Exposes `client`.
- Keeps `consts`, `interface`, and `server` internal to the module.
- Re-exports constants and `run_server`.

## Integration Points

The daemon IPC support imports `jsonrpc::run_server`; client code imports through `jsonrpc::client`.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/server/filesystem.rs -->
# File Research: sources/block-storage/stratisd/src/jsonrpc/server/filesystem.rs

## Purpose

Implements server-side filesystem operations for the min JSON-RPC API.

## Main Types and Behavior

- `filesystem_create` resolves a pool by name, obtains a mutable pool guard, and calls `create_filesystems`.
- `filesystem_list` walks all pools and accumulates pool names, filesystem names, used bytes, creation timestamps, devnodes, and UUIDs.
- `filesystem_destroy` resolves filesystem UUID by name and calls `destroy_filesystems`.
- `filesystem_rename` resolves filesystem UUID and calls `rename_filesystem`.
- `filesystem_origin` returns the origin UUID as a simple string if present.

## Integration Points

Called from `StratisParams::process` in `server/server.rs`. Blocking pool operations are wrapped with `tokio::task::block_in_place`.

## Notable Semantics

Lookup failures produce explicit `StratisError::Msg` values naming the missing pool or filesystem.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/server/filesystem.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/server/key.rs -->
# File Research: sources/block-storage/stratisd/src/jsonrpc/server/key.rs

## Purpose

Implements server-side key management for min JSON-RPC.

## Main Types and Behavior

- `key_set` delegates to the engine key handler with a received FD and maps `MappingCreateAction` to `Option<bool>`.
- `key_unset` delegates to the key handler and maps deletion identity to false.
- `key_list` collects key descriptions from the engine key handler.

## Integration Points

Consumes file descriptors validated by `expects_fd!` in request dispatch. It is the server counterpart to `client/key.rs`.

## Notable Semantics

`key_set` uses `Some(false)` for first creation, `Some(true)` for value update, and `None` for identity.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/server/key.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/server/mod.rs -->
# File Research: sources/block-storage/stratisd/src/jsonrpc/server/mod.rs

## Purpose

Declares the JSON-RPC server module tree.

## Main Types and Behavior

- Imports server-side utility macros.
- Declares filesystem, key, pool, report, and module-inception `server`.
- Re-exports `run_server`.

## Integration Points

Used by `jsonrpc/mod.rs` and IPC setup.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/server/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/server/pool.rs -->
# File Research: sources/block-storage/stratisd/src/jsonrpc/server/pool.rs

## Purpose

Implements server-side pool operations for min JSON-RPC.

## Main Types and Behavior

- Pool lifecycle: `pool_create`, `pool_destroy`, `pool_start`, `pool_stop`, `pool_rename`.
- Device operations: `pool_init_cache`, `pool_add_data`, `pool_add_cache`, internal `add_blockdevs`.
- Listing: `pool_list` returns names, physical total/used, cache/encryption flags, and UUIDs.
- Encryption bindings: bind/unbind/rebind keyring and Clevis.
- State queries: `pool_is_encrypted`, `pool_is_stopped`, `pool_has_passphrase`, and `pool_is_bound`.

## Integration Points

Called from `StratisParams::process`. It translates engine action enums into boolean changed status for the min protocol.

## Notable Semantics

Stopped-pool queries inspect both active engine pools and `engine.stopped_pools()`. For V1 stopped metadata, encryption is inferred from presence of encryption info; for V2 it is read from `features`. Passphrase and Clevis queries handle both current `EncryptionInfo` and legacy/inconsistent `PoolEncryptionInfo`.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/server/pool.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/server/report.rs -->
# File Research: sources/block-storage/stratisd/src/jsonrpc/server/report.rs

## Purpose

Implements the server-side report endpoint.

## Main Types and Behavior

- `report` returns `engine.engine_state_report()` as JSON.

## Integration Points

Called by `StratisParamType::Report` dispatch and returned directly as `StratisRet::Report`.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/server/report.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/server/server.rs -->
# File Research: sources/block-storage/stratisd/src/jsonrpc/server/server.rs

## Purpose

Implements the min JSON-RPC Unix socket server, including request dispatch, ancillary FD handling, async listener/request/response futures, and server startup.

## Main Types and Behavior

- `StratisParams::process` is the central dispatcher from `StratisParamType` to server handlers.
- `StratisServer` owns the engine and Unix listener, accepts requests, spawns per-request tasks, and sends responses.
- `handle_cmsgs` extracts at most one `SCM_RIGHTS` file descriptor and closes extras on protocol violation.
- `try_recvmsg` receives JSON plus optional FD and builds `StratisParams`.
- `try_sendmsg` serializes and sends the response.
- `StratisUnixRequest` waits for read readiness and deserializes a request.
- `StratisUnixResponse` waits for write readiness and sends a response.
- `StratisUnixListener` binds a nonblocking Unix stream socket, creating/removing the socket path as needed.
- `run_server` spawns the server task on the configured socket path.

## Integration Points

This is the transport and dispatch backbone for `stratis-min`. It integrates with the engine, server pool/key/filesystem/report modules, systemd readiness notification, and JSON-RPC constants/interface types.

## Notable Semantics

`expects_fd!` enforces FD expectations per method. Unexpected FDs are closed before returning protocol errors. The listener uses `listen` backlog `0`, so connection queuing behavior is intentionally minimal.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/server/server.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/server/utils.rs -->
# File Research: sources/block-storage/stratisd/src/jsonrpc/server/utils.rs

## Purpose

Provides server-side JSON-RPC utility macro and result conversion helper.

## Main Types and Behavior

- `expects_fd!` validates whether a method requires or forbids a received file descriptor.
- If an FD is forbidden but received, the macro attempts to close it and returns a protocol error.
- `stratis_result_to_return` converts `StratisResult<T>` into `(T, rc, message)` tuples using `OP_OK`, `OP_ERR`, and `OP_OK_STR`.

## Integration Points

Used by `server/server.rs` dispatch for every request returning a standard tuple.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/jsonrpc/server/utils.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/lib.rs -->
# File Research: sources/block-storage/stratisd/src/lib.rs

## Purpose

Defines the crate-level feature-gated module surface and macro imports.

## Main Types and Behavior

- Imports macro crates under `engine` feature: `nix`, `serde_derive`, `log`, `serde_json`, `libcryptsetup_rs`.
- Test-only macro imports include `proptest` and `assert_matches`.
- Declares internal `macros` under `engine`.
- Exposes `engine`, `dbus`, `stratis`, `jsonrpc`, and `systemd` according to features.

## Integration Points

Controls whether the full engine, D-Bus API, min JSON-RPC API, and systemd compatibility modules are compiled.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/lib.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/macros.rs -->
# File Research: sources/block-storage/stratisd/src/macros.rs

## Purpose

Defines crate-local helper macros for async testing and blocking task spawning.

## Main Types and Behavior

- `test_async!` builds a current-thread Tokio runtime with a `LocalSet` for tests.
- `spawn_blocking!` wraps `tokio::task::spawn_blocking`, awaits the join, and maps join errors into `StratisError`.

## Integration Points

Used under the engine feature by tests and code that needs a compact blocking-task wrapper.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/macros.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/stratis/dm.rs -->
# File Research: sources/block-storage/stratisd/src/stratis/dm.rs

## Purpose

Runs the devicemapper event monitoring task and routes device-mapper events into engine pool/filesystem event handlers.

## Main Types and Behavior

- `dm_event_thread` starts an async task when a real engine is present; with `None`, it logs that monitoring is disabled for the sim engine.
- `process_dm_event` waits for DM FD readiness, clears readiness, arms DM polling, gets engine events, and invokes pool/filesystem event processing.
- D-Bus builds send background signals for pool and filesystem diffs; min/non-D-Bus builds ignore return diffs.
- `setup_dm` initializes DM, requires minor version at least 37, adjusts FD flags, and wraps the DM FD in `AsyncFd`.

## Integration Points

Started from `stratis/run.rs` alongside udev, IPC, timer, signal, and key-loading tasks.

## Notable Semantics

The code clears async readiness without reading from the DM FD because the devicemapper library manages event state through `arm_poll()`/event APIs.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/stratis/dm.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/stratis/errors.rs -->
# File Research: sources/block-storage/stratisd/src/stratis/errors.rs

## Purpose

Defines the central `StratisError` type and `StratisResult<T>` alias.

## Main Types and Behavior

- `StratisError` covers plain messages, chained errors, best-effort rollback groups, rollback errors with action availability, no-action rollback errors, disabled actions, out-of-space, and wrapped external errors.
- `error_to_all_available_actions` walks nested error structures to collect pool action availability restrictions.
- `error_to_available_actions` returns the most restrictive availability state.
- Implements `Display`, `Error`, and `From` conversions for IO, nix, UUID, UTF-8, serde JSON, data encoding, devicemapper, cryptsetup, tokio join, blkid, udev, mpsc receive, NUL, and feature-gated D-Bus errors.

## Integration Points

This error type is used across engine, runtime, JSON-RPC, D-Bus, devicemapper, cryptsetup, udev, and systemd integration.

## Notable Semantics

Rollback-related variants carry enough structure to both report the causal and rollback failures and derive the pool action restrictions that should result.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/stratis/errors.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/stratis/ipc_support/dbus_support.rs -->
# File Research: sources/block-storage/stratisd/src/stratis/ipc_support/dbus_support.rs

## Purpose

Sets up D-Bus-specific IPC support and udev event processing.

## Main Types and Behavior

- Registers existing pools with the D-Bus udev handler at startup.
- Logs D-Bus API availability.
- Spawns a loop that calls `udev.process_udev_events()`.
- Uses `tokio::select!` to return if the udev task exits.

## Integration Points

Selected by `ipc_support/mod.rs` when `dbus_enabled` is active. Called from `stratis/run.rs`.

## Notable Semantics

If D-Bus udev processing exits, setup reports the task failure through `StratisError`.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/stratis/ipc_support/dbus_support.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/stratis/ipc_support/dummy.rs -->
# File Research: sources/block-storage/stratisd/src/stratis/ipc_support/dummy.rs

## Purpose

Provides IPC-less udev handling for builds without D-Bus and without min JSON-RPC.

## Main Types and Behavior

- Receives `UdevEngineEvent` values from a channel.
- Batches the first awaited event plus any immediately available queued events.
- Calls `engine.handle_events(events)` and ignores returned IPC-layer state.

## Integration Points

Selected only when neither `dbus_enabled` nor `min` is active.

## Notable Semantics

Channel shutdown is treated as an error because the dummy handler would no longer receive udev events.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/stratis/ipc_support/dummy.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/stratis/ipc_support/jsonrpc_support.rs -->
# File Research: sources/block-storage/stratisd/src/stratis/ipc_support/jsonrpc_support.rs

## Purpose

Sets up min JSON-RPC IPC support and udev event forwarding.

## Main Types and Behavior

- `handle_udev` spawns a task that batches udev events and calls `engine.handle_events`.
- `setup` starts both udev handling and the JSON-RPC server.
- A `tokio::select!` returns if either the udev handler or server task exits.

## Integration Points

Selected by `ipc_support/mod.rs` when `min` is active and D-Bus is not. Uses `jsonrpc::run_server`.

## Notable Semantics

JSON-RPC has no persistent IPC-side object model, so event handling ignores returned data structure updates.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/stratis/ipc_support/jsonrpc_support.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/stratis/ipc_support/mod.rs -->
# File Research: sources/block-storage/stratisd/src/stratis/ipc_support/mod.rs

## Purpose

Selects the correct IPC support implementation based on Cargo features.

## Main Types and Behavior

- Declares `dbus_support` for `dbus_enabled`.
- Declares `dummy` when neither `dbus_enabled` nor `min` is active.
- Declares `jsonrpc_support` for `min`.
- Re-exports the appropriate `setup`.

## Integration Points

Used by `stratis/run.rs` without needing feature-specific code at the call site.

## Notable Semantics

If both `dbus_enabled` and `min` are enabled for clippy, D-Bus wins for the exported `setup`.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/stratis/ipc_support/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/stratis/keys.rs -->
# File Research: sources/block-storage/stratisd/src/stratis/keys.rs

## Purpose

Runs an async task that reacts to newly added key descriptions and attempts to load volume keys for matching encrypted pools.

## Main Types and Behavior

- `load_vks` waits on an optional key-description receiver.
- For each key description, it scans active pools for encrypted pools whose encryption info contains the sent key description.
- For each matching pool UUID, it obtains a mutable pool guard and runs `load_volume_key` in a blocking task.
- Logs success, recoverable load failures, join failures, and missing pools.

## Integration Points

Started from `stratis/run.rs` with a receiver created during real `StratEngine` initialization.

## Notable Semantics

If no receiver is provided, the task awaits forever using `futures::future::pending()`, which keeps the runtime branch alive without consuming CPU.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/stratis/keys.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/stratis/mod.rs -->
# File Research: sources/block-storage/stratisd/src/stratis/mod.rs

## Purpose

Declares Stratis daemon runtime modules and re-exports the public runtime API.

## Main Types and Behavior

- Re-exports `StratisError`, `StratisResult`, `run`, and `VERSION`.
- Declares `dm`, `errors`, `ipc_support`, `keys`, `run`, module-inception `stratis`, `timer`, and `udev_monitor`.

## Integration Points

Imported by crate users and other modules as the main runtime facade.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/stratis/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/stratis/run.rs -->
# File Research: sources/block-storage/stratisd/src/stratis/run.rs

## Purpose

Implements the main daemon startup and task orchestration loop.

## Main Types and Behavior

- `signal_thread` waits for Ctrl-C/SIGINT.
- `run(sim)` optionally unshares the mount namespace, sets up crypt logging, registers Clevis token support, creates process keyring, builds a multi-thread Tokio runtime, and starts the engine.
- `start_threads` starts udev monitoring, IPC support, signal handling, devicemapper event monitoring, timed checks, and volume-key loading.
- Uses `tokio::select!` to shut down when a task exits, errors, or SIGINT arrives.
- Real mode initializes `StratEngine`; simulation mode uses `SimEngine`.

## Integration Points

This is the primary entrypoint re-exported by `stratis/mod.rs`. It wires together engine, IPC, D-Bus/min feature variants, DM, udev, timers, key management, and shutdown notification.

## Notable Semantics

If running as PID 1, the daemon skips mount namespace unsharing because container PID 1 behavior makes that unnecessary or ineffective. On shutdown, it sends a broadcast notification to blocking udev threads.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/stratis/run.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/stratis/stratis.rs -->
# File Research: sources/block-storage/stratisd/src/stratis/stratis.rs

## Purpose

Defines the daemon version constant.

## Main Types and Behavior

- `VERSION` is populated from Cargo package metadata with `env!("CARGO_PKG_VERSION")`.

## Integration Points

Re-exported by `stratis/mod.rs` and logged during daemon startup.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/stratis/stratis.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/stratis/timer.rs -->
# File Research: sources/block-storage/stratisd/src/stratis/timer.rs

## Purpose

Runs periodic background checks for pool and filesystem usage.

## Main Types and Behavior

- `check_pool_and_fs` loops forever, calling engine pool and filesystem event processing with `None` to indicate timed checks rather than DM events.
- D-Bus builds send background signals for produced diffs.
- Min/non-D-Bus builds ignore returned diffs.
- Sleeps 10 seconds between checks.
- `run_timers` spawns the check loop and awaits it.

## Integration Points

Started by `stratis/run.rs` as one of the daemon’s long-running tasks.

## Notable Semantics

Because the spawned loop never normally returns, `run_timers` only exits on task failure or cancellation.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/stratis/timer.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/stratis/udev_monitor.rs -->
# File Research: sources/block-storage/stratisd/src/stratis/udev_monitor.rs

## Purpose

Monitors udev block-device events and forwards them into the daemon’s async event channel.

## Main Types and Behavior

- `udev_thread` runs blocking udev polling in `spawn_blocking`.
- Creates a libudev context and block-subsystem monitor.
- Polls with a 100 ms timeout so it can periodically check shutdown broadcast state.
- On events, converts libudev events to `UdevEngineEvent` and sends them through an unbounded channel.
- `UdevMonitor` wraps `libudev::MonitorSocket` and implements `AsFd`.

## Integration Points

Started by `stratis/run.rs`; consumed by D-Bus, JSON-RPC, or dummy IPC support depending on feature selection.

## Notable Semantics

Shutdown notification failure due to closed or lagged broadcast receiver is treated as a daemon-shutdown error.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/stratis/udev_monitor.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/systemd/bindings.rs -->
# File Research: sources/block-storage/stratisd/src/systemd/bindings.rs

## Purpose

Includes generated systemd FFI bindings.

## Main Types and Behavior

- Suppresses naming, dead-code, FFI, and clippy lints typical of bindgen output.
- Includes `${OUT_DIR}/bindings.rs`.

## Integration Points

Used by `systemd/mod.rs` for `sd_notify` and `syslog`.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/systemd/bindings.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/systemd/mod.rs -->
# File Research: sources/block-storage/stratisd/src/systemd/mod.rs

## Purpose

Provides systemd compatibility helpers for readiness notification and syslog forwarding.

## Main Types and Behavior

- `serialize_pairs` converts key/value pairs into systemd notify payload lines.
- `notify` serializes pairs, converts to `CString`, calls `sd_notify`, and maps negative returns to IO errors.
- `syslog` converts a Rust log `Record` message to `CString` and calls system `syslog`.

## Integration Points

`jsonrpc/server/server.rs` calls `notify` with `READY=1` when systemd compatibility is enabled. Logging infrastructure can route records through `syslog`.

## Notable Semantics

`syslog` silently returns if the log message cannot be represented as a C string due to interior NUL bytes.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/systemd/mod.rs -->