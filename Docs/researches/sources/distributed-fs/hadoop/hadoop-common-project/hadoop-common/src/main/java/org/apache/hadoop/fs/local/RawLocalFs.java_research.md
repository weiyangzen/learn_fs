<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/local/RawLocalFs.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/local/RawLocalFs.java

## Purpose
Adapts the legacy `RawLocalFileSystem` to the `AbstractFileSystem` API through `DelegateToFileSystem`.

## Important APIs, Types, And Functions
Constructors bind `FsConstants.LOCAL_FS_URI`, `RawLocalFileSystem`, and the `file` scheme. Overrides include `getUriDefaultPort`, `getServerDefaults(Path)`, deprecated `getServerDefaults()`, and `isValidName`.

## Control Flow
Construction delegates all filesystem operations to a new `RawLocalFileSystem`. Server defaults come from `LocalConfigKeys`. Name validation always returns true so OS-specific validation happens in the underlying local filesystem.

## State And Persistence
State is inherited delegate state. No extra fields are stored in this class.

## Dependencies And Integration Points
Used by `LocalFs` and AFS factory paths. Depends on local constants, `FsServerDefaults`, and `Path`.

## Risks
Skipping name validation is intentional but means invalid paths fail later and differently by platform. Defaults are generic and may not describe the actual local device.

## Test Signals
Verify `file://` AFS creation, no default port, server defaults, and path handling on platform-specific invalid names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/local/RawLocalFs.java -->
