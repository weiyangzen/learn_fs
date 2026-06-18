# sources/distributed-fs/openafs/src/volser/volser_internal.h

## Purpose

`volser_internal.h` gathers internal cross-module prototypes for the Volser implementation and related vos utility code. It is not the RPC interface definition; it lets C files in this area call shared helpers without exposing them as stable external API.

## Important APIs and Declarations

Server/internal declarations include `Abort`, `Log`, `InitErrTabs`, `split_volume`, transaction APIs (`FindTrans`, `NewTrans`, `TransList`, `DeleteTrans`, `TRELE`, `GCTrans`), and `VPFullUnlock`. The file also declares many `UV_*` vos-side procedures from `vsprocs.c`, covering create, move, backup, release, dump, restore, add/remove site, list, sync, rename, status, zap, set info, copy, clone, dump cloned volume, get size, and convert RO. It also declares VLDB mapping/enumeration helpers and `verbose` / `noresolve` globals.

## Control Flow Role

The header connects `volmain.c` to transaction GC and partition unlock logic, `volprocs.c` to transaction functions, split-volume code, and common logging, and vos/client code to orchestration APIs. In this researched set, it is the compile-time bridge between daemon startup, RPC procedure implementation, and transaction management.

## State and Persistence Behavior

The header is stateless, but it declares side-effecting functions. `DeleteTrans` can detach volumes and terminate Rx calls, `GCTrans` can purge timed-out temporary volumes, `UV_*` functions can modify VLDB and volume state, and `split_volume` can move vnode data between volumes.

## Dependencies and Integration Points

It forward-declares `struct nvldbentry` and uses Volser/Rx/volume-related types expected from surrounding includes. It integrates the volserver daemon, server RPC implementation, transaction manager, volume splitting, and vos command/client orchestration.

## Risks and Edge Cases

The file mixes server-side and client-side declarations, increasing coupling. Prototype drift can cause compile or runtime bugs, especially for dump/restore callback signatures. Return conventions vary across OpenAFS-specific and Unix error codes, so callers must preserve each implementation's contract.

## Test Signals

Compile coverage across volserver and vos utilities is the primary signal. Runtime coverage should exercise transaction create/delete/GC, volume split, and representative `UV_*` orchestration paths such as create, move, release, dump, restore, and list.
