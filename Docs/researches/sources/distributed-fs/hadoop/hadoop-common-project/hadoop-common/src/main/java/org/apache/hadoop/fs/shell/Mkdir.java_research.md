# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Mkdir.java

Purpose: implements `-mkdir`, creating directories with optional parent creation.

Important APIs and types: `processOptions()`, `processPath()`, and `processNonexistentPath()`.

Control flow: options require at least one path and parse `-p`. Existing paths are accepted only if they are directories and `-p` is set; existing files cause `PathIsNotDirectoryException`. Missing paths require existing parent unless `-p`, then call `fs.mkdirs()`.

State and persistence: mutates filesystem by creating directories. State is only `createParents`.

Dependencies and integration: extends `FsCommand`, uses `PathData`, `Path`, and Hadoop path exceptions.

Risks: parent validation has special handling for root/null parent. `fs.mkdirs()` false produces generic `PathIOException` without detailed cause. With `-p`, existing directories are silently accepted.

Test signals: cover missing args, existing directory with and without `-p`, existing file, missing parent with and without `-p`, root edge case, and failed `mkdirs()`.
