# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/DeleteOpParam.java

## Purpose

`DeleteOpParam` models the WebHDFS `op` query parameter for HTTP DELETE operations.

## Important APIs, Types, And Functions

It extends `HttpOpParam<DeleteOpParam.Op>`. Enum `Op` includes `DELETE`, `DELETESNAPSHOT`, and `NULL`, each with expected HTTP code. Op methods define HTTP type, auth requirement, output behavior, redirect behavior, expected response, and query string.

## Control Flow

Construction parses a string into an enum op and rewrites invalid parse errors to identify DELETE operations. DELETE operations do not require auth at the op layer, do not output a body, and do not redirect.

## State And Persistence

Only parsed operation value is stored.

## Dependencies And Integration Points

Used by WebHDFS server/client op dispatch for file delete and snapshot delete. `WebHdfsFileSystem.delete` and `deleteSnapshot` use enum constants directly.

## Risks

Expected response-code mismatches break validation. Adding DELETE operations requires updating both client enum and server handling.

## Test Signals

Tests should cover op parsing, invalid op messages, expected HTTP codes, query string output, and delete/delete-snapshot calls.
