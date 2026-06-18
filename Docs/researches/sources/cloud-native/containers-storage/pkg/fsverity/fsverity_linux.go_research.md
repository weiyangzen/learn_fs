## sources/cloud-native/containers-storage/pkg/fsverity/fsverity_linux.go

Purpose: Linux fs-verity enablement and digest measurement helpers.

Important APIs/types/functions: `verityDigest`, `EnableVerity`, and `MeasureVerity`.

Control flow: `EnableVerity` issues `FS_IOC_ENABLE_VERITY` with SHA256 and 4096 block size, accepting `EEXIST` as success. `MeasureVerity` issues `FS_IOC_MEASURE_VERITY` into a fixed 64-byte buffer and returns hex digest bytes up to reported size.

State and persistence: enabling verity permanently changes file metadata/state on supporting filesystems; measuring is read-only.

Dependencies and integration points: used by `chunkedDiffer.recordFsVerity`. Depends on Linux ioctls, read-only file descriptors for enablement, and `x/sys/unix` constants.

Risks: kernel/filesystem support varies; digest buffer size is fixed at 64; callers decide whether unsupported errors are fatal. Enablement errors are wrapped with path description.

Test signals: no direct selected tests; behavior is indirectly referenced by chunked storage but not covered here.
