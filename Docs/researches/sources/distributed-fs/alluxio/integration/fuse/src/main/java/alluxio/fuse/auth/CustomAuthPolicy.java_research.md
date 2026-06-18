# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/auth/CustomAuthPolicy.java

Purpose: auth policy that forces a configured Alluxio owner and group for newly created FUSE paths while still allowing explicit chown to other valid users/groups through the parent policy.

Important APIs and flow: static `create` reads custom user/group properties, validates they are non-empty, resolves uid/gid, constructs fixed `SetAttributePOptions`, and returns the policy. `setUserGroupIfNeeded` always sets the configured owner/group. `setUserGroup` fast-paths matching uid/gid to the configured options, otherwise delegates to `LaunchUserGroupAuthPolicy`.

State, dependencies, risks, and tests: state includes fixed uid/gid and set-attribute options. It depends on shell-backed uid/gid resolution and Alluxio `setAttribute`. Risks are startup failure when configured principals do not exist locally, and log message argument ordering appears swapped for owner/uid and group/gid. `CustomAuthPolicyTest` mocks ID resolution, verifies configured owner/group assignment, and verifies fixed uid/gid reporting.
