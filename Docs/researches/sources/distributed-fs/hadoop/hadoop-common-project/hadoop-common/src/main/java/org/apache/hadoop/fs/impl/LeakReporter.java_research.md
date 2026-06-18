# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/LeakReporter.java

## Purpose
Closeable leak sentinel that reports unclosed resources through a dedicated resource-leaks logger and optional cleanup action.

## Important APIs, Types, and Functions
Constructor captures resource description, BooleanSupplier isOpen, and RunnableRaisingIOE closeAction; close(); getLeakException(); isClosed(); toString(); finalize/reporting behavior through leak exception stack.

## Control Flow
An AtomicBoolean ensures close action runs once. If the object is finalized while isOpen reports true, it logs a leak with the captured allocation exception and invokes closeAction.

## State and Persistence Behavior
Stores closed flag, supplier, close action, and allocation stack exception. No persistence, but affects cleanup of leaked resources.

## Dependencies and Integration Points
Depends on SLF4J, RunnableRaisingIOE, BooleanSupplier, AtomicBoolean. Used by FS stream/store code to detect lifecycle leaks.

## Risks and Test Signals
Risks include finalizer timing, closeAction throwing, false positives from isOpen suppliers, and strong references captured in suppliers. Tests should cover idempotent close, leak exception presence, and close action invocation.
