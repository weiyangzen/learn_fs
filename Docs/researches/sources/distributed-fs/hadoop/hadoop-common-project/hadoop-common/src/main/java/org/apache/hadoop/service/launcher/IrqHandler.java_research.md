<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/IrqHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/IrqHandler.java

Source read size: 176 lines, 4582 bytes.

## Purpose
Wrapper around JVM signal handling that binds a named signal to a Hadoop callback and records how many times it has fired.

## Important APIs, Types, and Functions
Implements `SignalUtil.Handler`. Important methods are `bind()`, `raise()`, `handle()`, `getName()`, `getSignalCount()`, and `toString()`. Nested `Interrupted` is the callback interface, and nested `InterruptData` carries signal name and number.

## Control Flow, State, and Persistence Behavior
Construction validates signal name and callback. `bind()` creates a `SignalUtil.Signal` and registers this handler, rejecting double binding and wrapping unsupported signal setup with an explanatory `IllegalArgumentException`. `handle()` increments an atomic count, creates `InterruptData`, logs, and calls the callback. `raise()` triggers the bound signal. State is in-memory only.

## Dependencies and Integration Points
Used by `InterruptEscalator` to wire signals such as TERM/INT into launcher shutdown logic. Depends on Hadoop `SignalUtil`, `Preconditions`, and SLF4J.

## Risks and Test Signals
Risks include JVM/platform signal portability, unsupported signal handling with `-Xrs`, callback exceptions propagating from signal handling, and `raise()` before successful bind. Test constructor validation, bind once, unsupported signal errors, callback data content, signal count increments, raise behavior, and integration with `InterruptEscalator`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/launcher/IrqHandler.java -->
