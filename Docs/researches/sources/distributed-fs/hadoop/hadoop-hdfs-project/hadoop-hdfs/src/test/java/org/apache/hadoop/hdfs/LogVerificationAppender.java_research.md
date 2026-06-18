# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/LogVerificationAppender.java

`LogVerificationAppender` is a Log4j 1.x in-memory appender used by tests to verify expected log output. It captures `LoggingEvent` instances and exposes counters for throwable messages or rendered log messages containing a substring.

It extends `AppenderSkeleton`. `requiresLayout` returns false, `close` is a no-op, `append` records events in an `ArrayList`, and `getLog` returns a defensive copy. `countExceptionsWithMessage` checks each event's `ThrowableInformation` and throwable message, while `countLinesWithMessage` checks `getRenderedMessage`.

State is only the in-memory event list; nothing is persisted or automatically cleared. Dependencies are Log4j `AppenderSkeleton`, `LoggingEvent`, and `ThrowableInformation`. Tests attach the appender to a logger, execute a path expected to log, then assert counts.

Risks include no synchronization for concurrent logging, possible `NullPointerException` when a throwable has a null message, and broad substring matching that can overcount. Test signals are the returned counts of matching exception or log-message events.
