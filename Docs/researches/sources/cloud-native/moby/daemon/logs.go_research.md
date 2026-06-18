# sources/cloud-native/moby/daemon/logs.go

## Purpose
This file implements daemon-side container log retrieval and log config merging/validation.

## Important APIs, Types, And Functions
`Daemon.ContainerLogs` returns a channel of `backend.LogMessage` values and TTY status. `getLogger` retrieves the live container logger or starts a read-only logger for stopped containers. `mergeAndVerifyLogConfig` and `defaultLogConfig` merge daemon defaults and validate driver-specific options.

## Control Flow
`ContainerLogs` starts a trace span, validates stdout/stderr selection, resolves the container, rejects removal/dead state and `none` driver reads, obtains a logger, verifies it implements `logger.LogReader`, parses tail, and calls `ReadLogs`. It then launches a goroutine that forwards log messages or errors to a buffered channel until log streams close or context is canceled, while closing temporary loggers and marking `ConsumerGone`.

## State, Persistence, And Dependencies
The function reads container state under existing daemon/container abstractions and may create a temporary logger. It does not directly persist state. `mergeAndVerifyLogConfig` mutates the provided `LogConfig`, filling default type/config and merging cache-related defaults before validation.

## Integration Points
The file bridges API log requests (`backend.ContainerLogsOptions`) to logger drivers, container state, tracing, daemon default log config, and `logger.ValidateLogOpts`.

## Risks And Edge Cases
Follow mode is disabled when a new logger is created for a stopped container. Error forwarding copies only the error to avoid partial data. Channel sends are guarded by context cancellation to avoid blocking forever. If `StartLogger` returns an error after creating resources, the code marks `created=true` and notes a possible resource leak TODO.

## Test Signals
`logs_test.go` only covers nil per-container log config map merging. Broader behavior relies on integration tests around log streaming and individual driver tests.
