# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/BCFile.java

Purpose: block-compressed physical storage layer beneath TFile, supporting compressed data blocks, named meta blocks, indexes, magic/version footer, and bounded block readers.

Important APIs/types/functions: `BCFile.Writer`, `Writer.BlockAppender`, `WBlockState`, `Reader`, `Reader.BlockReader`, `RBlockState`, `MetaIndex`, `MetaIndexEntry`, `DataIndex`, `Magic`, and `BlockRegion`.

Control flow: writer starts at file offset zero, writes magic, creates data blocks until the first meta block, records each closed block region, then on close writes the data-index as a meta block, serializes meta index, writes meta-index offset, version, and trailing magic. Reader seeks to the footer, verifies version/magic, reads meta index, opens the `BCFile.index` meta block, and reconstructs the data index. Block readers wrap `BoundedRangeFileInputStream` with the configured decompressor.

State and persistence: persists block regions, compression names, meta names with `data:` prefix, version, and magic in the BCFile format. Writer maintains in-progress/closed flags and an error counter.

Dependencies and integration: depends on Hadoop FS streams, `Compression`, `Utils.Version`, TFile buffer settings, `SimpleBufferedOutputStream`, and `CompareUtils` for offset lookup.

Risks: only one block appender may be open; data blocks after meta blocks are illegal. `DataOutputStream.size()` wraps for raw blocks above 4GB, noted in comments. Tests should cover footer parsing, duplicate/missing meta blocks, block order rules, compression codecs, corrupt magic/version, block index lookup, and resource return on exceptions.
