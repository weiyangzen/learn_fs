<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/MultiObjectDeleteException.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/MultiObjectDeleteException.java

## Purpose

`MultiObjectDeleteException` represents S3 multi-object delete responses that returned per-object failures despite an HTTP 200 status.

## Important APIs, Types, and Functions

It extends AWS `S3Exception`, stores a list of `S3Error`, exposes `errors()`, `translateException(String)`, and static `errorToString(S3Error)`.

## Control Flow

Construction builds an S3Exception with status 200, synthetic error code, service name, and a message summarizing the error count. Translation inspects contained errors: access denied failures produce an `AccessDeniedException`; otherwise a general `AWSS3IOException` is returned. Each error can be formatted with key, version id, code, and message.

## State and Persistence Behavior

The error list is stored in memory. There is no persistence.

## Dependencies and Integration Points

It integrates AWS SDK S3 error models with S3A exception translation and bulk-delete/remove-keys flows.

## Risks and Edge Cases

HTTP 200 does not mean success for multi-delete. Mixed errors are collapsed to one translated IOException, so callers needing per-key detail must inspect `errors()`. Error lists should be treated as immutable by callers but are not defensively copied here.

## Test Signals

Test construction message/status/code, access-denied translation, non-access-denied translation, mixed error behavior, formatting with and without version id, and preservation of all S3 errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/MultiObjectDeleteException.java -->
