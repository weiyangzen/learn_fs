# sources/distributed-fs/openafs/src/WINNT/afsclass/c_svc.cpp

## Purpose

`c_svc.cpp` implements `SERVICE`, the cached representation of a BOS process/service on an AFS server.

## Important APIs, Types, and Functions

Implemented methods include constructor/destructor, `GetIdentifier`, `Invalidate`, `RefreshStatus`, `GetName`, parent open methods, `GetStatus`, and user-param accessors. `RefreshStatus` handles a synthetic `BOS` service and real BOS process status.

## Control Flow

Construction stores the parent server identifier and service name, initializes stale status, and should store the parent cell identifier. `RefreshStatus` opens the parent server and BOS object, synthesizes a running simple service status for the `BOS` pseudo-service, or calls BOS worker tasks to get process info, execution state, notifier, and parameter list. It concatenates parameters with spaces and strips trailing CR/LF from aux status, params, and notifier before updating the cache.

## State and Persistence Behavior

State is an in-memory `SERVICESTATUS` snapshot and stale flag. The object reflects BOS process configuration and runtime state but does not persist changes itself.

## Dependencies and Integration Points

The file depends on `SERVER` for BOS handles, `IDENT`, BOS worker tasks, `NOTIFYCALLBACK`, time conversion for the synthetic BOS status, and `SERVICESTATUS` from the header.

## Risks and Edge Cases

The constructor contains `m_lpiCell = m_lpiCell;`, leaving the cell identifier uninitialized instead of copying from the parent server. `OpenCell` can therefore dereference invalid state. Parameter concatenation uses fixed `cchRESOURCE` buffers and `lstrcat`, so many/long parameters can overflow. `RefreshStatus` returns `TRUE` even when `rc` is false.

## Test Signals

Tests should cover synthetic BOS status, stopped/missing process state fallback, notifier and parameter enumeration, CR/LF stripping, long parameter lists, failure status propagation, and `OpenCell` on a service.
