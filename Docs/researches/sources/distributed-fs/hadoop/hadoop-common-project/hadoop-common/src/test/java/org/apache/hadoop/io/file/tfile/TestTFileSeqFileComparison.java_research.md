
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileSeqFileComparison.java

Purpose: Performance comparison tool and JUnit smoke test that writes and reads similar random workloads through TFile and SequenceFile under none, LZO, and gzip compression.

Important APIs and types: Defines `KVAppendable`, `KVReadable`, `TFileAppendable`, `TFileReadable`, `SeqFileAppendable`, `SeqFileReadable`, and option parser `MyOptions`. Uses `TFile.Writer/Reader`, `SequenceFile.Writer/Reader`, `Compression.Algorithm`, `BytesWritable`, Commons CLI, and Hadoop `Time`.

Control flow: Setup configures filesystem buffers and a random dictionary. `timeWrite()` generates random key/value lengths and dictionary-filled payloads until target file size. `timeRead()` scans all records. `compareRun()` runs SequenceFile write/read, TFile write/read twice, then SequenceFile again for each supported compression. `main()` supports standalone single-format create/read operations.

State and persistence: Creates performance files under a temp root and deletes them when read after creation. Options and dictionary are per test instance.

Dependencies and integration points: Bridges TFile, SequenceFile, Hadoop compression codecs, and filesystem buffering.

Risks: It is benchmark-like and prints timing rather than asserting throughput. CLI option definitions reuse `-o` for output buffer and key length, which may confuse parsing.

Test signals: Smoke coverage that both formats can write/read generated data with configured codecs.
