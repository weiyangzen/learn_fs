
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileSeek.java

Purpose: Performance-style test and command-line tool for TFile creation and random lower-bound seeking.

Important APIs and types: Uses `KVGenerator`, `KeySampler`, `RandomDistribution.Zipf/Flat`, `NanoTimer`, Commons CLI `Options`, `TFile.Writer`, `TFile.Reader`, and `Reader.Scanner.lowerBound()`.

Control flow: `setUp()` parses default or supplied options, configures FS buffer sizes, random distributions, and generators. `createTFile()` writes sorted random records until target file size. `seekTFile()` samples keys between first and last keys, performs lower-bound seeks, reads hit entries, and prints timing and hit/miss statistics. `testSeeks()` skips unsupported compression, then creates and reads according to options.

State and persistence: Writes a temp TFile under configurable root and deletes it in teardown. Options hold seed, codec, sizes, and operation mode.

Dependencies and integration points: Exercises TFile indexing, scanner lower bounds, compression support detection, and local filesystem buffering.

Risks: Timing output is environment-dependent. Random seed defaults to `System.nanoTime()`, reducing reproducibility. Miss-rate math divides by hits.

Test signals: Useful for seek performance smoke and scanner behavior under generated sorted data.
