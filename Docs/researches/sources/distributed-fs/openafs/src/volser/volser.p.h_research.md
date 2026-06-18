# sources/distributed-fs/openafs/src/volser/volser.p.h

## Purpose

`volser.p.h` is the core public/private Volser header for server and utility code. It defines transaction flags, volume type aliases, the `struct volser_trans` transaction object, timing and helper constants, Volser-specific error values, backup/listing structures, restore/release flag bits, utility prototypes, and the server-to-server encryption policy enum.

## Important APIs, Types, and Constants

The central type is `struct volser_trans`, representing an active volume transaction with list linkage, transaction id, timestamps, return code, attached `Volume *`, volume id, partition, remote dump state, reference count, initial attach flags, current volume flags, transaction flags, restore incrementality, debug call/procedure fields, and a pthread mutex in pthread builds.

Flag groups include volume state flags (`VTDeleteOnSalvage`, `VTOutOfService`, `VTDeleted`), attach flags (`ITOffline`, `ITBusy`, `ITReadOnly`, `ITCreate`, `ITCreateVolID`), transaction flag `TTDeleted`, volume type aliases, restore/copy/clone flags, release flags, and volume-info validity flags. Lock macros map to `opr_mutex_*` in pthread builds and no-ops otherwise. `GCWAKEUP`, `MAXHELPERS`, Volser service constants, backup-facing structs, and `enum vol_s2s_crypt` are also defined here.

## Control Flow Role

`IT*` flags passed to transaction creation determine attach mode in `volprocs.c`. `VT*` flags are applied to volume header state and used to reject operations on deleted transactions. `TTDeleted` lets `DeleteTrans` defer freeing until outstanding references are released. `GCWAKEUP` drives background GC timing. `enum vol_s2s_crypt` controls outbound transfer security.

## State and Persistence Behavior

The header has no direct side effects, but it defines the in-memory transaction state used to pin volume objects and the bit values that map to persisted header changes. For example, `VTDeleteOnSalvage` maps to `V_destroyMe`, and `VTOutOfService` maps to `V_inService`. `THOLD` is a raw refcount increment and requires correct locking context.

## Dependencies and Integration Points

It includes OpenAFS volume definitions, ubik declarations, and pthread declarations in pthread builds. It is consumed by `volmain.c`, `volprocs.c`, `voltrans.c`, Volser client utilities, and higher-level `vsprocs.c` code.

## Risks and Edge Cases

Risks include shared-structure coupling, obsolete/dangerous flags such as documented "DO NOT USE" `ITReadOnly`, pthread lock macros becoming no-ops in non-pthread builds, historical name-limit constants, and protocol-sensitive error values.

## Test Signals

Tests should indirectly validate this header through transaction creation modes, flag-setting RPCs, deferred transaction deletion, stale transaction GC, server-to-server crypto option parsing, and restore/release flag behavior.
