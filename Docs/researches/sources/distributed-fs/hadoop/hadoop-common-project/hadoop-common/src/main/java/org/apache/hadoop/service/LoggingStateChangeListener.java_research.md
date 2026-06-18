<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/LoggingStateChangeListener.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/LoggingStateChangeListener.java

Source read size: 64 lines, 1982 bytes.

## Purpose
Simple `ServiceStateChangeListener` implementation that logs service state changes.

## Important APIs, Types, and Functions
Constructors accept default logging or custom `Logger` and `Level`. `stateChanged(Service service)` logs service name and new state at the configured level.

## Control Flow, State, and Persistence Behavior
The listener is stateless except for logger and level references. It is called synchronously by `ServiceOperations.ServiceListeners` during service notifications and has no persistence.

## Dependencies and Integration Points
Integrates with `AbstractService` local/global listener registration and SLF4J logging. It is useful for daemon diagnostics and tests that need visible lifecycle transitions.

## Risks and Test Signals
Risks are low: logging at an unavailable level or expensive service `toString()`/name access during notification. Test constructor defaults, custom level behavior, registration as local and global listener, and resilience when multiple services emit state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/LoggingStateChangeListener.java -->
