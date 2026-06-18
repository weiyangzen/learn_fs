# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractRenameTest.java

Purpose: `AbstractContractRenameTest` validates file and directory rename semantics, including missing sources, destination collisions, directory moves, parent creation policy, and attempts to rename under a file.

Important APIs and types: it uses `FileSystem`, `Path`, `FileAlreadyExistsException`, `FileNotFoundException`, `ContractOptions` flags, and `ContractTestUtils` helpers such as `rename`, `writeDataset`, `writeTextFile`, `verifyFileContents`, `rm`, and `dataset`.

Control flow: positive tests rename a file in the same directory, rename an empty directory, rename a directory into an existing directory, and move nested directory/file ancestor trees. Missing-source behavior is controlled by `RENAME_RETURNS_FALSE_IF_SOURCE_MISSING`. File-over-file behavior is controlled by `RENAME_OVERWRITES_DEST` and `RENAME_RETURNS_FALSE_IF_DEST_EXISTS`, which are asserted mutually exclusive. Rename into nonexistent directory follows `RENAME_CREATES_DEST_DIRS`. Rename of non-empty source into existing destination accepts either POSIX replacement (`RENAME_REMOVE_DEST_IF_EMPTY_DIR`) or CLI-style nesting. Negative tests attempt to rename into a direct child or descendant of a path that is actually a file.

State and persistence behavior: tests write deterministic source and destination data and validate final byte content to distinguish overwrite from rejection. Directory tests verify both source removal and destination ancestor creation.

Dependencies and integration points: the suite relies heavily on contract flags to encode acceptable semantic variation across HDFS, local, object store, and CLI-like stores. It also depends on listing diagnostics from `generateAndLogErrorListing()` on unexpected outcomes.

Risks: rename behavior is one of the most variable filesystem surfaces; incorrect contract flag values can either fail valid stores or hide nonconformance. Some tests do not explicitly assert the boolean result of raw `fs.rename()` calls in ancestor cases.

Test signals: pass indicates rename preserves data, handles destination conflicts as declared, moves directories and nested ancestors correctly, rejects paths under files, removes sources, and does not silently create wrong destinations.
