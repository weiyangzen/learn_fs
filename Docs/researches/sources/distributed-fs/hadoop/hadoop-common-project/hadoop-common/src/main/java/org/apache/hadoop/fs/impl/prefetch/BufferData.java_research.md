# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/BufferData.java

## Purpose
Stateful wrapper for one block ByteBuffer used by caching/prefetching block managers. It enforces buffer lifecycle transitions and detects data mutation after readiness.

## Important APIs, Types, and Functions
State enum UNKNOWN/BLANK/PREFETCHING/CACHING/READY/DONE; constructor; getters; getChecksum(); setPrefetch(); setCaching(); setReady(); setDone(); updateState(); throwIfStateIncorrect(); stateEqualsOneOf(); toString().

## Control Flow
Buffers start BLANK. setPrefetch requires BLANK and stores a future. setCaching requires PREFETCHING or READY. setReady converts the buffer to a read-only view, computes CRC32, rewinds it, and transitions from expected states. setDone recomputes checksum if set and fails if content changed, then clears action and marks DONE.

## State and Persistence Behavior
Stores block number, ByteBuffer/read-only view, volatile state, action Future, and checksum. No persistence.

## Dependencies and Integration Points
Used by prefetch/caching block managers and tests to manage in-memory block data.

## Risks and Test Signals
Risks are checksum zero sentinel collisions, state transition strictness, read-only buffer expectations, and synchronization around state/action. Tests should cover valid/invalid transitions, checksum mutation detection, future reporting, and buffer position preservation.
