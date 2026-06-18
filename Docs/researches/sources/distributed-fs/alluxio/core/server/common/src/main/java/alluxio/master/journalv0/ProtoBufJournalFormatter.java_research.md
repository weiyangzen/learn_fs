# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/ProtoBufJournalFormatter.java

## Purpose
`ProtoBufJournalFormatter` is the legacy formatter implementation for protobuf-delimited journal entries. It writes length-delimited `JournalEntry` records and reads them back while tracking the latest sequence number.

## Important APIs, Types, and Functions
It implements `serialize(JournalEntry, OutputStream)` with `writeDelimitedTo()` and `deserialize(InputStream)` by returning an anonymous `JournalInputStream`. The reader uses `ProtoUtils.readRawVarint32()`, a reusable 1 KiB buffer for small entries, `JournalEntry.parseFrom()`, and `getLatestSequenceNumber()`.

## Control Flow, State, and Persistence
On read, the stream consumes the first byte, returns `null` for EOF, decodes the varint size, reads exactly that many bytes, logs and returns `null` for truncated entries, parses the entry, and records its sequence number. It does not close or advance any outer journal state except through the wrapped input stream.

## Dependencies and Integration Points
It depends on generated journal protobufs, `ProtoUtils`, Java I/O, and SLF4J. It is used by UFS readers/writers and `JournalTool`.

## Risks and Test Signals
Risks include memory allocation for very large entry sizes, accepting truncated tail entries as end of stream, and compatibility with protobuf delimiter semantics. Signals are exact round trips, latest-sequence updates, corrupted-tail behavior during log replay, and compatibility with older generated `JournalEntry` schemas.
