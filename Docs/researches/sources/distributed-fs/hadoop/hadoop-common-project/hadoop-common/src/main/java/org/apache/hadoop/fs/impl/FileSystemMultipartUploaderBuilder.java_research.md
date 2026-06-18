# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FileSystemMultipartUploaderBuilder.java

## Purpose
Concrete builder for FileSystemMultipartUploader.

## Important APIs, Types, and Functions
Constructor; getThisBuilder(); build(); public getters exposing FS, permission, buffer size, replication, flags, checksum, block size.

## Control Flow
build instantiates FileSystemMultipartUploader with this builder and filesystem. Other methods expose protected base state to the uploader.

## State and Persistence Behavior
Stores state in MultipartUploaderBuilderImpl base only.

## Dependencies and Integration Points
Used by FileSystem multipart upload factory paths.

## Risks and Test Signals
Tests should verify builder defaults from filesystem, fluent setters, and build creates uploader with qualified base path.
