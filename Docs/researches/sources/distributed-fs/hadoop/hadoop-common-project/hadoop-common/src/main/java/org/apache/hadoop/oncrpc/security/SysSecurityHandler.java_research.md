# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/security/SysSecurityHandler.java

Purpose: `SecurityHandler` implementation for `AUTH_SYS` credentials.

Important APIs/types/functions: constructor, `getUser`, `shouldSilentlyDrop`, `getVerifer`, `getUid`, `getGid`, and `getAuxGids`.

Control flow: maps uid to a username via `IdMappingServiceProvider`, returns false for silent drop, returns a new `VerifierNone`, and exposes uid/gid/aux gids from `CredentialsSys`.

State and persistence: stores credential object and ID mapping provider references; no persistence in this class.

Dependencies and integration: used by NFS/ONC RPC services that accept AUTH_SYS. Depends on Hadoop security ID mapping.

Risks: user identity depends on external id mapping configuration and cache. The handler does not authorize by itself; it only exposes identity attributes. Returns a new verifier each call rather than singleton.

Test signals: service security tests should cover uid-to-user fallback and gid/aux gid propagation.
