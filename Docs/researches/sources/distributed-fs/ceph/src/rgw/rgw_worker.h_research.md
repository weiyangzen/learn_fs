# sources/distributed-fs/ceph/src/rgw/rgw_worker.h

## Purpose
`rgw_worker.h` declares a base class for periodic RGW RADOS background threads.

## Important APIs, Types, and Functions
`RGWRadosThread` owns nested `Worker`, a `Thread` and `DoutPrefixProvider` that waits on a condition variable and calls the parent processor. The parent exposes virtual `interval_msec()`, `process()`, optional `init()` and `stop_process()`, lifecycle methods `start()`/`stop()`, `signal()`, and down-flag controls.

## Control Flow
Derived classes implement `process()` and interval selection. The worker thread sleeps or waits, wakes on signal or interval, and stops when `down_flag` is set.

## State and Persistence Behavior
The base stores process-local thread state: worker pointer, Ceph context, RADOS store, atomic down flag, and thread name. Persistence is the responsibility of derived `process()` implementations.

## Dependencies and Integration Points
Depends on Ceph `Thread`, mutex/condition variable wrappers, RGWRados forward declaration, and DoutPrefixProvider. Used by RGW services that need periodic RADOS-side maintenance.

## Risks
Implementation is out of line elsewhere, so derived classes rely on undocumented exact entry-loop semantics. `worker` is a raw pointer, making start/stop ownership important. `stop()` is called from the destructor and must be safe for partially initialized instances.

## Test Signals
Derived-thread tests should cover start/stop idempotence, signal wakeups, interval wakeups, process error handling, down flag visibility, and destructor stop behavior.
