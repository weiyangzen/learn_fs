# sources/distributed-fs/beegfs-go/common/logger/logger.go

Purpose: provides a configurable zap logger wrapper that supports stdout, stderr, rotating log files, syslog, and dynamic log-level updates through the config manager listener interface.

Important APIs/types are `Logger`, `Config`, `supportedLogTypes`, `SupportedLogTypes`, `New`, `Configurer`, `UpdateConfiguration`, and `getLevel`. BeeGFS log levels 0 through 5 map to zap fatal, error, warn, info, and debug.

Control flow in `New` forks between developer and production modes. Developer mode ignores configured level and builds zap's development logger at debug. Production mode creates a console encoder with ISO timestamps, creates an atomic zap level, chooses a write syncer by configured type, then builds a zap core. `LogFile` uses `ensureLogsAreWritable` and lumberjack; `Syslog` uses `NewSyslogWriteSyncer`.

State is the embedded `*zap.Logger` plus `zap.AtomicLevel`. `UpdateConfiguration` type-asserts a `Configurer`, reads its logging config, computes the new level, and mutates only the atomic level; destination and encoder are not changed at runtime.

Dependencies include zap, zapcore, lumberjack, syslog, `configmgr`, reflection, and OS streams. Integration points include app config reload, syslog, file rotation, and packages that embed logger config in their own configuration structs.

Risks: runtime updates ignore destination changes, which may surprise callers. Syslog parsing depends on the console encoder format. Invalid levels return info plus an error, so callers must honor the error. Developer mode discards configured type/file entirely.

Test signals: `logger_test.go` checks developer/stdout creation, unsupported type errors, level updates, and all level mappings.
