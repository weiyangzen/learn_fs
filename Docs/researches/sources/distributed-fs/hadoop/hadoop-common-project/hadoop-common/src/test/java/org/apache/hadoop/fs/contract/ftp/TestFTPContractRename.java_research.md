# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ftp/TestFTPContractRename.java

## Purpose
`TestFTPContractRename` runs rename contract tests against FTP while accounting for FTPFileSystem's same-directory rename limitation.

## Important APIs, Types, And Functions
It extends `AbstractContractRenameTest`, returns `FTPContract`, and overrides `testRenameDirIntoExistingDir()` plus `testRenameFileNonexistentDir()`. `verifyUnsupportedDirRenameException(IOException)` accepts failures containing `FTPFileSystem.E_SAME_DIRECTORY_ONLY`.

## Control Flow
Most rename tests are inherited. Two inherited scenarios that require cross-directory or destination-parent behavior are expected to fail for FTP; the override calls `super`, fails if it unexpectedly succeeds, and accepts only the known same-directory-only exception.

## State And Persistence
State is inherited test paths on the FTP server. The helper has no fields.

## Dependencies And Integration Points
The test depends directly on `FTPFileSystem.E_SAME_DIRECTORY_ONLY`, so it is tightly coupled to FTP rename diagnostics.

## Risks
Changing FTPFileSystem error text can break this test even if behavior is unchanged. Conversely, accepting only message text may miss distinct failures with the same substring.

## Test Signals
Passing signals include ordinary same-directory rename behavior and deliberate acceptance of unsupported cross-directory rename cases.
