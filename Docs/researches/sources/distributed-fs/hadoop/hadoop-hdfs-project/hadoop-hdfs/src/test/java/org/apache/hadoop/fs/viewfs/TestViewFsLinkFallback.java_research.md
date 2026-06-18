# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsLinkFallback.java

## Purpose

`TestViewFsLinkFallback` validates `linkFallback` behavior through the `AbstractFileSystem` and `FileContext` APIs rather than the `FileSystem` API. It focuses on mkdir, create, delegation-token aggregation, listFiles, and rename behavior when fallback and internal mount-directory trees overlap.

## Important APIs, types, and functions

The test uses `AbstractFileSystem.get`, `FileContext.getFileContext`, `ConfigUtil.addLinkFallback`, `ConfigUtil.addLink`, `Options.CreateOpts`, `Options.Rename.OVERWRITE`, `CreateFlag.CREATE`, `LocatedFileStatus`, `RemoteIterator`, `Token`, `DistributedFileSystem`, `FileAlreadyExistsException`, and `FileNotFoundException`. Helper `verifyRename` asserts source disappearance and destination existence.

## Control flow, state, and persistence

Setup starts a three-namespace HDFS cluster and clears namespace 0 root before each test. Each test builds a mount table, prepares fallback target trees under `/fallbackDir`, gets an `AbstractFileSystem` or `FileContext` for `viewfs://default/`, then performs operations. Mappings deliberately overlap mount internal directories and fallback directories to test shadowing and fallback routing.

## Dependencies and integration points

This integrates the newer AbstractFileSystem/ViewFs path with fallback resolution, parent creation, create-parent semantics, token collection from explicit links plus fallback, `listFiles` over fallback roots, and rename behavior across fallback/internal paths.

## Risks and test signals

Risks include API divergence from `ViewFileSystem`, failure to create parents when `createParent` is false but internal dirs exist, weak failure when fallback NameNodes are down, wrong token count, create-over-internal-dir behavior, and rename into internal directories without matching fallback structure. Signals are HDFS existence checks, exact token count 3, expected `FileAlreadyExistsException`/`FileNotFoundException`, and successful overwrite renames.
