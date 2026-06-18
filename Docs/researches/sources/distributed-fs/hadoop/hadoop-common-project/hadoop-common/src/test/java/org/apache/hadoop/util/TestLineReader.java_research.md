# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestLineReader.java

Purpose: validates `LineReader` custom delimiter handling, especially delimiter prefixes split across buffer boundaries or overlapping with input text.

Important APIs and types: `LineReader(InputStream, byte[] delimiter)`, `readLine(Text)`, Hadoop `Text`, byte-array streams, and UTF-8 encoding.

Control flow: the first test intends to place a delimiter-prefix-like token at a 64 KiB buffer edge and verify the next record includes unmatched prefix bytes rather than dropping them. The second test uses delimiter `record` with leading delimiters, adjacent delimiters, and EOF fragments like `ecordrecorcore` to check empty records and partial delimiter retention. The third test uses data `aaaabccc` with delimiter `aaab` to cover overlapping delimiter prefixes.

State and persistence: parser state is in-memory buffer position plus delimiter-match progress. No files are created.

Dependencies and integration points: covers Hadoop text input splitting semantics used by record readers with non-newline delimiters.

Risks: partial delimiter matches can lose bytes, create extra records, or hang at EOF. Buffer-boundary bugs are particularly likely for multi-byte delimiters. Test signals are exact `Text.toString()` assertions for every returned record.
