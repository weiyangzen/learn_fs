# sources/distributed-fs/eos/proto/namespace/ns_quarkdb/ChangelogEntry.proto

## Purpose
Defines protobuf messages for recording MGM configuration changes. It is part of the QuarkDB-backed namespace/configuration metadata contract.

## Important APIs, types, and functions
Package `eos.mgm` contains `ConfigModification` with `key`, `previous_value`, and `new_value`, plus `ConfigChangelogEntry` with repeated modifications, an `int64 timestamp`, and a free-form `comment`.

## Control flow
The file has no executable control flow. Generated protobuf code serializes, deserializes, and mutates changelog entries for callers.

## State and persistence
Field numbers are persistent wire-format state. `modifications = 1`, `timestamp = 2`, and `comment = 3` must remain compatible with stored changelog entries. The schema records configuration deltas rather than full snapshots.

## Dependencies and integration points
Uses proto3 and integrates with MGM configuration engines, QuarkDB persistence, and admin/audit tooling that displays configuration history.

## Risks and test signals
Changing field numbers or package names would break existing data. Tests should cover round-trip serialization, multiple modifications per entry, empty comments, timestamp interpretation, and compatibility with previously stored changelog records.
