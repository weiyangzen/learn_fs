# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractEtagTest.java

Purpose: `AbstractContractEtagTest` validates etag exposure and consistency for filesystems that support etags through path capabilities.

Important APIs and types: it uses `EtagSource`, `FileStatus`, `LocatedFileStatus`, `FileSystem`, `Path`, `CommonPathCapabilities.ETAGS_AVAILABLE`, `ETAGS_PRESERVED_IN_RENAME`, AssertJ assertions, and AssertJ assumptions. The internal `etagFromStatus(FileStatus)` helper requires status objects to implement `EtagSource` and return a non-blank etag.

Control flow: `testEtagConsistencyAcrossListAndHead()` asserts `ETAGS_AVAILABLE`, touches a file, obtains the etag from `getFileStatus`, then lists the path and compares the listed status etag. `testEtagsOfDifferentDataDifferent()` writes one byte sequence, captures its etag, overwrites with same-length different data, and requires the etag to change. `testEtagConsistencyAcrossRename()` runs only when `ETAGS_PRESERVED_IN_RENAME` is true and checks rename does not change etag. `testLocatedStatusAlsoHasEtag()` verifies `listLocatedStatus()` and `listFiles()` return `LocatedFileStatus` entries with etags matching `getFileStatus`.

State and persistence behavior: tests create and overwrite short files and rename one file. Etag is treated as persistent object identity or content-version metadata depending on the capability under test.

Dependencies and integration points: the test integrates Hadoop path-capability probing, object metadata in `FileStatus`, and list APIs used by query planners. It depends on `ContractTestUtils.createFile` and `touch`.

Risks: etag semantics vary across filesystems. The same-length overwrite test prevents trivial length/path-only etags but may fail on stores with weak or delayed metadata refresh. Rename preservation is opt-in, so false capability declarations are the main risk.

Test signals: pass indicates etags are non-empty, exposed consistently across head/list/listFiles/listLocatedStatus, change when content changes, and are preserved across rename only when the filesystem declares that behavior.
