# sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/SwiftMockOutputStream.java

## Purpose
`SwiftMockOutputStream` is the simulation-mode output stream for Alluxio's Swift under file system. Instead of streaming bytes to Swift as they are written, it buffers all writes into a local temporary file and uploads that file to a JOSS mock `StoredObject` when `close()` succeeds.

## APIs and Control Flow
The constructor accepts a JOSS `Account`, container name, object name, and Alluxio temporary directory list. It chooses a temp directory with `CommonUtils.getTmpDir`, builds a UUID-named local file with `PathUtils.concatPath`, and wraps a `FileOutputStream` in a `BufferedOutputStream`. The three `write` overloads and `flush` delegate directly to the local stream. `close()` is guarded by `mClosed`; on first close it closes the local stream, resolves `Container` and `StoredObject` through JOSS, and calls `uploadObject(mFile)`.

## State, Dependencies, and Integration
State is local to one stream: the temp `File`, delegate output stream, target Swift identifiers, JOSS account, and close flag. It integrates with `SwiftUnderFileSystem.createObject` only when `SWIFT_SIMULATION` is enabled. Dependencies are JOSS model objects, Alluxio temp path utilities, and SLF4J logging.

## Risks and Test Signals
The temp file is not deleted after upload, so repeated simulation writes can leave local artifacts. `mClosed` is not thread-safe, which matches the `@NotThreadSafe` annotation. Errors during JOSS upload are wrapped as `IOException`. There is no direct test for this class in the listed subset; coverage is indirect through Swift simulation paths.
