# sources/cloud-native/containerd/integration/client/client_unix_test.go

## Purpose
This non-Windows integration test file defines Unix test image/command defaults and verifies runtime option mutation during task creation.

## Important APIs, Types, and Functions
Globals choose BusyBox images and short/long commands. `TestNewTaskWithRuntimeOption` uses a `fakeTaskService` to capture `CreateTaskRequest` options. `fakeTaskService` implements minimal task service methods.

## Control Flow
The test creates a client with the fake task service, gets the test image, creates containers with runtime options, starts task creation with optional UID/GID/shim cgroup opts, unmarshals the captured task options, and compares them to expected runc options.

## State and Persistence
Containers and snapshot views are created through client APIs and cleaned up. Captured task requests are stored in a mutex-protected map.

## Dependencies and Integration Points
Uses runc options protobufs, client task creation, OCI image config, plugins runtime ID, typeurl unmarshalling, and protobuf comparison helpers.

## Risks
The fake task service only implements the methods needed for the test and returns not-found for get/delete. The test is specific to runc v2 option semantics.

## Test Signals
Confirms task opts can overwrite runtime option IO UID/GID and shim cgroup while preserving unrelated runtime option fields.
