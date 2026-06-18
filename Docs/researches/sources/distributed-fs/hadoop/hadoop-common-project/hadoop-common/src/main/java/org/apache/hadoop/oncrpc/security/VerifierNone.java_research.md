# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/VerifierNone.java

Purpose: verifier implementation for `AUTH_NONE`.

Important APIs/types/functions: singleton `INSTANCE`, constructor, `read`, and `write`.

Control flow: `read` consumes a length and requires zero. `write` emits zero length.

State and persistence: no body state; no persistence.

Dependencies and integration: used in most portmap and accepted/denied replies, and by `SysSecurityHandler`.

Risks: public constructor allows multiple instances despite singleton. Malformed nonzero length throws precondition failure.

Test signals: reply and auth-info tests cover zero-length read/write.
