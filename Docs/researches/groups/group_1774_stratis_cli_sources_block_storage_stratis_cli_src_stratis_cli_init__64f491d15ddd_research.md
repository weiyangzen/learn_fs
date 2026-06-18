# Group Research: group_1774_stratis_cli_sources_block_storage_stratis_cli_src_stratis_cli_init__64f491d15ddd

Scope: `Docs/research_subset_a.md` only. Files read completely: all 33 listed `stratis_cli` source files in this group.

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/__init__.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/__init__.py

## Role

Package initializer for `stratis_cli`. It exposes the installed CLI entry point and selected top-level error/exit helpers.

## Contents

- Imports `StratisCliEnvironmentError` from `._errors`.
- Imports `StratisCliErrorCodes` and `exit_` from `._exit`.
- Imports `run` from `._main`.

## Dependencies and Notes

This file intentionally has no runtime logic beyond imports. Its import of `run` is also used as an import-order sentinel by `_actions/_data.py`, which asserts the top-level package is initialized before generated D-Bus classes are built.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/__init__.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/__init__.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/__init__.py

## Role

Aggregator for action classes, D-Bus interface constants, daemon-version checking, and error-chain utilities. Parser modules import this package-level surface instead of each implementation module.

## Exported Surface

Re-exports:

- Action classes: `BindActions`, `RebindActions`, `CryptActions`, debug action classes, `LogicalActions`, `PhysicalActions`, `PoolActions`, `StratisActions`, `TopActions`.
- Interface constants: `BLOCKDEV_INTERFACE`, `FILESYSTEM_INTERFACE`, `MANAGER_0_INTERFACE`, `POOL_INTERFACE`.
- Helpers: `check_stratisd_version`, `get_errors`.

## Notable Behavior

This centralizes parser dependencies on the action layer. Because importing actions can cascade into D-Bus support modules, additions here should be checked for circular/import-order pressure with `_actions/_data.py` and `_error_reporting.py`.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/__init__.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_bind.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_bind.py

## Role

Implements encryption binding operations for pools: bind, rebind, and unbind using Clevis or kernel keyring credentials.

## Main Behavior

- `_get_pool_id()` normalizes parser namespaces that identify pools either by legacy positional `pool_name` or by `--name`/`--uuid`.
- `BindActions.bind_clevis()` JSON-serializes Clevis config and calls `Pool.Methods.BindClevis`.
- `BindActions.bind_keyring()` calls `Pool.Methods.BindKeyring` with a key description.
- `BindActions.unbind()` selects `UnbindClevis` or `UnbindKeyring` from `EncryptionMethod` and optionally passes `token_slot`.
- `RebindActions.rebind_clevis()` and `rebind_keyring()` invoke corresponding rebind methods, also with optional token-slot targeting.

## Error Handling

Non-OK stratisd return codes become `StratisCliEngineError`; unchanged results become `StratisCliNoChangeError`. Pool lookup failures are left to generated managed-object query errors and interpreted later by `_error_reporting.py`.

## Notable Risk Areas

The same action code serves legacy and newer parser paths, so namespace shape matters. Token slot arguments are passed as D-Bus optional tuples and must remain aligned with stratisd API expectations.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_bind.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_connection.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_connection.py

## Role

Provides shared low-level D-Bus connection access for action modules.

## Main Components

- `Bus._BUS` stores a lazy singleton `dbus.SystemBus()`.
- `Bus.get_bus()` initializes and returns the system bus.
- `get_object(object_path)` returns a non-introspecting proxy for the Stratis service and object path.

## Dependencies and Notes

Uses `SERVICE` from `_actions/_constants.py`. D-Bus connection failures propagate as D-Bus exceptions for centralized reporting.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_connection.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_constants.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_constants.py

## Role

Defines D-Bus service, object path, interface names, sector size, and supported daemon version bounds for the action layer.

## Constants

- `SERVICE = "org.storage.stratis3"`.
- `TOP_OBJECT = "/org/storage/stratis3"`.
- `SECTOR_SIZE = 512`.
- `MINIMUM_STRATISD_VERSION = "3.9.0"`.
- `MAXIMUM_STRATISD_VERSION = "4.0.0"`.
- `REVISION` derives from the minimum version minor component, yielding `r9`.
- Interface constants cover blockdev, filesystem, manager, pool, report, and legacy `Manager.r0`.

