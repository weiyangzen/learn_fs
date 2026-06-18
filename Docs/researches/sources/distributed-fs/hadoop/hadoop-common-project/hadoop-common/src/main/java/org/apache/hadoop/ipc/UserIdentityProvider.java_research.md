<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/UserIdentityProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/UserIdentityProvider.java

## Purpose
`UserIdentityProvider` groups schedulable RPC calls by the caller's short user name, allowing scheduler/decay logic to aggregate all jobs from a user.

## Important APIs, Types, And Functions
- Implements `IdentityProvider`.
- `makeIdentity(Schedulable obj)` returns `obj.getUserGroupInformation().getShortUserName()` or `null` when no UGI is present.

## Control Flow
The provider fetches the `UserGroupInformation` from the `Schedulable`. A null UGI produces no identity; otherwise the short user name is returned.

## State And Persistence
Stateless; no fields and no persistent side effects.

## Dependencies And Integration Points
Used by RPC scheduling/fairness components such as decay schedulers and call queues that need an identity key. Depends on `Schedulable` and Hadoop security UGI.

## Risks And Edge Cases
Null identity must be handled by downstream scheduler code. Short-name mapping can collapse Kerberos principals or proxy identities depending on UGI configuration.

## Test Signals
Scheduler tests should cover null UGI, simple users, Kerberos principals mapped to short names, and proxy-user calls if identity semantics matter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/UserIdentityProvider.java -->
