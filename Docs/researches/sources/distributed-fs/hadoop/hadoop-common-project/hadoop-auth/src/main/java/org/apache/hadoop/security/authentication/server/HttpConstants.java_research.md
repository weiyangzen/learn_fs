# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/HttpConstants.java

Purpose: central constants for HTTP authentication header names and scheme strings used across Hadoop Auth client and server code.

Important APIs, types, and functions: defines `WWW_AUTHENTICATE_HEADER`, `AUTHORIZATION_HEADER`, `NEGOTIATE`, `BASIC`, and `DIGEST`; private constructor prevents instantiation.

Control flow: no runtime logic. Constants are referenced by Kerberos client/server handlers and scheme utility methods.

State and persistence: no state.

Dependencies and integration points: integrates SPNEGO, Basic, and Digest handling across client authenticators and server handlers.

Risks and test signals: typos would break protocol interoperability. Test signals are SPNEGO client/server tests and scheme utility tests that use these constants.
