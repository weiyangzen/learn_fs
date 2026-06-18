# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestIdentityProviders.java

Purpose: verifies pluggable IPC identity provider loading and default user identity extraction from a `Schedulable`.

Important APIs/types/functions: `IdentityProvider`, `UserIdentityProvider`, `Schedulable`, `CommonConfigurationKeys.IPC_IDENTITY_PROVIDER_KEY`, `Configuration.getInstances()`, `UserGroupInformation`, and local `FakeSchedulable`.

Control flow: one test sets the identity provider config key to `UserIdentityProvider`, loads provider instances, and checks type/size. The second creates `UserIdentityProvider`, asks it to make an identity for `FakeSchedulable`, compares that to the current UGI username, and verifies the default `Schedulable.getCallerContext()` path throws `UnsupportedOperationException`.

State and persistence behavior: no persistent state. The only mutable state is a local `Configuration`; current-user lookup depends on process security context.

Dependencies and integration points: ties call scheduling identity to Hadoop configuration plugin loading and UGI. This is used by fair/decay schedulers and queue metrics that group work by caller identity.

Risks and test signals: small but important signal that provider class names remain loadable through configuration and that default schedulable identity remains username-based. The current-user dependency can vary by test environment but should be stable under Hadoop's test UGI setup.
