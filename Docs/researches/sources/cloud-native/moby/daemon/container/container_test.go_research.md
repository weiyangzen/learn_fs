<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/container_test.go -->
# sources/cloud-native/moby/daemon/container/container_test.go

## Purpose
Tests selected container helpers for stop signal/timeouts, secret target path construction, and JSON logger path population.

## Important APIs, Types, And Functions
`TestContainerStopSignal`, `TestContainerStopTimeout`, `TestContainerSecretReferenceDestTarget`, `TestContainerLogPathSetForJSONFileLogger`, and `TestContainerLogPathSetForRingLogger`.

## Control Flow
Tests instantiate minimal `Container` values, call helper methods, and assert defaults/overrides. Logger tests create temp roots, start json-file loggers, defer close, and compare `LogPath`.

## State And Persistence Behavior
Logger tests create log files under temp directories. Other tests are in-memory only.

## Dependencies And Integration Points
Depends on container API types, swarm references, jsonfile logger, filepath, syscall, and gotest.

## Risks And Test Signals
Signals include fallback to SIGTERM and default timeout, invalid stop signal fallback, secret mount path defaulting, and nonblocking ring logger preserving json-file API log path.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/container_test.go -->
