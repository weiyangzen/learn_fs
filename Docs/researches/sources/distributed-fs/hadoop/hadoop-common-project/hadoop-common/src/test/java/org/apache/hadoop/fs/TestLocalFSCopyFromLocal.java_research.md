# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocalFSCopyFromLocal.java

Purpose: specializes the copy-from-local contract suite for `LocalFileSystem` and documents self/recursive copy edge cases.

Important APIs/types/functions: `AbstractContractCopyFromLocalTest`, `LocalFSContract`, `copyFromLocalFile(delSrc, overwrite, src, dst)`, `createTempFile`, `createTempDirectory`, `assertPathExists`, and `assertPathDoesNotExist`.

Control flow/state/persistence: the inherited contract supplies setup and common copy tests. Local additions copy a file to its own parent with source deletion, copy a directory to itself with source deletion, copy a parent into its child with source deletion, and copy a parent into its child without deletion. The no-delete case intentionally asserts recursive nested output exists, documenting current local behavior rather than rejecting it.

Dependencies/integration points: integrates local FS with the generic contract framework. Uses Java temp files/directories converted to Hadoop `Path` through URI constructors.

Risks/test signals: catches dangerous deletion behavior when source and destination overlap. The recursive-copy case is a risk marker: local FS may recurse deeply depending on underlying copy implementation, so future fixes must preserve or consciously update the documented behavior.
