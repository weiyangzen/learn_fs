# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/Nfs3Constant.java

## Purpose
`Nfs3Constant.java` centralizes NFSv3 protocol constants, procedure enums, mode/access bits, write stability options, verifier values, and NFS export cache config keys.

## Important APIs, Types, and Functions
- `SUN_RPCBIND=111`, `PROGRAM=100003`, and `VERSION=3` identify NFS RPC services.
- `NFSPROC3` enum maps NFSv3 procedures to ordinal wire values and marks non-idempotent procedures (`CREATE`, `MKDIR`, `SYMLINK`, `MKNOD`, `REMOVE`, `RMDIR`, `RENAME`, `LINK`) as not idempotent.
- `NFSPROC3.fromValue(int)` safely returns null for invalid ordinals.
- File handle, cookie verifier, create verifier, and write verifier byte sizes are defined.
- Access request/response bit masks and POSIX mode bit masks are defined.
- `WriteStableHow` maps `UNSTABLE`, `DATA_SYNC`, and `FILE_SYNC` to ordinals.
- `WRITE_COMMIT_VERF` is initialized from current time for server-instance write commit verification.
- Filesystem property bits, create options, and `nfs.exports.cache.*` config defaults are defined.

## Control Flow and State
Most fields are immutable constants. `WRITE_COMMIT_VERF` is process-start-time state and changes between server instances. Enum ordinal order is protocol-significant.

## Dependencies and Integration Points
NFSv3 dispatchers, request/response serializers, write handling, access checks, and `NfsExports` use these constants.

## Risks and Edge Cases
`WriteStableHow.fromValue(int)` does not bounds-check and can throw `ArrayIndexOutOfBoundsException` for invalid wire values. `MODE_ALL` contains duplicate OR terms but the result remains effectively a mask of all listed bits. Protocol constants must remain stable.

## Test Signals
Tests should cover ordinal mapping, invalid procedure values, idempotence flags, stable write enum parsing, and config default use in `NfsExports`.
