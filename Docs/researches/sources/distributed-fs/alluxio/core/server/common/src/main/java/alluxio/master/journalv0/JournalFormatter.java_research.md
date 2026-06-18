# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/JournalFormatter.java

## Purpose
`JournalFormatter` abstracts serialization and deserialization of legacy journal entries. It lets storage implementations treat journal streams uniformly while the formatter owns entry framing.

## Important APIs, Types, and Functions
The interface defines `serialize(JournalEntry, OutputStream)` and `deserialize(InputStream)`. Its nested `Factory.create()` currently returns `ProtoBufJournalFormatter`.

## Control Flow, State, and Persistence
The formatter contract is stateless. Serialization writes one entry to an output stream; deserialization wraps an input stream in a `JournalInputStream` that yields entries until end of stream or truncation. Actual persistence is performed by the caller's streams.

## Dependencies and Integration Points
It depends on protobuf `JournalEntry`, Java I/O streams, `JournalInputStream`, and `ProtoBufJournalFormatter`. It is used by `UfsJournalReader`, `UfsJournalWriter`, and `JournalTool`.

## Risks and Test Signals
Risks include format changes that break replay compatibility and deserializers that treat corrupted tail bytes incorrectly. Signals are protobuf round trips, truncated-entry handling, sequence-number tracking, and ability of `JournalTool` to read production log files.
