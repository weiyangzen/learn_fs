# sources/cloud-native/moby/daemon/logger/jsonfilelog/jsonfilelog_test.go

Purpose: unit and integration tests for the json-file logger.

Important APIs/types/functions: tests cover basic logging, tags, option parsing, gzip rotation, labels/env attrs, and benchmark write performance. Helpers read compressed rotated files.

Control flow/state/persistence: tests create temporary log paths, write `logger.Message` values, close the logger, and inspect generated JSON or rotated gzip content.

Dependencies/integration: validates `JSONFileLogger.New`, `Log`, `ValidateLogOpt`, `loggerutils.LogFile`, and attr/tag extraction from `logger.Info`.

Risks: tests focus on expected local filesystem behavior; cross-platform rotation is mostly covered through loggerutils tests.

Test signals: strong signal for persisted json-line format and option validation.
