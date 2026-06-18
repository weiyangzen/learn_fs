# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestServer.java

## Purpose

`TestServer` covers focused unit behavior in Hadoop IPC `Server`: socket binding with configured ranges, exception logging suppression/terse modes, exception-handler classification, and purge interval configuration.

## Important APIs, Types, And Functions

The file uses `Server.bind(...)`, anonymous `Server` subclasses over `LongWritable`, `Server.logException()`, `Server.ExceptionsHandler`, `addSuppressedLoggingExceptions()`, `addTerseExceptions()`, and `getPurgeIntervalNanos()`. It defines three dummy exception types to test logging classes.

## Control Flow

Binding tests occupy or create sockets, set a `TestRange` configuration, and verify `Server.bind()` picks a free port in range, binds without range, accepts empty range config, or throws `BindException` when the only configured port is occupied. Logging tests construct a server and mocked logger, then assert suppressed exceptions produce no logger calls, terse exceptions log only a message, and other exceptions log with stack trace. Handler tests add multiple exception classes and query classification. The purge test sets `IPC_SERVER_PURGE_INTERVAL_MINUTES_KEY` and compares nanos conversion.

## State And Persistence Behavior

State is local to sockets, a temporary server instance, mock invocation history, and server exception-handler sets. No filesystem persistence is involved. Socket cleanup is handled in `finally` blocks.

## Dependencies And Integration Points

The tests integrate with Java `ServerSocket`, Hadoop `Configuration`, IPC server internals, SLF4J logging, Mockito, and `CommonConfigurationKeysPublic`. They are a direct guard for server bootstrap and operator-facing exception logging behavior.

## Risks And Test Signals

Risks include port allocation races, platform socket semantics, accidental stack-trace logging for terse classes, and unit conversion errors for purge interval. Signals are bound socket assertions, caught `BindException`, zero/mock interaction checks, and exact nanos conversion for the purge interval.
