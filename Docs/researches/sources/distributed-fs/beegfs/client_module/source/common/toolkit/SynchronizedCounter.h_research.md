# sources/distributed-fs/beegfs/client_module/source/common/toolkit/SynchronizedCounter.h

## Purpose
Defines a small atomic counter plus completion barrier used to wait until a count reaches zero.

## Important APIs and control flow
`SynchronizedCounter_init` sets the atomic count to zero and initializes a completion. `SynchronizedCounter_waitForCount` subtracts the expected wait count and waits for completion. `SynchronizedCounter_incCount` and `SynchronizedCounter_incCountBy` add work completions; if the atomic result becomes zero, they complete the barrier.

## State, dependencies, integration
State is `atomic_t count` plus a Linux `completion`. It depends on kernel atomic and completion APIs. It is suited for fan-out/fan-in cases where waiters pre-decrement by expected completions and workers increment as they finish.

## Risks and test signals
The completion is one-shot unless reinitialized; reuse across multiple independent waits can be unsafe. Incorrect wait counts can deadlock or complete too early. Tests should simulate exact, under, and over completion counts and validate no missed wakeup when increments race with wait setup.
