# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/oncrpc/security/TestCredentialsSys.java

Purpose: Unit tests for AUTH_SYS credential XDR serialization and credential-length padding behavior.

Important APIs/types/functions: `CredentialsSys`, setters/getters for UID/GID/stamp/hostName, `write`, `read`, `getCredentialLength`, and `XDR.asReadOnlyWrap`.

Control flow: one test round-trips UID/GID/stamp through XDR. Two hostname tests write/read hostnames whose lengths are not and are multiples of four, asserting UID/GID/stamp and credential length of 32.

State and persistence: local credential objects and in-memory XDR buffers.

Dependencies/integration points: ONC/RPC AUTH_SYS credential encoding for NFS/portmap requests.

Risks: XDR padding/length calculation is wire-compatible behavior; tests do not assert hostName after read, group list behavior, or maximum host size.

Test signals: validates basic credential field persistence and fixed opaque padding alignment for hostnames.