## Notable Behavior

The CLI is pinned to stratisd 3.9.x-compatible D-Bus interfaces and refuses stratisd 4.0.0 or later via `_stratisd_version.py`.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_constants.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_crypt.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_crypt.py

## Role

Implements whole-pool encryption state changes: encrypt an unencrypted pool, decrypt an encrypted pool, and reencrypt an encrypted pool.

## Main Behavior

- `encrypt()` requires `--in-place`, rejects already encrypted pools, builds optional keyring/Clevis credential lists, and calls `Pool.Methods.EncryptPool`.
- `unencrypt()` requires `--in-place`, rejects already unencrypted pools, and calls `Pool.Methods.DecryptPool`.
- `reencrypt()` requires `--in-place` and calls `Pool.Methods.ReencryptPool`.

## Safety and Error Handling

All methods use `long_running_operation()` for expected D-Bus `NoReply` behavior on long operations. Missing `--in-place` raises `StratisCliInPlaceNotSpecified`; non-OK daemon results raise `StratisCliEngineError`; unexpected unchanged success paths raise `StratisCliIncoherenceError`.

## Notable Risk Areas

These commands are high-impact and rely on parser opt-in, action prechecks, daemon return codes, and timeout/long-operation handling staying consistent.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_crypt.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_data.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_data.py

## Role

Generates Python D-Bus client classes and managed-object query helpers from embedded introspection XML.

## Generated Objects

Creates `Report`, `Filesystem`, `MOFilesystem`, `filesystems`, `Pool`, `MOPool`, `pools`, `MODev`, `devs`, `Manager`, `ObjectManager`, and `Manager0`.

## Compatibility Behavior

Adds a minimal legacy `Manager.r0` spec when needed so daemon version checks can read the `Version` property independently of the current manager interface revision.

## Environment and Safety Hooks

Reads `STRATIS_DBUS_TIMEOUT`, defaulting to 60000 ms, through `_environment.get_timeout()`. It wraps mutating methods that accept device paths (`CreatePool`, `InitCache`, `AddCacheDevs`, `AddDataDevs`) with assertions that paths are absolute.

## Error Handling

Generation errors from `dbus_python_client_gen` or `dbus_client_gen` become `StratisCliGenerationError`.

## Notable Risk Areas

This module is import-order sensitive and asserts `stratis_cli.run` exists before loading. Any D-Bus XML/interface change affects generated classes used across almost all action modules.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_data.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_debug.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_debug.py

## Role

Implements debug-only daemon, pool, filesystem, and blockdev actions.

## Main Behavior

- `TopDebugActions.refresh_state()` calls `Manager.Methods.RefreshState`.
- `TopDebugActions.send_uevent()` maps a `/dev/...` path to sysfs and writes `change` to the device `uevent` file.
- `PoolDebugActions` print pool object paths and pool metadata JSON.
- `FilesystemDebugActions` print filesystem object paths and filesystem metadata JSON.
- `BlockdevDebugActions.get_object_path()` looks up blockdevs by UUID and prints the object path.

## Error Handling

Daemon failures become `StratisCliEngineError`; sysfs write failures become `StratisCliSynthUeventError`.

## Notable Risk Areas

Synthetic uevent generation writes directly to host sysfs. Metadata pretty-printing assumes daemon-returned metadata strings are valid JSON.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_debug.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_environment.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_environment.py

## Role

Validates and converts environment-provided D-Bus timeout values.

## Main Behavior

`get_timeout(value)` parses a millisecond string to an integer, checks it is at least `-1` and no greater than `1073741823`, then returns integer seconds via floor division by 1000.

## Error Handling

Invalid integer strings, too-small values, and too-large values raise `StratisCliEnvironmentError`.

## Notable Behavior

The accepted lower bound allows `-1`, matching D-Bus timeout conventions, despite the function documentation describing a timeout conversion more generally.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_environment.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_formatting.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_formatting.py

## Role

