<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/copy_unix_test.go -->
# sources/cloud-native/containers-storage/pkg/archive/copy_unix_test.go

Purpose: exhaustive Unix tests for `CopyResource` and the copy preparation matrix.

Important APIs/types/functions: helpers `getTestTempDirs`, `isNotDir`, `joinTrailingSep`, `fileContentsEqual`, `dirContentsEqual`, `logDirContents`, `testCopyHelper`, `testCopyHelperFSym`; tests `TestCopyErr*` and `TestCopyCaseA` through `TestCopyCaseJ` plus symlink-following variants.

Control flow: tests create sample trees, prepare source/destination combinations, call `CopyResource` with follow-link false or true, and verify file hashes or directory diffs using `ChangesDirs`. The documented matrix covers file-to-new-file, file-to-asserted-directory error, file overwrite, file into directory, directory creation, directory-to-file errors, directory under existing directory, contents-only copy with `/.`, and symlink-to-file/directory variants.

State/persistence: temporary directories, files, symlinks, and copy outputs only.

Dependencies/integration: validates `CopyInfoSourcePath`, `TarResource`, `CopyTo`, `CopyResource`, path intent preservation, symlink following, tar rebasing, and diff-based directory equality.

Risks/test signal: protects user-facing copy semantics where a trailing separator or `/.` changes whether the directory itself or only contents are copied. It also asserts errors for invalid parent or not-directory destinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/copy_unix_test.go -->
