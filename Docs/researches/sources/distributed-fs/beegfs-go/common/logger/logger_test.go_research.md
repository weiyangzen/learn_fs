# sources/distributed-fs/beegfs-go/common/logger/logger_test.go

Purpose: unit tests the common logger constructor, dynamic configuration update path, and BeeGFS-to-zap log-level mapping.

Important test helpers include `testConfig`, which implements `Configurer` via `GetLoggingConfig`. Tests call `New`, `UpdateConfiguration`, and unexported `getLevel`.

Control flow: `TestNew` builds a developer logger and a stdout logger, then verifies unsupported types fail. `TestUpdateConfiguration` starts at warn level, supplies a replacement config with debug level, and checks the atomic level changes. `TestGetLevel` table-tests all valid numeric levels plus invalid level 6.

State behavior under test is the `Logger.level` atomic level and the embedded zap logger pointer. Persistence and external destinations are not heavily exercised; the test avoids logfile and syslog setup.

Dependencies include `testing`, `testify/assert`, `fmt`, and zapcore. Integration signal is focused on the logger package's config contract rather than real config manager reloads.

Risks: tests do not cover file permission failure, lumberjack setup, syslog write translation, developer-mode update behavior, or destination immutability after update. Assertions read private fields, so internal restructuring can require test updates.

Test signals: current coverage is good for core level semantics and constructor sanity but intentionally shallow for IO-backed destinations.
