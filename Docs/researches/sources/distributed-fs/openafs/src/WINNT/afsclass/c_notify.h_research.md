# sources/distributed-fs/openafs/src/WINNT/afsclass/c_notify.h

## Purpose

`c_notify.h` defines the AfsClass notification event taxonomy, event parameter structure, callback signature, and callback registration class.

## Important APIs, Types, and Functions

`NOTIFYEVENT` enumerates lifecycle, invalidate, refresh, cell-open, VLDB sync, server file/key/list operations, service operations, fileset operations, command/salvage operations, and user/group operations. `NOTIFYPARAMS` carries up to two identifiers, two strings, a progress/extra DWORD, status, and callback user value. `NOTIFYCALLBACKPROC` is the callback signature. `NOTIFYCALLBACK` registers/unregisters and dispatches through static `SendNotificationToAll` overloads.

## Control Flow

The header documents which fields are meaningful for many event types. Implementations call the overload that matches their context; the `.cpp` funnels these into a full parameter record.

## State and Persistence Behavior

The header declares the global callback list as static class data. Notifications are transient and synchronous.

## Dependencies and Integration Points

Every AfsClass object and operation implementation uses these events to report creation, destruction, refresh progress, and administrative operations to UI or monitoring clients.

## Risks and Edge Cases

Adding events must preserve numeric compatibility because `evtUser = 500` reserves a user range. Misusing parameter fields can break clients that rely on the documented per-event conventions.

## Test Signals

Compile tests should verify enum and struct ABI. Integration tests should assert expected begin/end/create/destroy sequences for server, service, fileset, and account workflows.
