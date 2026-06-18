# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/fuse/auth/AuthPolicyFactory.java

Purpose: configuration-driven factory for `AuthPolicy` implementations.

Important APIs and flow: `create(FileSystem, AlluxioConfiguration, FuseFileSystem)` reads `FUSE_AUTH_POLICY_CLASS`, validates it implements `AuthPolicy`, reflectively calls static `create(FileSystem, AlluxioConfiguration, Optional<FuseFileSystem>)`, invokes `init`, and returns the policy.

State, dependencies, risks, and tests: no persistent state. It depends on configuration class loading and reflection. Risks include runtime-only validation, strict static method signature, reflective exception wrapping, and requiring a present FUSE filesystem for policies such as `SystemUserGroupAuthPolicy`. Covered indirectly by JNI filesystem construction and auth policy tests.
