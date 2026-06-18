# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/LineReader.java

## Purpose

`LineReader` reads records from an `InputStream` into Hadoop `Text`, supporting default CR/LF/CRLF line endings or a custom byte delimiter.

## Important APIs, Types, And Functions

Constructors accept stream, buffer size, `Configuration`, and optional delimiter bytes. Public APIs are `readLine(Text,int,int)`, `readLine(Text,int)`, `readLine(Text)`, `close()`, and `getIOStatistics()`. Protected/test helpers expose buffer position/size and `unsetNeedAdditionalRecordAfterSplit()`. Core implementations are `readDefaultLine()` and `readCustomLine()`.

## Control Flow, State, And Persistence

The reader maintains a byte buffer, length, and position across calls. Default line reading handles LF, CR, and CRLF, including CR at buffer boundaries. Custom delimiter reading tracks partial delimiter matches and ambiguous bytes so split readers can avoid duplicate or missing records. It truncates stored `Text` to `maxLineLength` while still consuming bytes up to a record boundary or the consume hint. State is in-memory stream/buffer state; no persistence.

## Dependencies And Integration Points

It depends on `Configuration`, `Text`, filesystem `IOStatisticsSource`, and `IO_FILE_BUFFER_SIZE_KEY`. MapReduce input formats rely on it for split-aware line and custom-record reading.

## Risks And Test Signals

Delimiter boundary logic is subtle, especially at split boundaries and EOF. Tests should cover CR, LF, CRLF, unterminated final lines, very long lines with truncation, consume-limit overshoot, custom delimiters spanning buffers, ambiguous delimiter tails, IO statistics delegation, and close behavior.
