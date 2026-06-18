# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/JournalTestUtils.java

## Purpose
`JournalTestUtils` centralizes test setup for journal systems and embedded journal port allocation.

## Important APIs, Types, and Functions
It exposes `createEmbeddedJournalTestPorts`, `createJournalSystem(TemporaryFolder)`, and `createJournalSystem(String)`.

## Control Flow, State, and Persistence
Port creation obtains free ports, writes comma-separated embedded journal addresses plus hostname and port into global configuration, and returns the allocated port list. Journal-system creation builds a `JournalSystem` at a temporary URI with zero quiet time for master process tests.

## Dependencies and Integration Points
It depends on `PortRegistry`, global `Configuration`, `PropertyKey` journal settings, `TemporaryFolder`, `URI`, and `JournalSystem.Builder`.

## Risks
Free-port allocation can race with other processes before use. The helper mutates global configuration, so callers must reload properties after tests.

## Test Signals
This file has no direct tests; its value is consistent journal setup for replication and journal context tests.
