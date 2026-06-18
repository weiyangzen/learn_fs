# sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/auth/AbstractAuthPolicyTest.java

Purpose: abstract test base and shared behavior test for FUSE auth policies.

Important APIs and flow: `setUserGroup` test spies `AlluxioFuseUtils` to resolve uid/gid to names, invokes the concrete `mAuthPolicy`, verifies owner/group in an in-memory file system, then calls again to verify no redundant `setAttribute` when status already matches. Nested `CustomContextFuseFileSystem` supplies a controllable FUSE context; nested `UserGroupFileSystem` implements enough `FileSystem` to store and return `URIStatus` from `setAttribute`/`getStatus` while throwing for unrelated APIs.

State, dependencies, risks, and signals: state is the in-memory URI-to-status map and selected auth policy from subclasses. It depends on PowerMock static spying and many `FileSystem` interface stubs. It signals idempotent chown behavior and partial fake status behavior. Risks include the fake file system not modeling create, permissions, or missing-owner defaults, and broad unsupported methods that can hide integration drift until compile time.
