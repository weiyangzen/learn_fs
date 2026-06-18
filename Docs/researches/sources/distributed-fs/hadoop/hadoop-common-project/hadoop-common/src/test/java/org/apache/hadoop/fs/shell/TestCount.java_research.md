# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestCount.java

## Purpose
Unit-tests FsShell `count` option parsing, output headers, content summary formatting, quota usage formatting, storage-type quota selection, command metadata, and snapshot header support.

## Important APIs, Types, and Functions
The test targets `Count.processOptions`, `processPath`, `getCommandName`, `isDeprecated`, `getReplacementCommand`, `getName`, `getUsage`, and `getDescription`. It uses mocked `PrintStream`, mocked `FileSystem`, `PathData`, `ContentSummary`, `QuotaUsage`, and `StorageType`. Nested `MockContentSummary` and `MockQuotaUsage` override `toString` variants to expose which flags were passed.

## Control Flow
Setup registers `mockfs` and wraps Mockito `mockFs` with `MockFileSystem`. Option tests build `LinkedList<String>` arguments and assert internal flags: `-h`, `-q`, `-t`, no options, and missing path. Header tests verify exact `-v` output for no quota, quota, quota by all storage types, quota by SSD, combined `-q -t -v -h`, multiple storage types, and snapshot `-s`. Path tests configure `PathData`, run `processOptions`, call `processPath`, and verify the mocked output string reflects raw bytes vs human-readable, quota vs no quota, quota usage only, and selected storage types. Metadata tests assert exact command name, usage, and description strings.

## State and Persistence
All filesystem state is mocked. `PathData` uses `mockfs:/test`, while `MockFileSystem` returns controlled `MockContentSummary` and `MockQuotaUsage` objects. No external persistence is used.

## Dependencies and Integration Points
This test protects `Count` command behavior that users and scripts depend on, especially column headers and option interactions involving quota, storage type, erasure coding, snapshots, and human-readable output.

## Risks and Edge Cases
Exact string assertions make formatting regressions visible but also require updates for intentional CLI text changes. The test does not verify real `ContentSummary` numeric values; it verifies delegation flags and output assembly. Storage type set expectations depend on supported enum values including SSD, DISK, ARCHIVE, PROVIDED, and NVDIMM.

## Test Signals
Passing tests signal stable `count` CLI parsing and output contracts, including header text, path suffixing, quota usage delegation, storage-type filtering, and command help metadata.
