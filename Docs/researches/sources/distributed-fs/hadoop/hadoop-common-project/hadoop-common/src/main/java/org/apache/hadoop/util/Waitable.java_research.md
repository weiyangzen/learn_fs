# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Waitable.java

Purpose: `Waitable<T>` is a tiny condition-backed handoff object that lets one side wait until a non-null value is provided.

Important APIs/types/functions: constructor stores a `Condition`. `await()` waits while `val` is null and returns the value. `provide(T)` sets `val` and calls `signalAll`. `hasVal()` and `getVal()` expose current state.

Control flow: `await` uses a loop around `Condition.await()` to handle spurious wakeups. `provide` performs a single assignment and notification.

State and persistence behavior: stores one in-memory value and the caller-supplied condition. Once provided, the value is not cleared or replaced-protected.

Dependencies and integration points: depends on `java.util.concurrent.locks.Condition`; callers must pair it with the associated lock.

Risks: the class does not acquire or validate the condition's lock. Calling `await` or `provide` without holding the lock required by the `Condition` will throw `IllegalMonitorStateException` or race. `provide(null)` wakes waiters but leaves `hasVal` false and `await` will continue waiting. Fields are not volatile, so lock discipline is required for visibility.

Test signals: tests should cover proper lock usage, spurious wake resilience, interrupt propagation from `await`, `provide(null)` behavior, and visibility of `hasVal/getVal` under lock.
