# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestSymlinkLocalFS.java

Purpose: abstract local-filesystem specialization of `SymlinkBaseTest`, adding local edge cases for dangling links, partially qualified paths, target qualification, and platform exclusions.

Important APIs/types/functions: `SymlinkBaseTest`, shared `wrapper`, `createSymlink`, `getFileLinkStatus`, `getLinkTarget`, `getFileStatus`, `rename`, `setWorkingDirectory`, `FileUtil.fullyDelete`, `UserGroupInformation`, and platform assumptions.

Control flow/state/persistence: overrides base tests to skip unsupported dangling/recursive/timestamp cases on Windows or Solaris. Local tests stat nonexistent partially qualified paths, create dangling links, verify `getFileStatus` fails while `getFileLinkStatus` succeeds with owner/group/symlink/path fields, create the target later to make the link work, and verify absolute partially qualified targets remain absolute after parent rename. It also rejects local links to non-local filesystems and treats link-to-dot `IllegalArgumentException` as acceptable.

Dependencies/integration points: depends on either FileContext or FileSystem wrappers supplied by subclasses, local symlink support, raw local stat behavior, user/group information, and platform-specific symlink semantics.

Risks/test signals: catches dangling-link stat regressions, URI/path qualification mistakes, security-sensitive cross-filesystem symlink creation, and inconsistent wrapper behavior between local FileContext and FileSystem.
