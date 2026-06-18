# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/audit/AuditStatisticNames.java

## Purpose
Constant holder for audit-related metric/statistic names.

## Important APIs, Types, and Functions
AUDIT_FAILURE, AUDIT_REQUEST_EXECUTION, AUDIT_SPAN_CREATION, AUDIT_ACCESS_CHECK_FAILURE.

## Control Flow
No flow; private constructor.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Integrated with filesystem audit metrics and statistics collectors.

## Risks and Test Signals
Tests should verify metrics producers and consumers use the same names.
