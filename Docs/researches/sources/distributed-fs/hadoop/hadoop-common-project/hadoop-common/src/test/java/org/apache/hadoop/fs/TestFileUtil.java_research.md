## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileUtil.java

Purpose: broad contract suite for `FileUtil`: directory listing, recursive deletion, permission-assisted deletion, symlink handling, disk usage, archive extraction, copy/replace/temp-file helpers, stat conversion, jar/classpath utilities, filesystem comparison, Java untar symlink safety, link reading, regular-file detection, and write helpers for both `FileSystem` and `FileContext`.

Important APIs/types/functions: `FileUtil.list/listFiles/fullyDelete/fullyDeleteContents/getDU/unTar/unTarUsingJava/unZip/copy/stat2Paths/symLink/readLink/isRegularFile/write/createJarWithClassPath/getJarsInDirectory/compareFs`, `FileUtils`, Commons Compress tar/zip streams, Hadoop `Path`, `FileSystem`, `FileContext`, `FsPermission`, and helper classes `Verify` and `MyFile`.

Control flow: setup builds a temp tree with files, directories, symlinks to files/dirs, partitioned files, and a symlink cycle. Deletion tests verify symlinks are removed without deleting targets, dangling links are handled, and permission failures return false while optionally granting permissions can recover. Archive tests create tar/zip inputs, test permissions, reject traversal entries like `../foo`, and verify Java untar preserves in-tree symlinks but rejects arbitrary symlink escapes. Copy tests cover file/dir copy and source deletion. Later tests cover classpath jar manifest expansion, jar discovery, compareFs URI behavior, symlink creation edge cases, readLink edge cases, and writing bytes/strings to FS and FC.

State and persistence: uses JUnit `@TempDir` plus some `tmp` relative directories in Java untar tests, cleaned in finally blocks. It changes file permissions, creates symlinks, creates archives, and writes local files.

Dependencies/integration points: local OS symlink and permission semantics, Commons IO/Compress, Hadoop local FS, classpath manifest behavior, path traversal protections, and Java NIO symlink APIs.

Risks and test signals: high platform sensitivity around permissions, symlinks, Windows behavior, and archive file modes. Security-sensitive signals include rejecting zip/tar outputs outside the destination and avoiding symlink target deletion. Exact file lengths, jar manifest classpaths, and write/read equality protect data correctness.
