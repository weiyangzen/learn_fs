# sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/auth/CustomAuthPolicyTest.java

Purpose: concrete tests for fixed owner/group custom auth policy.

Important APIs and flow: setup writes custom auth class/user/group config, mocks `AlluxioFuseUtils.getUid` and `getGidFromGroupName`, creates and initializes `CustomAuthPolicy`, and reuses `AbstractAuthPolicyTest` behavior. `setUserGroupIfNeed` verifies a created URI receives configured owner/group; `getUidGid` verifies owner/group arguments are ignored and configured IDs are returned.

State, dependencies, risks, and signals: state is inherited fake file system plus fixed mocked IDs. It depends on PowerMock static mocking and global modifiable configuration. It signals startup validation and configured identity behavior, but does not test invalid custom user/group, parent fallback in `setUserGroup`, or interaction with a real system user database.
