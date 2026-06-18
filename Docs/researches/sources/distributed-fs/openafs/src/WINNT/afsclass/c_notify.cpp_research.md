# sources/distributed-fs/openafs/src/WINNT/afsclass/c_notify.cpp

## Purpose

`c_notify.cpp` implements the global callback registry and dispatch path for AfsClass notifications.

## Important APIs, Types, and Functions

It defines static `NOTIFYCALLBACK::nNotifyList` and `aNotifyList`, constructor/destructor registration, overloads of `SendNotificationToAll`, and instance `SendNotification`.

## Control Flow

Construction stores the supplied function/user value, finds a free slot, and expands the callback array in chunks of four with `REALLOC`. Destruction nulls any matching slot. `SendNotificationToAll` normalizes overloads into a full parameter set, fills `NOTIFYPARAMS`, then calls each registered callback. `SendNotification` invokes the user function inside a C++ exception guard and returns false if the callback fails or throws.

## State and Persistence Behavior

State is a process-global dynamic array of callback object pointers. There is no persistence and no event queue; notifications are synchronous calls on the sender's thread.

## Dependencies and Integration Points

This module is used throughout cell/server/aggregate/fileset/service/user/group refresh and mutation code. It depends on `NOTIFYEVENT`, `NOTIFYPARAMS`, `LPIDENT`, AfsClass allocation macros, and debug `DebugBreak`.

## Risks and Edge Cases

The global callback list is not visibly synchronized here, so concurrent register/unregister/dispatch can race unless callers hold the AfsClass critical section. `lstrcpy` into fixed `MAX_PATH` buffers can overflow if callers pass longer strings. A callback can unregister itself during dispatch, altering later slots.

## Test Signals

Tests should cover multiple callbacks, callback removal, callback failure returning false, thrown exceptions, string parameter propagation, and dispatch during object refresh notifications.
