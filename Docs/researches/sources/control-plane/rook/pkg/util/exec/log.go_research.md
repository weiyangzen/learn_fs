# sources/control-plane/rook/pkg/util/exec/log.go

## Purpose
`exec/log.go` defines the package logger for exec utilities.

## Important APIs, Types, and Functions
The package variable `logger` is a capnslog package logger named `github.com/rook/rook`, subsystem `exec`.

## Control Flow, State, and Persistence
There is no control flow. The logger participates in global capnslog state configured elsewhere.

## Dependencies and Integration Points
It depends on capnslog and is used by local and remote exec helpers for command/debug/error logging.

## Risks
Package-level logging can expose command args or output if callers pass sensitive data. Logging behavior depends on global capnslog configuration.

## Test Signals
No direct tests are mapped. Logging behavior is indirectly exercised by exec tests and runtime command paths.
