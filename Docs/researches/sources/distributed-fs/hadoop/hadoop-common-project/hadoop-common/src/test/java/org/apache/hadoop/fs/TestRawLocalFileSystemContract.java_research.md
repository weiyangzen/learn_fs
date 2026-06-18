# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestRawLocalFileSystemContract.java

Purpose: runs the generic filesystem contract against `RawLocalFileSystem` with local-specific disables and validates native/non-native permission loading consistency.

Important APIs/types/functions: `FileSystemContractBaseTest`, `RawLocalFileSystem`, `DF`, `NativeCodeLoader`, `StatUtils.setPermissionFromProcess`, `DeprecatedRawLocalFileStatus.loadPermissionInfoByNativeIO`, and `loadPermissionInfoByNonNativeIO`.

Control flow/state/persistence: setup installs the raw local filesystem. The contract disables rename and root-dir tests because local rename semantics differ and root writes are unsafe. Case sensitivity is inferred from OS and `DF.getFilesystem`, accounting for Docker mounts of Mac/Windows volumes. `testPermission` requires native code, creates a file, compares native and non-native owner/group/permission loading, then chmods normal and sticky-bit modes and compares again.

Dependencies/integration points: depends on native Hadoop libraries, shell chmod/stat behavior, `DF`, host filesystem type, and generic contract tests.

Risks/test signals: catches divergence between native and fallback permission loaders, sticky-bit parsing regressions, incorrect case-sensitivity assumptions in mounted filesystems, and unsafe generic contract expectations for raw local FS.
