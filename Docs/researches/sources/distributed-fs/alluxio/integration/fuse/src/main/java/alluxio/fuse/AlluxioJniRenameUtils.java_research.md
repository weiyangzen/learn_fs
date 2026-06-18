# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/AlluxioJniRenameUtils.java

Purpose: bit helpers for libfuse rename flags used by JNI FUSE. It defines `NO_FLAGS`, `RENAME_NOREPLACE`, and `RENAME_EXCHANGE`.

Important APIs and flow: `exchange(int)` and `noreplace(int)` test the respective bits; `noFlags(int)` requires exact zero. `AlluxioJniFuseFileSystem.renameInternal` uses these helpers to reject exchange, reject noreplace overwrites, delete existing destinations for no-flag overwrites, and reject unknown flags.

State, dependencies, risks, and tests: no state and no external dependencies. Risks are Linux-specific numeric flag assumptions and no validation for combined unsupported bits beyond the caller logic. Rename behavior is covered indirectly by JNI filesystem tests for no-flag success, missing source, existing destination, and length limits.
