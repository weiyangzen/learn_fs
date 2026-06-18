# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/auth/LaunchUserGroupAuthPolicyTest.java

Purpose: unit coverage for `LaunchUserGroupAuthPolicy`, the FUSE auth policy that uses the process launch user and group rather than per-request FUSE context credentials. The test extends `AbstractAuthPolicyTest`, creates the policy with `LaunchUserGroupAuthPolicy.create(mFileSystem, Configuration.global(), Optional.empty())`, and calls `init()`.

Important APIs and control flow: `setUserGroupIfNeeded` is invoked on a non-existent `AlluxioURI` and must not create or mutate the file; `mFileSystem.getStatus` still throws `FileDoesNotExistException`. `getUid` and `getGid` accept arbitrary names but return `AlluxioFuseUtils.getSystemUid()` and `getSystemGid()`.

State, dependencies, integration, risks, tests: the file depends on PowerMock preparation for `AlluxioFuseUtils`, JUnit assertions, the inherited in-memory filesystem, and global Alluxio configuration. It checks that launch-user auth is stable and non-invasive. Risk is limited coverage: it does not test existing-file ownership mutation because the policy intentionally needs no owner/group update.
