# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/security/MockNotRunningSecretManager.java

Purpose: mock secret manager that can be reflectively constructed but is intentionally not running, used to test router startup/error behavior with an unusable delegation-token manager.

Important APIs/types/functions: extends `AbstractDelegationTokenSecretManager<DelegationTokenIdentifier>`, has a `Configuration` constructor, and implements `createIdentifier()` by returning an HDFS `DelegationTokenIdentifier`.

Control flow: like the running mock, this class only supplies construction and identifier creation. Its value comes from not starting or not satisfying runtime expectations in `RouterSecurityManager` tests, allowing failure paths to be exercised.

State and persistence behavior: no external persistence; any superclass in-memory state is not relied upon as active service state. Integration points are router security manager reflection and service lifecycle validation. Risks are semantic ambiguity: the name and test use must clearly indicate that construction success does not mean the manager is operational. Test signals are indirect in `TestRouterSecurityManager`, where operations with this class are expected to throw service-state errors.
