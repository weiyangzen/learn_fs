<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/AdminHelper.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/AdminHelper.java

## Purpose

`AdminHelper` centralizes shared command-line utility code for HDFS admin tools such as cache, crypto, and storage policy administration.

## Important APIs and types

It provides DFS resolution (`getDFS`, URI overload, `checkAndGetDFS`), exception formatting (`prettifyException`), table formatting (`getOptionDescriptionListing`), cache TTL/limit parsers, command resolution (`determineCommand`), usage printing, the `Command` interface, and the built-in `HelpCommand`.

## Control flow

Admin tools call `determineCommand` on the first argument, then invoke the returned command. `-help` returns a dynamic `HelpCommand` that prints either all command long usages or a specific command's long usage. DFS resolution handles `ViewFileSystemOverloadScheme` by unwrapping the raw mounted filesystem for the configured default URI before requiring `DistributedFileSystem`.

## State and persistence behavior

The helper is stateless. It parses strings and returns wrappers; actual persistence is performed by tool commands against HDFS.

## Dependencies and integration points

It integrates Hadoop `Configuration`, `FileSystem`, `DistributedFileSystem`, ViewFS overload scheme, `CachePoolInfo`, `DFSUtil`, and `TableListing`. The `Command` contract is implemented by `CacheAdmin` and `CryptoAdmin` nested commands.

## Risks and test signals

Risks include incorrect ViewFS unwrapping, `prettifyException` truncating useful diagnostics, help returning exit code 1 when all help is printed, and parser edge cases for "never" and "unlimited". Tests should cover HDFS and non-HDFS filesystems, ViewFS overload, command lookup, help for unknown commands, TTL parsing, and limit parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/AdminHelper.java -->
