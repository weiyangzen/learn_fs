<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/ConsistentUnderFileSystem.java -->
# sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/ConsistentUnderFileSystem.java

Purpose: adapter base for UFS implementations that do not suffer eventual-consistency issues. It maps guarded "existing", "nonexisting", and "renamable" operations directly to normal UFS operations.

Important APIs and control flow: `createNonexistingFile` calls `create`, delete-existing calls `deleteDirectory`/`deleteFile`, get-existing status methods call their normal equivalents, `isExistingDirectory` calls `isDirectory`, open-existing calls `open`, and rename-renamable calls `renameDirectory`/`renameFile`.

State, persistence, and integration: no additional state beyond `BaseUnderFileSystem`. It changes behavioral assumptions for concrete subclasses by trusting immediate consistency. Dependencies include Alluxio URI/config and UFS options. Risks include misuse for eventually consistent object stores, which would bypass protective checks expected elsewhere. Test signals should verify subclasses inherit the direct mappings and that higher layers select this base only for truly consistent UFS backends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/ConsistentUnderFileSystem.java -->
