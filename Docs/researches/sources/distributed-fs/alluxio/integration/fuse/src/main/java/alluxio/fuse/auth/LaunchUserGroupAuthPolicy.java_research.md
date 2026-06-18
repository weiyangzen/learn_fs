# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/auth/LaunchUserGroupAuthPolicy.java

Purpose: default auth policy that treats the user launching the FUSE process as the owner/group baseline.

Important APIs and flow: `init` resolves launch uid/gid. `setUserGroupIfNeeded` is a no-op because Alluxio client creation already uses the launch user. `setUserGroup` skips work for launch uid/gid, checks existing `URIStatus`, caches uid-to-name and gid-to-name lookups, builds `SetAttributePOptions` for resolvable IDs, and updates Alluxio attributes only when needed.

State, dependencies, risks, and tests: state includes launch ids and two Guava lookup caches. It depends on Alluxio status/setAttribute and local user/group shell utilities. Risks include stale user/group cache entries, partial updates when only uid or gid resolves, and exceptions if launch identity cannot be resolved. `AbstractAuthPolicyTest` verifies chown behavior and no duplicate `setAttribute` when owner/group already match.
