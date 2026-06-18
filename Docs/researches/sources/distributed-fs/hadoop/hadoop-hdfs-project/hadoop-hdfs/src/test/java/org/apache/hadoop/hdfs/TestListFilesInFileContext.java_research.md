# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestListFilesInFileContext.java

## Purpose
Tests `FileContext.util().listFiles` behavior on HDFS for files, directories, recursion, non-recursion, block-location metadata, and symbolic links.

## APIs and Control Flow
`testSetUp` starts a cluster and obtains `FileContext`. `writeFile` creates parent paths and writes deterministic random bytes. `testFile` lists a file with recursive true and false and checks one `LocatedFileStatus`. `testDirectory` verifies empty directory listing, one-file listing, then recursive and non-recursive ordering for nested files. `testSymbolicLinks` creates symlinks to a directory and file and checks recursive listing follows the directory symlink and non-recursive listing returns the file target. `cleanDir` deletes the test root after each test.

## State, Dependencies, Integration
State is HDFS namespace, file contents, symlink metadata, and block locations. Dependencies include `FileContext`, `Options.CreateOpts`, `CreateFlag`, `RemoteIterator`, `LocatedFileStatus`, and `FsPermission`. It integrates FileContext utility listing with HDFS block-location reporting and symlink resolution.

## Risks and Test Signals
Signals are lengths, qualified paths, block-location counts, iterator exhaustion, and ordering. Risks are ordering assumptions and HDFS symlink behavior needing symlink support enabled in the environment.
