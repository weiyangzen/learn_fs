# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AGetFileStatus.java

## Purpose

Mock-S3 unit tests for `S3AFileSystem.getFileStatus()` classification of files, fake directory markers, implicit directories, root, and missing paths.

## Important APIs, Types, and Functions

Tests mock `S3Client.headObject()`, `listObjects()`, and `listObjectsV2()`, then call `fs.getFileStatus(Path)`. Helpers match `HeadObjectRequest` and set up V1/V2 list responses with `CommonPrefix` and `S3Object`.

## Control Flow

`testFile()` stubs object metadata and verifies file status path, length, mod time, and no erasure coding. `testFakeDirectory()` makes the object key miss but `key/` list contain a zero-size marker and expects a directory. `testImplicitDirectory()` makes metadata miss and list return a common prefix. `testRoot()` treats `/` as an existing directory despite misses. `testNotFound()` makes all probes empty and expects `FileNotFoundException`.

## State, Dependencies, and Integration Points

State is the mocked S3 client behavior inherited from `AbstractS3AMockTest`. It integrates S3A status probing, directory-marker interpretation, V1/V2 listing fallbacks, erasure-coding status expectations, and path qualification.

## Risks and Test Signals

These tests encode S3A's object-store directory model. They catch probe-order or request-key regressions, root handling mistakes, and accidental erasure-coding metadata changes. They do not exercise live object store consistency.
