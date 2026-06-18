# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/auth/AuthPolicy.java

Purpose: abstraction for mapping FUSE/Alluxio ownership between numeric Unix IDs and Alluxio owner/group names.

Important APIs and flow: implementations initialize via `init`, optionally set owner/group after create or mkdir through `setUserGroupIfNeeded`, set explicit `uid`/`gid` through `setUserGroup`, and report current/default uid/gid. Default `getUid(owner)` and `getGid(group)` ignore their arguments and return policy defaults.

State, dependencies, risks, and tests: interface has no state. Implementations integrate with Alluxio `setAttribute`, FUSE context, and system user/group lookup. Risks are policy-specific performance and correctness differences. Auth tests exercise shared `setUserGroup` behavior and custom policy lookup.
