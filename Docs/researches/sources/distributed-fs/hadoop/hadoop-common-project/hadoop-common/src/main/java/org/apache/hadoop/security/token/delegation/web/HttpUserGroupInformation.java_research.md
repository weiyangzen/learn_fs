<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/HttpUserGroupInformation.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/HttpUserGroupInformation.java

Source read size: 41 lines, 1544 bytes.

## Purpose
Small public utility for code running inside Hadoop HTTP request handling to retrieve the current request's `UserGroupInformation`.

## Important APIs, Types, and Functions
The only API is static `get()`, which delegates to `DelegationTokenAuthenticationFilter.getHttpUserGroupInformationInContext()`.

## Control Flow, State, and Persistence Behavior
No state is owned by this class. It reads the filter-managed thread-local UGI and returns null when the current thread is not processing an authenticated request through the delegation-token filter.

## Dependencies and Integration Points
Depends on `UserGroupInformation` and the filter's thread-local context. It is a bridge for servlets and HTTP endpoints that need Hadoop identity rather than only servlet principals.

## Risks and Test Signals
Risks include callers assuming non-null outside filter scope or after asynchronous thread handoff. Test within authenticated requests, delegation-token-authenticated requests, proxy-user requests, unauthenticated requests, and worker threads that do not inherit the filter context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/HttpUserGroupInformation.java -->
