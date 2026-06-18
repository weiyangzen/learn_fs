<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/Contracts.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/Contracts.java

## Purpose
`Contracts` provides lightweight argument checking helpers for metrics2 code, supplementing generic precondition utilities with return-the-argument convenience methods.

## Important APIs and Types
The class is private and non-instantiable. It offers overloaded `checkArg` methods for object, int, long, float, and double arguments.

## Control Flow
Each overload checks a supplied boolean expression. If false, it throws `IllegalArgumentException` with `msg + ": " + arg`; otherwise it returns the original argument.

## State and Persistence
There is no state and no persistence.

## Dependencies and Integration Points
It is available to metrics2 utility/source/sink code for local validation. It depends only on Hadoop classification annotations.

## Risks and Test Signals
Because the caller supplies the boolean expression, incorrect predicates are not detectable here. The message always includes the argument, which can leak sensitive values if misused. Tests should cover every overload, true-path value preservation, false-path exception type/message, and behavior with null object arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/Contracts.java -->
