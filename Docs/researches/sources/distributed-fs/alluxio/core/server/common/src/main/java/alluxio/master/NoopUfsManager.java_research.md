# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/NoopUfsManager.java

## Purpose
`NoopUfsManager` is a UFS manager that suppresses under-storage connection work for tests and journal formatting.

## Important APIs, Types, And Functions
It extends `AbstractUfsManager` and overrides `connectUfs(UnderFileSystem fs)` with an empty implementation.

## Control Flow, State, Dependencies, Risks, And Tests
The inherited manager may still track mounts and UFS resources, but connection side effects are skipped. No persistence is performed by this override. Dependencies include `AbstractUfsManager` and `UnderFileSystem`. Risks are using it outside tests/formatting where actual UFS connectivity or authentication setup is required. Tests should verify operations that instantiate noop masters do not attempt UFS connects and that inherited manager behavior remains acceptable for formatting contexts.
