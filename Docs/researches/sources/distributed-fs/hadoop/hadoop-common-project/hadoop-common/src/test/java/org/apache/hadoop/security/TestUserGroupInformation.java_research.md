# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestUserGroupInformation.java

Purpose: broad unit/integration coverage for `UserGroupInformation`: login modes, current/login users, proxy users, auth-to-local rules, group lookup metrics, credentials and tokens, subject propagation, Kerberos relogin timing, token import, and concurrency around subjects and credentials.

Important APIs and types: `UserGroupInformation`, `AuthenticationMethod`, `SaslRpcServer.AuthMethod`, `SecurityUtil`, `KerberosName`, `Subject`, `User`, `Credentials`, `Token`, `TokenIdentifier`, `KeyTab`, `KerberosTicket`, `LoginContext`, `SubjectInheritingThread`, `RetryPolicies`, metrics assertions, and Hadoop token config keys.

Control flow: setup installs a dummy JAAS configuration to catch accidental use of the JVM default login config, sets Kerberos realm properties, resets UGI before each test, and clears the login user after each test. Tests validate supported/unsupported login methods, proxy real-auth lookup, `doAs` scoping, OS group parity, constructor short-name rules under simple/Kerberos and Hadoop/MIT mechanisms, Kerberos rule initialization, equality by shared subject, group getters, token add/replace/named-token behavior, credential copy semantics, immutable token collections, token identifiers, auth method propagation, LoginContext preservation, UGI under non-Hadoop `Subject`, `getUGIFromSubject` principal conversion, relogin elapsed-time reflection, `setLoginUser`, private token exclusion, token race prevention, external token files, subject login with keytab private credential, renewal retry-time backoff, concurrent `getCurrentUser`, destroyed-ticket handling, and token import from config or system properties.

State and persistence: heavily mutates static UGI configuration/login user, KerberosName rules, JVM system properties, Hadoop metrics, token files under `target`, and `hadoop.token.files`/`HADOOP_TOKENS` properties. Some cleanup is explicit, but metrics and global state are central risk areas.

Dependencies and integration points: integrates OS `whoami`/`id -Gn` or winutils, Hadoop metrics, token storage files, JAAS, Kerberos principal parsing, Mockito spies/mocks, retry policies, and concurrent execution primitives.

Risks: large global-state surface can cause order-dependent failures. OS group tests are environment-dependent. Reflection against private `hasSufficientTimeElapsed` is brittle. Concurrency tests rely on timeouts and barriers. Token import ignores bad entries/files, so assertions focus on successful valid imports and dedupe behavior.

Test signals: very strong behavioral signal for UGI's core contract: subject identity, auth methods, credentials isolation, token persistence/import, private token filtering, Kerberos retry scheduling, concurrency safety, and global configuration handling.
