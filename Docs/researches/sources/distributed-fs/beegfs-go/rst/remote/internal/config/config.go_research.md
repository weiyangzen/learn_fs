# sources/distributed-fs/beegfs-go/rst/remote/internal/config/config.go

## Purpose
Defines BeeRemote application configuration, validation, and a mapstructure decode hook for protobuf oneof-based Remote Storage Target type configuration.

## Important APIs, Types, And Functions
Exports `AppConfig`, `MgmtdConfig`, `AppConfig.NewEmptyInstance`, `AppConfig.UpdateAllowed`, `AppConfig.ValidateConfig`, and `SetRSTTypeHook`.

## Control Flow
`AppConfig` aggregates mount, management, server, logger, job, worker-manager, worker, RST, and developer config. `ValidateConfig` checks job DB path presence, minimum retained job entries, and max/min retention consistency. `SetRSTTypeHook` intercepts decoding into `flex.RemoteStorageTarget`, finds a supported RST type key, constructs the proper protobuf oneof wrapper, decodes kebab-case-compatible type-specific config with unknown-key errors, sets `Type`, and deletes the type key.

## State And Persistence
No persistence here. Config values are consumed by the service and may point to durable paths such as job DB and logs. `UpdateAllowed` currently permits all updates, although comments note RST dynamic update policy is incomplete.

## Dependencies And Integration Points
Used by `beegfs-remote/main.go` and `configmgr`. Depends on server/job/worker/workermgr config structs, common logger config, RST supported type registry, mapstructure, protobuf `flex.RemoteStorageTarget`, and common `types.MultiError`.

## Risks And Edge Cases
`ValidateConfig` appends a multi-error for missing `PathDBPath` but returns immediately for retention errors, so multiple validation issues may not all be reported. The error message says `job.path-db-path`, while the flag is `job.path-db` in main. Decode hook mutates the input map in place and rejects mixing multiple RST types when `Type` already exists. Kebab/camel duplicate keys can produce ambiguous results as documented.

## Test Signals
No direct tests. Needed coverage includes validation combinations, supported/unsupported RST type decoding, unknown keys, duplicate type fields, kebab-case matching, and dynamic update expectations.