Shared formatting helpers for table output, optional D-Bus properties, and UUID display.

## Main Components

- `TABLE_UNKNOWN_STRING = "???"`.
- `TOTAL_USED_FREE = "Total / Used / Free"`.
- `get_property()` unwraps optional `(valid, value)` D-Bus properties.
- `print_table()` computes display widths with `wcwidth.wcswidth()` and prints aligned rows.
- `get_uuid_formatter()` returns a hyphenated or unhyphenated UUID formatter.

## Notable Behavior

`print_table()` mutates `row_entries` by inserting the header row at index 0. Callers pass newly built row lists, so this is local in current usage.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_formatting.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_introspect.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_introspect.py

## Role

Contains embedded D-Bus introspection XML used by `_data.py` to generate client classes.

## Interfaces Covered

`SPECS` defines XML for:

- `org.freedesktop.DBus.ObjectManager`.
- `org.storage.stratis3.Manager.r9`.
- `org.storage.stratis3.Report.r9`.
- `org.storage.stratis3.blockdev.r9`.
- `org.storage.stratis3.filesystem.r9`.
- `org.storage.stratis3.pool.r9`.

## API Surface Captured

The XML includes manager methods for pool creation/destruction/start/stop, key management, reports, and stopped-pool properties; pool methods for adding devices, cache initialization, filesystem lifecycle, snapshots, metadata, binding, encryption, reencrypt/decrypt, and property setters; filesystem and blockdev properties used by list/detail commands.

## Notable Risk Areas

This file is the local source of truth for generated D-Bus bindings. Drift from stratisd’s actual API causes generation failures, missing-property errors, or runtime method/property invocation failures.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_introspect.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_list_filesystem.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_list_filesystem.py

## Role

Implements filesystem listing and detailed filesystem display.

## Main Behavior

`list_filesystems()` fetches managed objects, optionally narrows by pool and filesystem ID, maps pool object paths to names, wraps filesystem data in `MOFilesystem`, and chooses table or detail display.

## Display Classes

- `ListFilesystem` provides common helpers for size triples, size limit, devnode, name, UUID, and pool-name rendering.
- `Table.display()` prints pool, filesystem, total/used/free/limit, device, and UUID.
- `Detail.display()` prints one filesystem’s UUID, name, pool, device, creation timestamp, snapshot origin, revert schedule state, size details, and size limit.

## Error and Compatibility Handling

Missing D-Bus properties are rendered as `???` where possible. Detailed listing asserts exactly one filesystem matched.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_list_filesystem.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_list_pool.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_list_pool.py

## Role

Implements pool listing for both running and stopped pools, including table and detailed views, alert summarization, encryption details, and stopped-pool metadata.

## Running Pool Behavior

- `list_pools()` dispatches to default table/detail or stopped table/detail classes.
- `Default.alert_codes()` derives maintenance, allocation-space, and encryption alerts from pool properties.
- `DefaultTable.display()` prints name, total/used/free, property flags, UUID, and alert codes.
- `DefaultDetail.display()` prints UUID, name, alerts, metadata version, allowed actions, cache, filesystem limit, overprovisioning, encryption/token-slot details, allocation state, and sizes.

## Stopped Pool Behavior

- `StoppedTable.display()` reads `Manager.StoppedPools` and prints name, metadata version, UUID, device count, key-description presence, and Clevis presence.
- `StoppedDetail.display()` selects a stopped pool by `PoolId`, prints metadata/encryption feature state, and lists devices.
- `StoppedPool` parsing from `_utils.py` is used for stopped-pool representation.

## Alerts and Helpers

`DeviceSizeChangedAlerts` scans blockdevs for observed-size changes. `TokenSlotInfo` combines keyring and Clevis token-slot details for sorted output.

## Notable Risk Areas

This module does substantial compatibility handling for legacy and V2 metadata. Missing or variant D-Bus properties are generally displayed as unknown rather than failing, but detailed output depends on current generated accessor behavior.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_list_pool.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_logical.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_logical.py

## Role

Implements filesystem/logical-volume actions within pools.

## Main Behavior

