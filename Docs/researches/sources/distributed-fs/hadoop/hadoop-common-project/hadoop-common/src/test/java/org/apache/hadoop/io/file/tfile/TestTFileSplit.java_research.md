
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileSplit.java

Purpose: Tests TFile split scanning by byte range and by record number, plus record-number/location conversion symmetry.

Important APIs and types: Uses `TFile.Writer`, `TFile.Reader`, `Reader.createScannerByByteRange()`, `createScannerByRecordNum()`, `getRecordNumNear()`, `getLocationByRecordNum()`, `getRecordNumByLocation()`, and `Reader.Scanner.getRecordNum()`.

Control flow: `createFile()` writes sorted records with a chosen compression. `readFile()` divides the file into ten byte ranges, scans each, asserts each split has records, and checks total rows equal reader entry count. `readRowSplits()` divides by record numbers and checks scanner record numbers before and after entry reads. `checkRecNums()` validates offset edge cases and random record/location symmetry. The test runs uncompressed 100k records and gzip 500k records.

State and persistence: Creates temp TFiles per compression and deletes them after each scenario.

Dependencies and integration points: Exercises TFile indexing used by MapReduce-style input splits and record-based scanners.

Risks: Large record counts can be slow. Random begin/end selection is nondeterministic.

Test signals: Strong coverage for split boundary correctness and record-number APIs.
