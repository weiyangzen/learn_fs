# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/security/user/ServerUserState.java

## Purpose
`ServerUserState` provides a process-global server `UserState` built from global Alluxio configuration.

## Important APIs, Types, and Functions
It contains a static `INSTANCE` initialized by `UserState.Factory.create(Configuration.global())`, a private constructor, and `global()`.

## Control Flow, State, and Persistence
The singleton is initialized at class load time and returned by `global()`. It has no persistence, reload, or synchronization logic beyond class initialization.

## Dependencies and Integration Points
It depends on `Configuration.global()` and `UserState`. Server components use it when they need a shared authentication user state.

## Risks and Test Signals
Risks include stale configuration if global auth settings change after class load, hidden initialization failures, and shared mutable state inside `UserState`. Signals are correct subject creation under server auth configurations and stable reuse across callers.