- `create_volumes()` prechecks duplicate filesystem names, builds size and size-limit optional arguments, and calls `Pool.Methods.CreateFilesystems`.
- `list_volumes()` delegates to `_list_filesystem.list_filesystems()`.
- `destroy_volumes()` maps names to filesystem object paths and calls `Pool.Methods.DestroyFilesystems`.
- `snapshot_filesystem()` calls `Pool.Methods.SnapshotFilesystem`.
- `rename_fs()` calls `Filesystem.Methods.SetName`.
- `set_size_limit()` and `unset_size_limit()` write `Filesystem.Properties.SizeLimit`.
- `schedule_revert()` and `cancel_revert()` write `Filesystem.Properties.MergeScheduled`.

## Error Handling

Preexisting or missing states become `StratisCliPartialChangeError`, `StratisCliNoChangeError`, or `StratisCliNoPropertyChangeError`; daemon non-OK codes become `StratisCliEngineError`; inconsistent success results become `StratisCliIncoherenceError`.

## Notable Risk Areas

Create/destroy paths precompute expected state from `GetManagedObjects`; concurrent daemon clients could make postcondition checks stale.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_logical.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_physical.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_physical.py

## Role

Implements block-device listing for all pools or a selected pool.

## Main Behavior

`PhysicalActions.list_devices()` fetches managed objects, optionally filters devices by pool name, wraps device objects with `MODev`, maps pool paths to pool names, and prints a table with pool name, device path, physical size, tier, and UUID.

## Formatting Details

- Shows physical path plus metadata devnode when they differ.
- Shows in-use size plus observed size when device size has changed.
- Converts tier values through `BlockDevTiers`.
- Supports hyphenated or unhyphenated UUID display.

## Compatibility Handling

Missing D-Bus properties are displayed as `???`.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_physical.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_pool.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_pool.py

## Role

Implements pool lifecycle, device management, pool property management, and pool alert explanation actions.

## Main Behavior

- `create_pool()` validates name uniqueness, checks devices are not already used in conflicting tiers, builds encryption/integrity arguments, calls `Manager.Methods.CreatePool`, and optionally disables overprovisioning.
- `stop_pool()` and `start_pool()` call manager stop/start methods using `PoolId` selectors.
- `start_pool()` supports unlock method selection, token slots, key capture/keyfile file descriptors, and cache removal.
- `init_cache()`, `add_data_devices()`, and `add_cache_devices()` precheck tier conflicts and call pool device-add methods.
- `list_pools()` delegates to `_list_pool.list_pools()`.
- `destroy_pool()` calls `Manager.Methods.DestroyPool`.
- `rename_pool()` calls `Pool.Methods.SetName`.
- `extend_data()` detects devices with larger observed physical size and calls `GrowPhysicalDevice`.
- `set_fs_limit()` and `set_overprovisioning_mode()` set pool properties.
- `explain_code()` prints a `PoolAlert` explanation.

## Error Handling

Uses specific user errors for name conflicts, no property changes, resource-not-found, devices already in use, partial changes, and no device size changes. Non-OK daemon codes become `StratisCliEngineError`; unexpected daemon success shape becomes `StratisCliIncoherenceError`.

## Notable Risk Areas

Device membership and size checks are derived from `GetManagedObjects`, so concurrent state changes can affect correctness. `create_pool()` also catches marshalling errors to produce a clearer journal-size-too-large message.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_pool.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_stratis.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_stratis.py

## Role

Contains miscellaneous daemon-level Stratis actions.

## Main Behavior

`StratisActions.list_stratisd_version()` imports generated `Manager` lazily, reads `Manager.Properties.Version` from the top object, and prints it.

## Dependencies

Uses `get_object(TOP_OBJECT)` and generated D-Bus property access from `_actions/_data.py`.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_stratis.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_stratisd_version.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_stratisd_version.py

## Role

Checks that the running `stratisd` version is compatible with this CLI.

## Main Behavior

`check_stratisd_version()` builds a packaging specifier requiring `>= 3.9.0` and `< 4.0.0`, reads `Manager0.Properties.Version`, and raises if the daemon version is outside that range.

## Error Handling

Raises `StratisCliStratisdVersionError` with actual, minimum, and maximum versions.

