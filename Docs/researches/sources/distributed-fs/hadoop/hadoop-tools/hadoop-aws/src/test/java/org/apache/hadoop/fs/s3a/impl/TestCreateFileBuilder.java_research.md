# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestCreateFileBuilder.java

## Purpose
`TestCreateFileBuilder` unit-tests S3A's `CreateFileBuilder` option parsing and callback handoff without using a real S3A filesystem.

## Important APIs, Types, and Functions
- `mkBuilder()` creates a builder over the local filesystem path `/` with custom callbacks.
- `BuilderCallbacks.createFileFromBuilder()` wraps a `BuilderOutputStream` in `FSDataOutputStream` and exposes parsed options.
- Tests cover `.create()`, `.append()`, `FS_S3A_CREATE_PERFORMANCE`, and `FS_S3A_CREATE_HEADER.*` options.
- `unwrap()` and `build()` extract the custom output stream for assertions.

## Control Flow
`testSimpleBuild()` verifies a basic create has no overwrite and no performance flag. `testAppendForbidden()` confirms append is unsupported. `testPerformanceSupport()` sets the S3A create performance option and checks it reaches callbacks. `testHeaderOptions()` supplies mandatory and optional header options and validates header map entries, including `If-None-Match`. `testIncompleteHeader()` sets the header prefix without a suffix and expects `IllegalArgumentException`.

## State and Persistence Behavior
No real files are written; the output stream's `write()` is a no-op. Parsed builder options are retained in `BuilderOutputStream` for assertions.

## Dependencies and Integration Points
The test bridges Hadoop's `FSDataOutputStreamBuilder` API, S3A-specific create options, custom header mapping, and callback-based file creation.

## Risks and Edge Cases
The test uses local FS only as a builder parent, so it does not cover S3 upload behavior. Header validation focuses on option parsing, not downstream request construction.

## Test Signals
Passing confirms create-builder flags, performance option, custom headers, and append rejection are correctly parsed before S3A output stream creation.
