# sources/distributed-fs/beegfs-go/watch/internal/config/config.go

## Purpose

This file defines BeeWatch's top-level application configuration and the update/validation rules shared by the config manager, logger, metadata manager, and subscriber manager.

## Important APIs, Types, And Functions

`AppConfig` groups `logger.Config`, `MgmtdConfig`, `subscribermgr.HandlerConfig`, `[]metadata.Config`, `[]subscriber.Config`, and hidden developer settings. It implements `configmgr.Configurable`, `logger.Configurer`, and `subscribermgr.Configurer`. `GetLoggingConfig` and `GetSMConfig` expose component-specific views without import cycles. `NewEmptyInstance` supports unmarshalling. `UpdateAllowed` enforces dynamic reload constraints. `ValidateConfig` checks static metadata buffer and target requirements.

## Control Flow

Config updates are type-checked, then developer and metadata settings are rejected if changed after startup. Logging changes are permitted only for the `Level` field; all other log sink/rotation fields are fixed. Subscriber and handler changes are allowed and later interpreted by `subscribermgr.Manager`.

## State And Persistence

This file owns no runtime state but defines which config can change without process restart. That policy preserves metadata socket/buffer stability and avoids reinitializing developer-only server features or log sinks at runtime.

## Dependencies And Integration Points

It integrates with `common/configmgr`, `common/logger`, `common/types.MultiError`, `metadata.Config`, `subscriber.Config`, and `subscribermgr.HandlerConfig`. `main.go` must be manually kept in sync with `AppConfig` fields because flags are defined there.

## Risks And Test Signals

Reflection-based logging comparison can miss semantic equality issues if logger config adds non-comparable fields. The event-version field is validated indirectly by `metadata.New`, not here. Static validation currently requires exactly one metadata service and nonzero buffer fields. Tests cover metadata update rejection but not logging-level-only reload, subscriber validation, or malformed developer changes.
