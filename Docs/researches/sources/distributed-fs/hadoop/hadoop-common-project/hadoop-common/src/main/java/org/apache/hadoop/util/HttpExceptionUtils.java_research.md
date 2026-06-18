# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/HttpExceptionUtils.java

## Purpose

`HttpExceptionUtils` serializes server-side exceptions into Hadoop's `RemoteException` JSON shape and reconstructs/throws client-side exceptions from non-expected HTTP responses.

## Important APIs, Types, And Functions

Constants define JSON keys: `RemoteException`, `exception`, `javaClassName`, and `message`. Server APIs are `createServletExceptionResponse()` and `createJerseyExceptionResponse()`. Client flow is `validateResponse(HttpURLConnection, int)`, which reads error JSON, calls `createExceptionFromJson()`, and uses a generic trick to throw reconstructed exceptions.

## Control Flow, State, And Persistence

Server methods set status/content type and write pretty JSON through `JsonSerialization.writer()`. Client validation returns on expected status. Otherwise it reads the error stream, parses a map, reflectively finds a public `(String)` constructor for the remote exception class, and throws it; if parsing or reflection fails, it throws an `IOException` with response details. There is no mutable persistent state.

## Dependencies And Integration Points

It depends on servlet APIs, JAX-RS `Response`, `HttpURLConnection`, `MethodHandles`, and `JsonSerialization`. Hadoop REST services and clients use it to preserve exception class/message across HTTP boundaries.

## Risks And Test Signals

Reflective construction only works for public exception classes with a string constructor. Error messages are truncated to one line. Tests should cover servlet and Jersey JSON shape, expected-status no-op, malformed JSON fallback, unknown classes, constructor absence, and checked exception rethrow behavior.
