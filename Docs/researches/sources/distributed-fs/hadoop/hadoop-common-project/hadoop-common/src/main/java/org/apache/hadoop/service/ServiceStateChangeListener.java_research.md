<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/ServiceStateChangeListener.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/ServiceStateChangeListener.java

Source read size: 50 lines, 1819 bytes.

## Purpose
Callback interface for receiving service lifecycle state changes.

## Important APIs, Types, and Functions
The single method is `stateChanged(Service service)`.

## Control Flow, State, and Persistence Behavior
Implementations are invoked synchronously by service listener containers after state transitions. The interface owns no state or persistence.

## Dependencies and Integration Points
Used by `AbstractService`, `ServiceOperations.ServiceListeners`, and `LoggingStateChangeListener`. Enables daemon diagnostics, testing hooks, and cross-service coordination.

## Risks and Test Signals
Risks are implementation-side: slow or throwing listeners can delay or disrupt notification unless the caller catches exceptions. Test callback invocation on init/start/stop, removal before notification, duplicate registration handling, and exception handling in the service that owns the listener list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/ServiceStateChangeListener.java -->
