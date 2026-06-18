<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/local/LocalConfigKeys.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/local/LocalConfigKeys.java

## Purpose
Defines local filesystem default configuration constants and builds `FsServerDefaults` for the `file://` AbstractFileSystem implementation.

## Important APIs, Types, And Functions
Constants include block size, replication, stream buffer size, bytes per checksum, write packet size, encryption flag, trash interval, checksum type, and key provider URI. `getServerDefaults()` constructs the defaults object.

## Control Flow
`getServerDefaults` returns a new `FsServerDefaults` populated from static constants. There is no configuration lookup in this class.

## State And Persistence
Static constants only. No persisted state.

## Dependencies And Integration Points
Used by `RawLocalFs.getServerDefaults`. Extends `CommonConfigurationKeys` and depends on `DataChecksum.Type` and `FsServerDefaults`.

## Risks
Comments note some settings are placeholders ignored by local/raw/checksum FS behavior. Consumers should not assume local checksums or encryption follow these values.

## Test Signals
Verify defaults exposed through local AFS match constants and remain compatible with legacy local filesystem expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/local/LocalConfigKeys.java -->
