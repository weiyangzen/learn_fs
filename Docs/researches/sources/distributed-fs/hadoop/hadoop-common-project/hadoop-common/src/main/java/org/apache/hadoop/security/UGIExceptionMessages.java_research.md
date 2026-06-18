# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/UGIExceptionMessages.java

Purpose: package-private constants for standard `KerberosAuthException` and UGI login/logout error messages.

Important APIs/types/functions: string constants such as `FAILURE_TO_LOGIN`, `INVALID_UID`, `LOGIN_FAILURE`, `LOGOUT_FAILURE`, `MUST_FIRST_LOGIN`, `MUST_FIRST_LOGIN_FROM_KEYTAB`, `SUBJECT_MUST_CONTAIN_PRINCIPAL`, `SUBJECT_MUST_NOT_BE_NULL`, and `USING_TICKET_CACHE_FILE`. Private constructor enforces utility class pattern.

Control flow: none locally. `UserGroupInformation` imports these constants statically when throwing or wrapping Kerberos and login errors.

State/persistence: no mutable state, no persistence.

Dependencies/integration: integrated with `KerberosAuthException` message construction in UGI.

Risks: changing literal strings can break tests or downstream code that matches messages. Since the class is package-private, binary API impact is limited, but log/error compatibility still matters.

Test signals: UGI login failure paths, invalid UID OS-login path, null or principal-less subject login, relogin-before-login, keytab logout/relogin misuse, and message formatting in `KerberosAuthException`.
