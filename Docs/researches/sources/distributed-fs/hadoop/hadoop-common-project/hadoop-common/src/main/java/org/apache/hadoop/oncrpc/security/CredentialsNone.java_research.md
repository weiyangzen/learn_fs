# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/CredentialsNone.java

Purpose: credential implementation for `AUTH_NONE`.

Important APIs/types/functions: constructor, `read`, and `write`.

Control flow: constructor sets credential length to zero. `read` consumes and validates a zero length. `write` emits zero length.

State and persistence: inherited length field only; no persistence.

Dependencies and integration: used by null-auth RPC calls such as portmap registration.

Risks: malformed nonzero length triggers precondition failure. No body bytes are skipped if length is invalid.

Test signals: RPC call and auth-info tests cover zero-length behavior.
