# sources/cloud-native/moby/daemon/internal/distribution/utils/progress.go

## Purpose
Streams distribution progress messages to a JSON progress output and cancels the operation if the client writer fails.

## APIs, Control Flow, and Integration
`WriteDistributionProgress(cancelFunc, outStream, progressChan)` creates a JSON progress output, drains `progressChan`, writes each progress item, logs EPIPE as client cancellation, logs other write errors, calls `cancelFunc` once, and keeps draining until the channel closes to avoid producer deadlock.

## State, Dependencies, and Risks
State is the local `operationCancelled` guard. Risks include cancellation after first write failure while still consuming progress, and no return error to caller. Integration is API streaming for pull/push progress.
