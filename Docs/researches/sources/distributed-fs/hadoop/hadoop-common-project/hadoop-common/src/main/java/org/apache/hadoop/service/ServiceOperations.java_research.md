<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/ServiceOperations.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/ServiceOperations.java

Source read size: 173 lines, 5725 bytes.

## Purpose
Utility methods and listener container for working with `Service` instances, mainly safe stopping and robust listener notification.

## Important APIs, Types, and Functions
Static APIs are `stop(Service)`, `stopQuietly(Service)`, deprecated `stopQuietly(Log, Service)`, and `stopQuietly(Logger, Service)`. Nested `ServiceListeners` supports `add()`, `remove()`, `reset()`, and `notifyListeners(Service)`.

## Control Flow, State, and Persistence Behavior
`stop()` simply calls `service.stop()` if non-null. Quiet variants catch `Exception`, log a warning, and return the exception. `ServiceListeners` maintains a synchronized list, ignores duplicate registrations, snapshots listeners before notification, and invokes callbacks outside the synchronized block so listeners may register/unregister during callbacks. No persistent state exists.

## Dependencies and Integration Points
Used by `AbstractService`, `CompositeService`, shutdown hooks, and cleanup paths. Integrates with SLF4J and legacy commons logging.

## Risks and Test Signals
Risks include `stopQuietly(Logger, null)` being safe but logging paths assuming service non-null only after an exception, listener callback exceptions propagating to callers of `notifyListeners()`, and no Throwable catching in stop utilities. Test null stop, exception return/logging, duplicate listeners, mutation during notification, reset, callback ordering, and interaction with `AbstractService` listener exception handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/ServiceOperations.java -->
