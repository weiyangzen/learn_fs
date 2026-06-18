
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileUnsortedByteArrays.java

Purpose: Tests TFile behavior when created without a comparator, so records are unsorted and searchable key operations are disallowed.

Important APIs and types: Uses `TFile.Writer` with `null` comparator, `TFile.Reader`, `Reader.Scanner`, AssertJ assertions, `createScanner()`, `createScannerByKey()`, `lowerBound()`, `upperBound()`, and `seekTo()`.

Control flow: Setup writes four deliberately out-of-order records and closes the file. Tests assert `reader.isSorted()` is false and entry count is four. Full scans verify insertion order and that key/value can be read in either order. Creating a scanner by key and performing lower-bound, upper-bound, or seek operations are expected to throw.

State and persistence: Creates a gzip-compressed temp file and deletes it after each test.

Dependencies and integration points: Guards the distinction between unsorted scan-only TFiles and sorted indexed TFiles.

Risks: Some unused fields and duplicate scan-range logic remain. Exceptions are broad, not type-specific.

Test signals: Confirms unsorted files remain sequentially readable while search APIs fail fast.
