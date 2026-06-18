# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/AccessControlException.java


Purpose: `AccessControlException` is Hadoop's public IOException subtype for authorization and permission-denied failures.

Important APIs and types: It is `InterfaceAudience.Public` and `InterfaceStability.Evolving`. Constructors support a default "Permission denied." message for `RemoteException` unwrapping, an explicit detail string, and a throwable cause.

Control flow and state: The class carries only exception state inherited from `IOException`. There is no custom control flow beyond constructor selection and the fixed `serialVersionUID`.

Dependencies and integration: It is thrown across Hadoop security, filesystem, and IPC authorization paths and can cross RPC boundaries through Hadoop's remote exception handling.

Risks and test signals: Tests should verify default-message compatibility and cause retention. Callers should avoid treating all `IOException` instances as retryable when this subtype indicates an authorization decision.
