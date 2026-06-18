# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/SafeModeManager.java

## Purpose
`SafeModeManager` defines the minimal contract for master safe-mode state.

## Important APIs, Types, And Functions
It declares notifications for primary master start and RPC server start, plus `isInSafeMode`.

## Control Flow, State, Dependencies, Risks, And Tests
Implementations typically transition out of safe mode only after leadership and RPC readiness conditions are satisfied. This interface has no direct persistence or dependencies beyond the master package. Risks are semantic ambiguity if implementations interpret the notifications differently, especially during failover or restart. Tests should target concrete implementations for transition order, repeated notifications, and RPC rejection while `isInSafeMode` is true.
