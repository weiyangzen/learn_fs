# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/DiskChecker.java

Purpose: `DiskChecker` provides filesystem and disk-health checks for local directories, including optional write/sync/delete probing.

Important APIs and types: exceptions `DiskErrorException` and `DiskOutOfSpaceException`; `checkDir` and `checkDirWithDiskIo` overloads for `File` and `LocalFileSystem`/`Path`; permission-aware `mkdirsWithExistsAndPermissionCheck`; testing hooks `getFileNameForDiskIoCheck`, `replaceFileOutputStreamProvider`, and `getFileOutputStreamProvider`.

Control flow: `checkDirInternal` creates missing directories with race-tolerant `mkdirsWithExistsCheck`, verifies directory/read/write/execute with `FileUtil`, and optional `doDiskIo` writes one byte to a generated file, syncs, closes, deletes, and retries up to three filenames before declaring failure. LocalFS overload also sets expected permissions when newly created or mismatched.

State and persistence behavior: static atomic `FileIoProvider` supports tests. Disk IO checks create temporary files named `DiskChecker.OK_TO_DELETE_.NNN` or random UUID and delete them. Directory checks may create directories and set permissions.

Dependencies and integration points: used by disk validators and Hadoop daemons checking storage directories; depends on `LocalFileSystem`, `FsPermission`, `FileUtil`, `FileUtils`, and `IOUtils`.

Risks: validation has side effects on directories and permissions. File-method access checks may not capture all ACL/security behavior. Disk IO retry can leave files only if cleanup fails. Atomic provider replacement must be restored by tests.

Test signals: cover directory creation races, non-directory and access failures, LocalFS permission setting, disk IO success/failure/retry, cleanup on exceptions, deterministic/random probe filenames, provider replacement, and delete failure.
