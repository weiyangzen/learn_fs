# sources/control-plane/rook/pkg/util/sys/log.go

## Purpose
`sys/log.go` defines the package logger for system utility code.

## Important APIs, Types, and Functions
The package variable `logger` is a capnslog logger named `github.com/rook/rook`, subsystem `sys`.

## Control Flow, State, and Persistence
There is no control flow. Logging behavior follows capnslog global state.

## Dependencies and Integration Points
It depends on capnslog and is used by device parsing/discovery code.

## Risks
System utility logs can include host command output and device metadata. Verbosity is controlled globally.

## Test Signals
No direct tests are mapped. Device tests indirectly exercise code paths that log through this logger.
