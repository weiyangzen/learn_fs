# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/MasterContext.java

## Purpose
`MasterContext` groups shared dependencies required by master implementations.

## Important APIs, Types, And Functions
Constructors require `JournalSystem`, `PrimarySelector`, and a typed `UfsManager`; an optional `UserState` defaults to `ServerUserState.global`. Accessors expose journal system, primary selector, user state, state lock manager, and UFS manager.

## Control Flow, State, Dependencies, Risks, And Tests
The context is immutable except for the internally mutable `StateLockManager`. It carries no persisted state directly, but points masters to journal and UFS persistence. Dependencies include `JournalSystem`, `PrimarySelector`, `UfsManager`, and user-state classes. Risks include raw-type use in some callers, global user-state fallback complicating tests, and every context creating its own state lock manager. Tests should assert null rejection, default user-state selection, typed UFS manager access, and shared lock manager availability.
