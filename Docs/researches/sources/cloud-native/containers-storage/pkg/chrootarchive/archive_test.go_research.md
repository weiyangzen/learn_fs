<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/archive_test.go -->
# sources/cloud-native/containers-storage/pkg/chrootarchive/archive_test.go

Purpose: broad tests for chrootarchive public operations and wrappers.

Important APIs/types/functions: test wrappers `TarUntar`, `CopyFileWithTar`, `UntarPath`, `CopyWithTar`; helpers `prepareSourceDirectory`, `compareDirectories`, `compareDirectoriesChown`, `compareFiles`, `slowEmptyTarReader`; tests from `TestChrootTarUntar` through `TestChrootApplyDotDotFile`.

Control flow: tests create temporary trees, tar and untar through chroot archiver wrappers, exercise huge exclude lists passed via pipe/JSON instead of argv/env, reject nil archives and invalid directory untar/copy operations, copy files/directories/symlinks with and without chown, compare output via archive diffs or CRCs, and verify slow zero-padded empty tar readers complete. `TestChrootApplyDotDotFile` verifies a name containing `..` but not path traversal is allowed.

State/persistence: temporary files, directories, symlinks, tar files, and ownership changes where permitted.

Dependencies/integration: uses `archive`, `idtools`, `reexec.Init`, filesystem syscalls, and chrootarchive public APIs.

Risks/test signal: tests protect IPC of large options, rootless/ownership behavior, wrapper correctness, empty archive handling, and accidental over-rejection of safe dot-dot names. Several tests skip Windows/Solaris for known platform limitations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/archive_test.go -->
