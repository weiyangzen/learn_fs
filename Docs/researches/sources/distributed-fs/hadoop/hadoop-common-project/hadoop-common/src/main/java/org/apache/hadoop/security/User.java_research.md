# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/User.java

Purpose: package-private JAAS `Principal` representing Hadoop's canonical user identity inside a `Subject`, storing full name, short name, authentication method, login context, and last login timestamp.

Important APIs/types/functions: constructors normalize short name with `HadoopKerberosName.getShortName`. `getName` returns full principal; `getShortName` returns local short user. `setAuthenticationMethod`/`getAuthenticationMethod`, `setLogin`/`getLogin`, and `setLastLogin`/`getLastLogin` support UGI state transitions and relogin throttling.

Control flow: created by `UserGroupInformation.HadoopLoginModule`, remote/proxy user constructors, and tests. Constructor rejects illegal Kerberos/user names by wrapping short-name resolution failures as `IllegalArgumentException`.

State/persistence: immutable full and short names; volatile mutable auth method, login context, and last login. No durable persistence.

Dependencies/integration: tightly coupled to `UserGroupInformation`, `AuthenticationMethod`, `LoginContext`, and `HadoopKerberosName` auth-to-local rules.

Risks: `equals` compares full name and auth method but `hashCode` only uses full name, which is legal but can increase collisions. Auth method mutability means equality can change after insertion into hash collections. Login context is volatile but its internals require UGI locking discipline.

Test signals: short-name rule failures, equality across auth methods, mutable auth method effects, last-login updates during relogin, and subject principal extraction by UGI.
