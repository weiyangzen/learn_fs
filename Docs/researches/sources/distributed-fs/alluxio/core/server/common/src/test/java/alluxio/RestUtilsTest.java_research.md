# sources/distributed-fs/alluxio/core/server/common/src/test/java/alluxio/RestUtilsTest.java

## Purpose
`RestUtilsTest` verifies the common REST wrapper's success and error response behavior.

## Important APIs, Types, and Functions
The tests are `voidOkResponse()`, `stringOkResponse()`, `objectOkResponse()`, and `errorResponse()`. They exercise `RestUtils.call()`, `RestUtils.RestCallable`, `RestUtils.ErrorResponse`, global configuration, Jackson string serialization, `AlluxioStatusException`, and gRPC `Status`.

## Control Flow, State, and Persistence
Each test invokes `RestUtils.call()` with a callable. Null results should produce HTTP 200 with null entity, strings should be JSON-encoded strings, objects should be passed through as entities, and `AlluxioStatusException` should produce HTTP 500 with a status code and message in `ErrorResponse`. There is no persistence.

## Dependencies and Integration Points
It depends on JUnit, Jersey `Response`, Jackson, and Alluxio exception/configuration utilities. It protects REST endpoint wrappers used by web services.

## Risks and Test Signals
Risks covered include incorrect JSON handling for strings, object wrapping regressions, and loss of status/message data on exceptions. Passing tests signal stable REST response contracts for simple success and Alluxio-status failures.
