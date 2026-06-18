<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/InternalConstants.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/InternalConstants.java

## Purpose

`InternalConstants` collects private S3A implementation constants that are not stable public API.

## Important APIs, Types, and Functions

It defines delete idempotency, buffer sizes, rename/delete/upload limits, default block size, HTTP status codes, log names, S3A open/create option key sets, CSE padding length, access point messages, dynamic capabilities, AWS auth scheme name, and error-code strings.

## Control Flow

The class has static initialization for immutable open-file and create-file key sets and dynamic capability lists. There are no methods beyond the private constructor.

## State and Persistence Behavior

All state is static constants or immutable collections. No runtime mutation or persistence occurs.

## Dependencies and Integration Points

It is referenced across S3A operations for max multi-delete size, CSE length adjustment, status-code translation, capability reporting, create/open option validation, logging, and upload limits.

## Risks and Edge Cases

Because these constants are internal, external code should not depend on them. Changing limits such as `MAX_ENTRIES_TO_DELETE`, `RENAME_PARALLEL_LIMIT`, or CSE padding affects request batching and compatibility. Capability lists must stay aligned with actual feature support.

## Test Signals

Tests should assert option-key validation uses these sets, max delete limit matches S3 request constraints, dynamic capability reporting contains expected entries, and status-code constants match translation code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/InternalConstants.java -->
