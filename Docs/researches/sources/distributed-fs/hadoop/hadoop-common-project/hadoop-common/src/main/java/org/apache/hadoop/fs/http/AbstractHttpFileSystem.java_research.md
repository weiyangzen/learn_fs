# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/http/AbstractHttpFileSystem.java

## Purpose
Minimal read-only FileSystem for http/https URLs. It opens URLConnection streams and rejects mutation/list/seek operations.

## Important APIs, Types, and Functions
initialize(), getUri(), open(), getFileStatus(), getWorkingDirectory(), mkdirs(), hasPathCapability(), nested HttpDataInputStream implementing Seekable and PositionedReadable but throwing unsupported for positional APIs.

## Control Flow
open qualifies the path, opens a URLConnection, and wraps the input in FSDataInputStream. getFileStatus returns a synthetic non-directory status with unknown length. hasPathCapability reports FS_READ_ONLY_CONNECTOR true after argument validation.

## State and Persistence Behavior
Stores initialized URI only. It reads remote HTTP data but does not persist or cache state.

## Dependencies and Integration Points
Depends on URLConnection, FileSystem, CommonPathCapabilities, PathCapabilitiesSupport. HttpFileSystem and HttpsFileSystem provide schemes.

## Risks and Test Signals
Risks are lack of seek/positioned reads despite interface implementation, unknown length metadata, no listStatus, and URLConnection error handling. Tests should cover open success/failure, read-only capability, and UnsupportedOperationException for writes/seeks.
