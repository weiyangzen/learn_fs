# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/UnknownStoreException.java

## Purpose
`UnknownStoreException` represents an absent bucket or AWS store resource. It intentionally does not extend `FileNotFoundException` so missing stores are not cached or ignored as missing files.

## Important APIs, Types, and Functions
It extends `PathIOException` and provides constructors `(String path, String message)` and `(String path, String message, Throwable cause)`.

## Control Flow and State
Construction delegates path/message to `PathIOException` and conditionally installs a cause. There is no additional behavior.

## State and Persistence Behavior
The exception carries path, message, and optional cause. It persists no external state.

## Dependencies and Integration Points
Dependencies include Hadoop `PathIOException`. `S3AUtils.translateException()` maps unknown-bucket 404 responses to this type, and `S3ARetryPolicy` fails it fast.

## Risks and Test Signals
Risks include misclassifying missing objects as missing stores or vice versa, and callers catching only `FileNotFoundException`. Tests should verify unknown bucket translation, retry fail-fast behavior, cause preservation, and user-visible path/message formatting.
