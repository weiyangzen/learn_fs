<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CreateFileBuilder.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CreateFileBuilder.java

## Purpose

`CreateFileBuilder` implements S3A's builder API for file creation and translates builder options into S3A write flags, headers, and conditional overwrite metadata.

## Important APIs, Types, and Functions

It extends `FSDataOutputStreamBuilder`. Public APIs are `build()`, `withFlags()`, `getFlags()`, callback `createFileFromBuilder()`, and value type `CreateFileOptions` with flag/header/etag accessors.

## Control Flow

`build()` separates mandatory header keys from other mandatory keys, rejects unknown mandatory options, extracts create headers from `fs.s3a.create.header.*`, maps content type into an S3 header, rejects append, validates create/overwrite flags, derives `WriteObjectFlags`, validates conditional overwrite etag when enabled, and calls the callback.

## State and Persistence Behavior

The builder stores superclass options and callbacks. `CreateFileOptions` is immutable by reference except the header map is not defensively copied. No persistence occurs here.

## Dependencies and Integration Points

It integrates with Hadoop `FileSystem.createFile()`, `CreateFlag`, S3A create option constants, `WriteObjectFlags`, and the S3A output stream creation path.

## Risks and Edge Cases

Header mandatory keys are exempted from unknown-key rejection. Empty etag with conditional-etag flag fails fast. Append is unsupported. Mutable headers map can be changed if retained by callers.

## Test Signals

Test mandatory key validation, create headers, content type, recursive/performance/multipart flags, conditional overwrite with and without etag, append rejection, no create/overwrite rejection, `withFlags()` mapping, and callback option contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CreateFileBuilder.java -->
