# sources/control-plane/rook/pkg/util/logging.go

## Purpose
`logging.go` configures Rook's global capnslog log level with special handling for trace-level logging.

## Important APIs, Types, and Functions
`DefaultLogLevel` is `capnslog.INFO`. `SetGlobalLogLevel(userLogLevelSelection, logger)` maps user `TRACE` to `DEBUG`, maps `TRACE_INSECURE` to real `TRACE`, parses the level, defaults invalid values to INFO, rejects levels more verbose than TRACE, and calls `capnslog.SetGlobalLogLevel()`.

## Control Flow, State, and Persistence
The function mutates global logging state in capnslog. It logs parse/defaulting decisions with the provided logger.

## Dependencies and Integration Points
It depends on capnslog. Operator startup and CLI paths can use it to apply user-selected logging while avoiding accidental trace logs that may reveal secrets.

## Risks
Global log level changes affect all package loggers in-process, including tests. The string handling is case-sensitive through capnslog parsing and the explicit `TRACE`/`TRACE_INSECURE` checks.

## Test Signals
`logging_test.go` covers supported levels, invalid input defaulting, and the special trace mappings.
