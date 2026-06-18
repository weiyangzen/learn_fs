# sources/distributed-fs/ceph-client/net/dsa/stubs.c

## Purpose
This file defines the global DSA stubs pointer used by built-in networking code to call optional DSA functionality when DSA may be modular.

## Important APIs, Types, And Functions
It defines and exports `const struct dsa_stubs *dsa_stubs`.

## Control Flow
There is no control flow in this file. `dsa.c` assigns `dsa_stubs` to its static implementation table during module init and clears it during exit.

## State And Persistence
`dsa_stubs` is global pointer state. It is NULL when DSA is not active and points to DSA implementations while the DSA core module is loaded.

## Dependencies And Integration Points
It includes `<net/dsa_stubs.h>` and is built into `obj-y` when DSA is configured, allowing built-in callers to check the pointer without directly linking against a possibly modular DSA core.

## Risks And Edge Cases
Callers must handle NULL and avoid retaining stale function pointers across module unload. Synchronization expectations are defined by the users of the stub table.

## Test Signals
Build tests for modular DSA and runtime tests for hwtstamp validation through the stubs pointer are the main signals.
