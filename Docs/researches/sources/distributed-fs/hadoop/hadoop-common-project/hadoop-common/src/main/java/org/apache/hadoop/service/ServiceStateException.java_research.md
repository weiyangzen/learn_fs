<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/ServiceStateException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/ServiceStateException.java

Source read size: 127 lines, 4046 bytes.

## Purpose
Runtime exception used when service lifecycle operations fail or invalid state transitions are attempted. It can also carry launcher exit-code semantics.

## Important APIs, Types, and Functions
Constructors accept message, cause, and optional exit code. `getExitCode()` exposes the exit status. Static `convert(Throwable)` and `convert(String, Throwable)` wrap checked exceptions unless the fault is already a runtime exception.

## Control Flow, State, and Persistence Behavior
The class stores an integer exit code, defaulting to a service-specific launcher failure code. Conversion methods preserve existing runtime exceptions and wrap other throwables with message/cause. No persistence is involved.

## Dependencies and Integration Points
Used by `AbstractService`, `CompositeService`, and `ServiceStateModel` when lifecycle transitions or hooks fail. Integrates with launcher exit-code interfaces.

## Risks and Test Signals
Risks include runtime exceptions bypassing wrapping and therefore not gaining a service exit code, and callers losing checked-exception type information. Test constructors, exit-code propagation, conversion of IOException/Exception, pass-through of RuntimeException, and messages from invalid service transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/service/ServiceStateException.java -->
