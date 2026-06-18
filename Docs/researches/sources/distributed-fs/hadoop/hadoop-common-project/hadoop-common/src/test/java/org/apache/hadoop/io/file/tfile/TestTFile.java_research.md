
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFile.java

Purpose: Broad functional tests for TFile writer/reader basics, sorted and unsorted modes, duplicate keys, empty records, large values, prepared append streams, seeks, ranges, and metablocks.

Important APIs and types: Uses `TFile.Writer`, `TFile.Reader`, `Reader.Scanner`, `prepareAppendKey()`, `prepareAppendValue()`, `append()`, `createScanner()`, `createScannerByKey()`, `seekTo()`, `lowerBound()`, `upperBound()`, `prepareMetaBlock()`, and `getMetaBlock()`.

Control flow: Helpers write empty records, duplicated sorted records, a large 3 MB value, known-length stream records, and unknown-length stream records. Read helpers validate keys/values and seek/range behavior. `basicWithSomeCodec()` runs sorted tests for none and gz. `unsortedWithSomeCodec()` scans unsorted files. `testMetaBlocks()` writes named metadata blocks, rejects duplicates, reads them back, and rejects missing names.

State and persistence: Creates local filesystem TFiles under a temp root and deletes them after each scenario. Writers and readers own stream state.

Dependencies and integration points: Exercises Hadoop `FileSystem`, compression, TFile scanner locations, and metadata block APIs.

Risks: `readPrepWithUnknownLength()` has a loop condition `i < start`, so unknown-length read validation is effectively skipped. Large values stress memory and local disk.

Test signals: Strong format-level smoke coverage, with a noted gap around unknown-length reads.
