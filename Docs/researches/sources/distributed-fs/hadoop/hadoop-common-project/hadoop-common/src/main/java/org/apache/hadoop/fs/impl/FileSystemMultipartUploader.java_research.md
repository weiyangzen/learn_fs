# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FileSystemMultipartUploader.java

## Purpose
MultipartUploader built from basic FileSystem primitives: create a temporary collector directory, write each part as a file, concat parts, rename final output, and delete the collector.

## Important APIs, Types, and Functions
startUpload(), putPart()/innerPutPart(), complete()/innerComplete(), abort(), createCollectorPath(), getPathHandle(), totalPartsLen().

## Control Flow
startUpload creates a collector path under the target parent/name prefix and returns it as BBUploadHandle. putPart decodes uploadId to collector path, writes N.part with builder settings, copies the input stream, and closes it. complete validates handles, sorts by part number, detects duplicate part paths, creates empty file for zero total length or concats part files into a collector final file then renames over target, deletes collector, and returns a PathHandle. abort verifies collector exists and deletes it.

## State and Persistence Behavior
Remote/persistent state is the collector directory, part files, final file, and deletion/rename effects. Returned handles serialize paths as UTF-8 bytes.

## Dependencies and Integration Points
Depends on FileSystem createFile/concat/delete/getPathHandle, InternalOperations rename, BBUploadHandle/BBPartHandle, FutureIO, Commons IOUtils, and builder options.

## Risks and Test Signals
Risks include path-encoded handles being forgeable, collector path collisions/name splitting at dots, concat availability, partial cleanup on failure, empty-file overwrite semantics, and synchronous work inside completed futures. Tests should cover part ordering, duplicate handles, abort, zero-length upload, concat failure cleanup, and permission/checksum/block-size propagation.
