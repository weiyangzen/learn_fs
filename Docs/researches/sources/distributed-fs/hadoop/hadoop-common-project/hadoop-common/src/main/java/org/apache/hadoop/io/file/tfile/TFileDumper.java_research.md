<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/TFileDumper.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/TFileDumper.java

## Purpose
`TFileDumper` is a package-private diagnostics utility that opens a TFile and prints human-readable structural information: file versions, compression, record counts, block sizes, metadata overhead, per-data-block index entries, and per-meta-block regions.

## Important APIs and Types
The public surface is the static `dumpInfo(String file, PrintStream out, Configuration conf)` method. The nested `Align` enum formats table cells as left, center, right, or zero-padded numeric fields and calculates display widths.

## Control Flow
`dumpInfo` resolves the Hadoop `Path`, obtains file length and an `FSDataInputStream`, constructs a `TFile.Reader`, then collects properties from the underlying `BCFile.Reader` and `TFileMeta`. It totals compressed and raw data block sizes, totals meta block sizes, derives metadata-index/header sizes, prints the property table, forces the TFile data index loaded, and prints data-block and meta-block tables.

## State and Persistence
The utility does not mutate TFiles. It holds transient maps of formatted properties and uses reader internals such as `readerBCF.dataIndex`, `readerBCF.metaIndex`, and `reader.tfileIndex`. Streams and reader are cleaned in a `finally` block via `IOUtils.cleanupWithLogger`.

## Dependencies and Integration Points
It depends on Hadoop filesystem APIs, `TFile.Reader`, `BCFile.BlockRegion`, `BCFile.MetaIndexEntry`, `TFileIndexEntry`, `Compression.Algorithm`, and `Utils.Version`. It is invoked by `TFile.main` for command-line dumping.

## Risks and Edge Cases
The data block compression-ratio code divides by `dataSize` when compression is not `none`; malformed or empty compressed data metadata could make that unsafe. `Meta-Data Size Ratio` divides by `metaSize`, which should normally include required TFile metadata but is still a corrupt-file risk. The non-ASCII key dump loop reads `key[i]` instead of `key[j]`, so large block indexes or short keys can produce wrong hex output or an array bounds exception. It also samples UTF-8 bytes without validating full code-point boundaries.

## Test Signals
Tests should dump empty files, compressed and uncompressed files, files with user metadata blocks, non-ASCII/binary end keys, and malformed or edge metadata sizes. A targeted regression should exercise a binary key in a data block whose block index differs from the byte sample index.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/TFileDumper.java -->
