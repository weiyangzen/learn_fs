# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/MasterFactory.java

## Purpose
`MasterFactory` is the service-provider contract for discovering and constructing master services.

## Important APIs, Types, And Functions
Implementations expose `isEnabled`, `getName`, and `create(MasterRegistry, T context)`. The generic type binds factories to their required `MasterContext` subtype.

## Control Flow, State, Dependencies, Risks, And Tests
Factories are loaded by `ServiceLoader` through `ServiceUtils`, then used to create masters and journal placeholders. There is no direct persistence. Dependencies are the master registry and context classes. Risks include service-loader metadata omissions, raw generic usage in `ServiceUtils`, and `getName` stability because journal/checkpoint naming depends on it. Tests should cover service loading, disabled factories being skipped, stable names, and create-time dependency registration.
