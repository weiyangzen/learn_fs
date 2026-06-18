# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/S3AMultipartUploaderBuilder.java

## Purpose
`S3AMultipartUploaderBuilder` adapts Hadoop's multipart uploader builder pattern to construct `S3AMultipartUploader` instances with S3A-specific dependencies.

## Important APIs and Types
The constructor accepts `S3AFileSystem`, `WriteOperations`, `StoreContext`, target `Path`, and multipart uploader statistics. `getThisBuilder()` returns the typed builder. `build()` creates the uploader.

## Control Flow
The builder stores dependencies and defers all validation and operation behavior to the superclass and `S3AMultipartUploader` constructor. `build()` performs a direct instantiation.

## State and Persistence
The builder is an in-memory dependency holder and performs no persistence.

## Dependencies and Integration Points
It extends `MultipartUploaderBuilderImpl<S3AMultipartUploader, S3AMultipartUploaderBuilder>` and integrates with `S3AFileSystem` multipart uploader factory methods.

## Risks and Edge Cases
Nullability is annotated but not explicitly checked in this class. Incorrect dependency wiring will fail later during uploader operations.

## Test Signals
Tests should verify builder path propagation, dependency injection, type-safe fluent behavior, and that built uploaders operate against the qualified base path.
