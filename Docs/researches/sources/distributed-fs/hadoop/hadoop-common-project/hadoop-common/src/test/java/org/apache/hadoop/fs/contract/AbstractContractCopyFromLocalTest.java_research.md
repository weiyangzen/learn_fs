# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractCopyFromLocalTest.java

Purpose: `AbstractContractCopyFromLocalTest` validates `FileSystem.copyFromLocalFile()` behavior for local files and directories copied into the contract filesystem. It covers overwrite, delete-source, directory recursion, destination interpretation, and error handling.

Important APIs and types: the test uses local `java.io.File`, `java.nio.file.Files`, Apache Commons `FileUtils` and `IOUtils`, Hadoop `Path`, `FileSystem`, `FileStatus`, `PathExistsException`, and `FileAlreadyExistsException`. Helper methods include `copyFromLocal(File, overwrite, delSrc)`, `fileToPath()`, temp file and directory builders, and `assertFileTextEquals()`.

Control flow: each test creates temporary local sources, invokes a `copyFromLocalFile` overload, then validates remote existence and contents. File cases cover empty files, non-empty files, no-overwrite failure, overwrite success, missing source failure, and `delSrc=true`. Directory cases cover copying a file into an existing directory, copying to a nonexistent destination, copying non-empty and empty directories, directory overwrite options, delete-source for directories, nested directory trees, and failure when copying a directory onto an existing file.

State and persistence behavior: local temp files are cleaned in `teardown()` when tracked by the `file` field, while several directory tests create additional temp directories managed by the OS temp area. Remote filesystem state is written under paths derived from local file or directory names and validated through contract-base assertions.

Dependencies and integration points: it integrates local filesystem URIs (`new Path(file.toURI())`) with the target filesystem. It depends on `copyFromLocalFile` preserving file bytes, recursively copying directory trees, honoring overwrite and delete-source flags, and mapping a source directory relative to its local parent for expected destination paths.

Risks: temp directory cleanup is incomplete for every local helper-created directory, so repeated local test execution may leave OS temp artifacts. Destination expectations are path-name based and may differ for filesystems that normalize local names or reject certain URI forms. Directory overwrite behavior can vary across implementations, with `PathExistsException` and `FileAlreadyExistsException` used as expected signals.

Test signals: pass indicates reliable local-to-remote copy semantics for files, directories, trees, overwrite policy, deletion of local sources when requested, missing-source rejection, and file/directory collision handling.