## Notable Behavior

Uses `Manager0` so the version check can work through the minimal legacy manager interface rather than relying on the current full manager API.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_stratisd_version.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_top.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_top.py

## Role

Implements top-level report and key-management actions.

## Main Behavior

- `_fetch_keylist()` calls `Manager.Methods.ListKeys`.
- `_add_update_key()` gets a passphrase fd from stdin/keyfile and calls `Manager.Methods.SetKey`.
- `TopActions.get_report()` prints either managed objects, engine state, or named report JSON.
- `set_key()` rejects existing key descriptions and adds a key.
- `reset_key()` requires an existing key and updates it.
- `unset_key()` removes an existing key.
- `list_keys()` prints key descriptions in a table.

## Error Handling

Name conflicts, missing resources, no-change results, daemon failures, and impossible daemon result combinations are mapped to specific CLI errors.

## Notable Risk Areas

Key-setting passes file descriptors over D-Bus and must close local descriptors. Report output directly JSON-dumps daemon or managed-object structures.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_top.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_utils.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_utils.py

## Role

Shared action-layer utilities for encryption metadata, stopped-pool parsing, passphrase handling, size triples, exception-chain traversal, and long-running D-Bus calls.

## Main Components

- `EncryptionInfo`, `EncryptionInfoClevis`, and `EncryptionInfoKeyDescription` normalize legacy optional/inconsistent encryption data.
- `Device`, `PoolFeature`, and `StoppedPool` parse `StoppedPools` property content.
- `get_pass()` reads passphrases while disabling terminal echo when possible.
- `get_passphrase_fd()` returns a file descriptor from stdin or a keyfile, with optional verification.
- `fetch_stopped_pools_property()` reads `Manager.Properties.StoppedPools`.
- `SizeTriple` computes total/used/free values.
- `get_errors()` walks exception causes.
- `long_running_operation()` treats selected D-Bus `NoReply` failures as initiated long-running operations.

## Error Handling

Raises passphrase mismatch/empty and keyfile-not-found user errors. `STRATIS_STRICT_POOL_FEATURES` controls whether unknown stopped-pool feature strings are tolerated as `UNRECOGNIZED`.

## Notable Risk Areas

Passphrase handling uses raw file descriptors and terminal mode changes. The long-running decorator is intentionally narrow: only configured method names suppress `NoReply`.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_utils.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_alerts.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_alerts.py

## Role

Defines pool alert code enums, summaries, explanations, and lookup helpers.

## Alert Families

- `PoolMaintenanceAlert`: no IPC state changes, no pool maintenance changes.
- `PoolAllocSpaceAlert`: no allocatable space.
- `PoolDeviceSizeChangeAlert`: device size increased/decreased.
- `PoolEncryptionAlert`: volume key not loaded or status unknown.

## Main Behavior

Each alert enum implements `__str__()`, `explain()`, and `summarize()`. `PoolAlert` builds a `CODE_MAP`, exposes all codes/string codes, and converts a string code back to an alert object.

## Dependencies and Notes

Used by pool listing for alert display and by `PoolActions.explain_code()` to provide detailed explanations.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_alerts.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_constants.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_constants.py

## Role

Defines CLI-level enums and identifier helper classes shared between parsers and actions.

## Main Components

- `YesOrNo` converts `yes`/`no` parser choices to booleans.
- `IdType`, abstract `Id`, `PoolId`, and `FilesystemId` normalize UUID/name selection.
- `PoolId.stopped_pools_func()` builds selectors for the stopped-pools dictionary.
- `EncryptionMethod`, `UnlockMethod`, `Clevis`, `IntegrityTagSpec`, and `IntegrityOption` model parser choices and D-Bus argument values.

## Notable Behavior

`Id.managed_objects_key()` maps UUID/name IDs to D-Bus managed-object property filters; `Id.dbus_args()` maps them to `id`/`id_type` manager method arguments. `UnlockMethod.legacy_token_slot()` encodes legacy keyring/Clevis token slot mapping.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_constants.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_error_reporting.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_error_reporting.py

## Role

Centralized interpretation and user-facing reporting for action failures.

## Main Behavior

