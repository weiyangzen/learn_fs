# sources/control-plane/rook/pkg/util/logging_test.go

## Purpose
This file tests global log-level selection behavior.

## Important APIs, Types, and Functions
`TestSetGlobalLogLevel()` passes INFO, DEBUG, WARNING, ERROR, TRACE, TRACE_INSECURE, and INVALID to `SetGlobalLogLevel()` and uses `logger.LevelAt()` to verify desired and next-more-verbose visibility.

## Control Flow, State, and Persistence
The test mutates capnslog global state for each subtest. It does not restore a previous global level at the end.

## Dependencies and Integration Points
It depends on capnslog and testify. It protects operator logging configuration.

## Risks
Because logging state is global, parallel tests could interfere if added. The test does not cover lowercase/mixed-case inputs.

## Test Signals
Signals include TRACE being downgraded to DEBUG, TRACE_INSECURE enabling real TRACE, and invalid input defaulting to INFO.
