# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/auth/SystemUserGroupAuthPolicyTest.java

Purpose: unit coverage for `SystemUserGroupAuthPolicy`, which maps FUSE request uid/gid values to system user/group names and writes those into Alluxio metadata. The setup creates the policy with the optional FUSE filesystem, initializes it, and PowerMocks `AlluxioFuseUtils` static user/group lookup methods.

Important APIs and control flow: `setUserGroupIfNeed` builds a `FuseContext` backed by a 32-byte `ByteBuffer`, sets uid/gid, injects it through `mFuseFileSystem.setContext`, and verifies `URIStatus` owner/group become `systemUser` and `systemGroup`. `getUidGid` confirms reverse lookup via `getUid(USER)` and `getGid(GROUP)`.

State, dependencies, integration, risks, tests: state flows through the FUSE context and Alluxio file status metadata. Dependencies include PowerMock, Mockito matchers, `FuseContext`, and the inherited test filesystem. The test signal is strong for successful mapping but does not cover unknown uid/gid, missing optional FUSE filesystem, or failed static lookups.