- Maps D-Bus interface names to common resource names.
- Interprets D-Bus access, service availability, timeout, disconnect, failed call, and missing-property/search errors.
- Interprets generated client errors, daemon engine errors, user errors, version errors, incoherence errors, and synthetic uevent errors.
- `handle_error()` walks the exception chain with `get_errors()`, builds an explanation, and exits with code `ERROR`.

## Error Output

Produces messages prefixed with `Execution failed:` and delegates process termination to `exit_()`.

## Notable Risk Areas

It imports from `_actions`, so action package aggregation and error reporting are coupled. Unknown error chains intentionally re-raise after printing a report-request message.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_error_reporting.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_errors.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_errors.py

## Role

Defines the CLI exception hierarchy and user-facing string messages for expected error cases.

## Main Classes

- Base hierarchy: `StratisCliError`, `StratisCliRuntimeError`, `StratisCliUserError`.
- State/no-op errors: `StratisCliNoDeviceSizeChangeError`, `StratisCliNoPropertyChangeError`, `StratisCliPartialChangeError`, `StratisCliNoChangeError`.
- Resource/name errors: `StratisCliResourceNotFoundError`, `StratisCliNameConflictError`.
- Device-tier errors: `StratisCliInUseOtherTierError`, `StratisCliInUseSameTierError`.
- Runtime/system errors: `StratisCliIncoherenceError`, `StratisCliSynthUeventError`, `StratisCliUnknownInterfaceError`, `StratisCliEngineError`, `StratisCliActionError`.
- Setup/version/input errors: generation, environment, stratisd version, passphrase, keyfile, invalid option, and missing `--in-place`.

## Notable Behavior

`StratisCliEngineError` maps numeric daemon return codes to `StratisdErrors` when possible. `StratisCliActionError` wraps arbitrary action exceptions with command-line args and parser namespace for later error-chain interpretation.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_errors.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_exit.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_exit.py

## Role

Defines process exit codes and the helper used for CLI termination.

## Main Components

`StratisCliErrorCodes` has `OK = 0`, `ERROR = 1`, and `PARSE_ERROR = 2`.

`exit_(code, msg)` prints the message to stderr, flushes it, and raises `SystemExit(code)`.

## Dependencies and Notes

Used by `_error_reporting.py` for action failures and exposed at package top level by `__init__.py`.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_exit.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_main.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_main.py

## Role

Highest-level runtime wrapper for parsing and executing CLI commands.

## Main Behavior

`run()` builds the parser, configures `justbytes` display to avoid approximate strings, and returns `the_func(command_line_args)`.

`the_func()` parses args, runs any `post_parser` verifier, invokes `namespace.func(namespace)`, wraps action failures in `StratisCliActionError`, and sends them to `handle_error()` unless `--propagate` was set.

## Error Handling

Allows `BrokenPipeError`, `KeyboardInterrupt`, `SystemExit`, and `StratisCliEnvironmentError` to propagate. Other action exceptions are wrapped for centralized reporting.

## Notable Behavior

The returned callable returns `0` after successful command execution.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_main.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_parser/__init__.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_parser/__init__.py

## Role

Parser package initializer.

## Contents

Imports and re-exports `gen_parser` from `._parser`.

## Dependencies and Notes

This keeps the public parser entry point small and lets `_main.py` import `gen_parser` from `stratis_cli._parser`.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_parser/__init__.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_parser/_debug.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_parser/_debug.py

## Role

Defines parser data structures for debug commands.

## Command Surface

- Top-level debug: `refresh`, `uevent`.
- Pool debug: `get-object-path`, `get-metadata`.
- Filesystem debug: `get-object-path`, `get-metadata`.
- Blockdev debug: `get-object-path`.

## Dependencies

Binds commands to `TopDebugActions`, `PoolDebugActions`, `FilesystemDebugActions`, and `BlockdevDebugActions`. Uses shared `UUID_OR_NAME` identifier argument groups.

## Notable Risk Area

The blockdev debug parser allows the shared UUID/name choice group, while `BlockdevDebugActions.get_object_path()` uses `namespace.uuid.hex`; name selection would not satisfy that action’s assumptions.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_parser/_debug.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_parser/_encryption.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_parser/_encryption.py

