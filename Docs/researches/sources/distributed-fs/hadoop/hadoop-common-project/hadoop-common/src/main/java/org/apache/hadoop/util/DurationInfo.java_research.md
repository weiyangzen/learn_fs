# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/DurationInfo.java

## Purpose

`DurationInfo` is a small `AutoCloseable` duration logger built for try-with-resources blocks. It extends `OperationDuration`, logs a "Starting" line at construction, and logs the elapsed duration from `close()`.

## Important APIs, Types, And Functions

The public constructors accept a `Logger`, an optional `logAtInfo` flag, and `String.format` style text. `getFormattedText()` memoizes the formatted message from a `Supplier<String>`. `toString()` appends the inherited duration text, and `close()` calls `finished()` before logging at INFO or DEBUG.

## Control Flow, State, And Persistence

Construction records the start timestamp in `OperationDuration`, stores the logger, lazily formats text, and logs the start message only when the selected level is enabled. Closing updates the finish timestamp and emits the final message. State is per-instance and in-memory only; no persistent data is written beyond logging.

## Dependencies And Integration Points

It depends on SLF4J and `OperationDuration`. Callers integrate it around expensive operations such as configuration, filesystem, or service work where scoped elapsed-time logging is useful.

## Risks And Test Signals

The formatted text is cached, so mutable arguments are captured at first formatting rather than close time. `String.format` exceptions can be thrown during construction. Tests should cover INFO and DEBUG modes, lazy formatting, `toString()` duration text, and try-with-resources close behavior.
