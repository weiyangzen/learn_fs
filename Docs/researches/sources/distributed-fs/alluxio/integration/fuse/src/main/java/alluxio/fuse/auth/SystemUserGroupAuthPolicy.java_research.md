# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/auth/SystemUserGroupAuthPolicy.java

Purpose: auth policy that maps each FUSE request to the actual caller uid/gid from the FUSE context.

Important APIs and flow: static `create` constructs the policy; constructor requires a present `FuseFileSystem`. `setUserGroupIfNeeded` reads `getContext().uid/gid` and delegates to `setUserGroup`. `getUid`/`getGid` return current context IDs, while owner/group-specific overloads resolve names via `AlluxioFuseUtils`.

State, dependencies, risks, and tests: state is inherited file system references plus reliance on live FUSE context. It depends on JNI FUSE context and shell user/group resolution. Risks include performance overhead on create/mkdir, null or stale context outside callbacks, and local principal mismatch across clients. Covered indirectly through `AbstractAuthPolicyTest` infrastructure and JNI create/getattr paths.