## Role

Defines parser data structures for pool encryption, binding, rebinding, and unbinding commands.

## Main Components

- `ClevisEncryptionOptionsForTang` adapts positional `url` to shared Clevis option fields.
- `ClevisEncryptionOptionsForTpm2` sets TPM2 defaults and clears Tang-only fields.
- `BIND_SUBCMDS` and `REBIND_SUBCMDS` define legacy `pool bind`/`pool rebind` forms with move notices.
- `BIND_SUBCMDS_ENCRYPTION` and `REBIND_SUBCMDS_ENCRYPTION` define newer `pool encryption bind/rebind` forms using UUID/name pool selection.
- `ENCRYPTION_SUBCMDS` defines `on`, `off`, `reencrypt`, `bind`, `rebind`, and `unbind`.

## Dependencies

Uses shared parser helpers for Clevis/keyring options, `--in-place`, Tang trust/thumbprint selection, UUID/name groups, natural-number token slots, and post-parser validation.

## Notable Behavior

Whole-pool encryption commands require explicit `--in-place` arguments at parser/action level. Binding commands support Clevis NBDE/Tang, TPM2, and keyring flows.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_parser/_encryption.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_parser/_key.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_parser/_key.py

## Role

Defines parser data structures for key-management commands.

## Command Surface

- `set keydesc` with mutually exclusive keyfile/stdin value source.
- `reset keydesc` with mutually exclusive keyfile/stdin value source.
- `unset keydesc`.
- `list`.

## Dependencies

Commands bind to `TopActions.set_key`, `reset_key`, `unset_key`, and `list_keys`. Key value source arguments come from shared `KEYFILE_PATH_OR_STDIN`.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_parser/_key.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_parser/_logical.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_parser/_logical.py

## Role

Defines parser data structures for filesystem/logical actions.

## Main Components

- `parse_range_or_current()` accepts byte ranges or the literal `current` for size-limit setting.
- `FilesystemListOptions.verify()` enforces that filesystem UUID/name detail selection requires a pool name.
- `LOGICAL_SUBCMDS` defines `create`, `snapshot`, `list`, `destroy`, `rename`, `set-size-limit`, `unset-size-limit`, `schedule-revert`, `cancel-revert`, and `debug`.

## Dependencies

Binds commands to `LogicalActions` methods and filesystem debug subcommands. Uses shared `UUID_OR_NAME`, `RejectAction`, and `parse_range`.

## Notable Behavior

Filesystem `list` supports optional detail selection with post-parse validation because the pool name is positional and optional.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_parser/_logical.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_parser/_parser.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_parser/_parser.py

## Role

Top-level argparse construction for the Stratis CLI.

## Main Behavior

- `gen_subparsers()` walks parser/subparser trees.
- `PrintHelpAction` prints help for every subcommand.
- Helper functions add argument groups, arguments, mutually exclusive groups, and subcommands from declarative command tuples.
- `add_subcommand()` wraps command functions so `check_stratisd_version()` runs before command execution.
- `gen_parser()` creates the root parser, adds `--version`, hidden `--print-all-help`, global `--propagate`, global `--unhyphenated-uuids`, and root subcommands.

## Root Command Surface

Root subcommands are `pool`, `blockdev`, `filesystem`/`fs`, `report`, `key`, `debug`, and `daemon`. The `daemon version` subcommand prints stratisd version.

## Notable Behavior

Commands without a function default to parser error for missing subcommands. Version checking is applied through the wrapper around every configured command function.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_parser/_parser.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_parser/_physical.py -->
# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_parser/_physical.py

## Role

Defines parser data structures for block-device commands.

## Command Surface

- `list [pool_name]` lists block devices, optionally scoped to a pool.
- `debug` nests blockdev-level debug commands.

## Dependencies

Binds `list` to `PhysicalActions.list_devices` and imports `BLOCKDEV_DEBUG_SUBCMDS` from `_parser/_debug.py`.
<!-- END FILE RESEARCH: sources/block-storage/stratis-cli/src/stratis_cli/_parser/_physical.py -->