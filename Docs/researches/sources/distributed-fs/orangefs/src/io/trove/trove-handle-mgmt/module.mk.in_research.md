# sources/distributed-fs/orangefs/src/io/trove/trove-handle-mgmt/module.mk.in

## Purpose
Build-system fragment that adds OrangeFS TROVE handle-management sources to the server build.

## Important APIs, Types, And Functions
Sets `DIR := src/io/trove/trove-handle-mgmt` and appends `avltree.c`, `trove-extentlist.c`, `trove-ledger.c`, and `trove-handle-mgmt.c` to `SERVERSRC`.

## Control Flow
The broader make system includes this fragment so handle ledger, extent list, and AVL support are compiled into the server.

## State And Persistence
No runtime state. It controls compilation of handle-management code that manages persistent/free handle ranges elsewhere.

## Dependencies And Integration Points
Integrates the handle-management directory with the server build and with DBPF code that includes `trove-ledger.h`.

## Risks And Test Signals
Risks include omitted source files after handle-management changes and ordering/include assumptions in the aggregate build. Test signals are successful server builds and link coverage for handle-management symbols.
