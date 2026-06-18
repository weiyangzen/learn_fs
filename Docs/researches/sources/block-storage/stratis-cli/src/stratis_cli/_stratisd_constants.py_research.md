# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_stratisd_constants.py

## Purpose

Defines small Python representations of constants and data structures used when interacting with `stratisd`, the Stratis daemon.

The module includes daemon return codes, block device tier identifiers, report keys, pool action availability levels, metadata versions, and a Clevis configuration container.

## Definitions

### `StratisdErrors`

An `IntEnum` for daemon result codes:

- `OK = 0`
- `ERROR = 1`

`__str__` returns the enum member name, such as `OK` or `ERROR`.

### `BlockDevTiers`

An `IntEnum` for block device tiers:

- `DATA = 0`
- `CACHE = 1`

`__str__` returns the enum member name.

### `ReportKey`

An `Enum` of report identifiers:

- `ENGINE_STATE = "engine_state_report"`
- `MANAGED_OBJECTS = "managed_objects_report"`
- `STOPPED_POOLS = "stopped_pools"`

`__str__` returns the underlying string value.

The file notes that `managed_objects_report` is not a key recognized by `stratisd`, but is defined here because it is used together with daemon-recognized report constants.

### `PoolActionAvailability`

An `IntEnum` describing which categories of pool interaction are available:

- `fully_operational = 0`
- `no_ipc_requests = 1`
- `no_pool_changes = 2`

#### `pool_maintenance_alerts()`

Returns a list of `PoolMaintenanceAlert` values corresponding to the availability level:

- If availability is at least `no_ipc_requests`, includes `PoolMaintenanceAlert.NO_IPC_REQUESTS`.
- If availability is at least `no_pool_changes`, includes `PoolMaintenanceAlert.NO_POOL_CHANGES`.

Because this is an `IntEnum`, ordering is significant. `no_pool_changes` includes both alerts, since its value is greater than `no_ipc_requests`.

### `MetadataVersion`

An `Enum` for Stratis metadata versions:

- `V1 = 1`
- `V2 = 2`

`__str__` returns the numeric value as a string.

### `ClevisInfo`

A simple container for Clevis encryption metadata.

Constructor parameters:

- `pin: str`
- `config: Mapping[str, Any]`

Stored fields:

- `self.pin`
- `self.config`

This is used by parser/helper code to represent Clevis pin and JSON-like config data before action/daemon layers consume it.

## Dependencies

Imports from standard library:

- `Enum`
- `IntEnum`
- `typing.Any`
- `typing.List`
- `typing.Mapping`

Imports from local modules:

- `PoolMaintenanceAlert` from `_alerts`

## Cross-File Relationships

- `_parser/_shared.py` imports `ClevisInfo` and creates instances during Clevis option validation.
- Alert/reporting code can use `PoolActionAvailability.pool_maintenance_alerts()` to map daemon availability state into user-facing maintenance alerts.
- Parser/action code may rely on `MetadataVersion`, `BlockDevTiers`, `ReportKey`, and `StratisdErrors` as stable daemon-facing constants.

## Important Behaviors

- `PoolActionAvailability` values are ordered by severity/capability reduction; comparison operators are used directly.
- `ClevisInfo` has no validation, representation, equality, or conversion methods. It is only a lightweight field container.
- `ReportKey.__str__` differs from most other enums in this file by returning the value rather than the member name.

## Research Notes

This file is a shared constants boundary between CLI code and daemon semantics. Changes to enum numeric values or string values can affect DBus/report interpretation and compatibility with `stratisd`.
