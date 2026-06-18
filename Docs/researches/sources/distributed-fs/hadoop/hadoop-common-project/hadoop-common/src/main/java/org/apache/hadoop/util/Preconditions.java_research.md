# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Preconditions.java

## Purpose
`Preconditions` is Hadoop's private replacement for the small subset of Guava precondition helpers used in common code. It validates null references, argument predicates, and state predicates while preserving familiar exception types.

## Important APIs, Types, And Functions
The class is final with only static helpers. Key APIs are `checkNotNull(T)`, `checkNotNull(T,Object)`, `checkNotNull(T,String,Object...)`, `checkNotNull(T,Supplier<String>)`, `checkArgument(...)`, and `checkState(...)`. Package-visible getters expose default messages for tests.

## Control Flow
Each method returns immediately on success. On failure it either stringifies an object message, formats a varargs template, or evaluates a supplier. Formatting/supplier failures are caught, logged at debug, and replaced by a default message before throwing `NullPointerException`, `IllegalArgumentException`, or `IllegalStateException`.

## State And Persistence
There is no mutable business state. Static constants hold default messages, and a static SLF4J logger records message-construction failures. Nothing is persisted.

## Dependencies And Integration Points
It depends on `java.util.function.Supplier`, SLF4J, and Hadoop audience/stability annotations. It is integrated anywhere Hadoop wants low-overhead validation without carrying a public Guava dependency.

## Risks
Supplier-based messages are evaluated only on failure, but a null supplier on a failed check becomes a debug log plus default message rather than exposing the supplier bug. Varargs formatting uses `String.format`, so invalid format strings do not propagate. Successful checks do not validate message templates.

## Test Signals
Useful tests verify successful identity return, exception type and message for each overload, fallback behavior when format/supplier evaluation fails, and debug-only logging of message construction errors.
