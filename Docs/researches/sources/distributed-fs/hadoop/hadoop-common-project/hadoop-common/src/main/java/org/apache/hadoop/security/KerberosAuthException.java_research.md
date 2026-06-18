# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/KerberosAuthException.java


Purpose: `KerberosAuthException` is an IOException subtype for unrecoverable UGI Kerberos login/logout/subject errors where callers should not retry blindly.

Important APIs and types: It stores optional user, principal, keytab file, ticket cache file, and initial message fields with setters and getters. Constructors accept a message, cause, or initial message plus cause.

Control flow and state: `getMessage()` builds a contextual message from optional fields and the superclass message, using UGI exception message constants for labels. The object is mutable after construction so call sites can enrich context before throwing.

Dependencies and integration: It is used by `UserGroupInformation` Kerberos authentication flows and imports labels from `UGIExceptionMessages`.

Risks and test signals: Tests should verify message composition for each optional field and null initial message behavior. Since it can contain keytab and ticket-cache paths, logs should treat messages as security-sensitive.
