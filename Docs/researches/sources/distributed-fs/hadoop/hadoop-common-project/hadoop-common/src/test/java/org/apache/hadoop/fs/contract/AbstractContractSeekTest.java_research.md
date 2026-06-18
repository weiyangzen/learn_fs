# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractSeekTest.java

Purpose: `AbstractContractSeekTest` validates seeking, positioned reads, readFully semantics, EOF behavior, and closed-stream behavior for filesystems declaring `SUPPORTS_SEEK`.

Important APIs and types: it uses `FSDataInputStream`, `FileSystem`, `Path`, `EOFException`, `Configuration`, `CommonConfigurationKeysPublic.IO_FILE_BUFFER_SIZE_KEY`, `ContractOptions`, and `ContractTestUtils.verifyRead`. Test files include a deterministic `smallSeekFile` and a zero-byte file.

Control flow: `setup()` gates on seek support, creates the deterministic data file and zero-byte file, and configures a 4096 byte IO buffer. Tests cover zero-byte reads, block reads, operations after close, negative seek, ordinary seeks, reading past EOF, seeking past EOF then recovery, large-file seeks beyond buffer boundaries, positioned reads that must not change stream position, randomized seek/read sequences, readFully on zero-byte and small files, invalid offsets and lengths, reads past EOF, null buffers, and reading exactly at EOF.

State and persistence behavior: tests create deterministic files whose byte value equals offset modulo the dataset range, enabling direct validation after seek. `instream` is closed in teardown.

Dependencies and integration points: `assumeSupportsPositionedReadable()` uses `SUPPORTS_POSITIONED_READABLE`, defaulting true when seek is supported. Contract flags also control seek-on-closed, available-on-closed, and seek-past-EOF behavior. Random seek count is controlled by `TEST_RANDOM_SEEK_COUNT`.

Risks: `testRandomSeeks()` uses an unseeded `Random`, so reproducing failures requires the logged last ten seek/read pairs rather than a seed. Relaxed exception handling accepts several exception classes for invalid positioned reads because implementations differ. Closed-stream capabilities are explicitly variable.

Test signals: pass indicates seek positions are accurate, data read after seeks is correct, positioned reads preserve current position, EOF and invalid-argument behavior is coherent, streams recover after past-EOF seeks where allowed, and random seek/read sequences do not expose buffering bugs.
