# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Head.java

Purpose: implements `-head`, printing the first 1024 bytes of a single file.

Important APIs and types: `processOptions()`, custom `expandArgument()`, `processPath()`, and private `dumpToOffset()`.

Control flow: option parsing enforces exactly one argument. Expansion constructs a direct `PathData` without glob expansion. `processPath()` rejects directories and `dumpToOffset()` opens the file with sequential read policy and copies up to `endingOffset` bytes to `System.out`.

State and persistence: no mutation. `endingOffset` is fixed at 1024.

Dependencies and integration: extends `FsCommand`, uses `PathData.openFile(FS_OPTION_OPENFILE_READ_POLICY_SEQUENTIAL)`, `FSDataInputStream`, and `IOUtils.copyBytes()`.

Risks: output goes to `System.out` rather than inherited `out`, which matters for tests or embedded shells that redirect command streams. Glob support is intentionally absent via direct expansion. Small files simply copy less data.

Test signals: cover one-arg enforcement, directory rejection, short file, exact/long file truncation, non-glob behavior, and output stream expectations.
