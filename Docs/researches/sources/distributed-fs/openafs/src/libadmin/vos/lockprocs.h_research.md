# sources/distributed-fs/openafs/src/libadmin/vos/lockprocs.h

## Purpose

`lockprocs.h` declares the helper API implemented by `lockprocs.c` for VLDB entry site manipulation and queue handling used by VOS admin internals.

## Important APIs, Types, and Functions

It includes system networking, RX/XDR, VLDB, NFS, fsint, volint, volser, `lockdata.h`, util admin, admin internals, and `vosutils.h`. It declares `Lp_SetRWValue`, `Lp_SetROValue`, `Lp_Match`, `Lp_ROMatch`, `Lp_GetRwIndex`, `Lp_QInit`, `Lp_QAdd`, `Lp_QScan`, and `Lp_QEnumerate`.

## Control Flow

No executable control flow is present. The declarations define the interface used by `vsprocs` and VOS admin support code.

## State and Persistence Behavior

The declared functions operate on caller-owned `nvldbentry`, `qHead`, and `aqueue` objects. They only persist changes if higher-level code writes modified VLDB entries or consumes queues into persistent operations.

## Dependencies and Integration Points

This header creates a broad dependency surface on volserver/VLDB internals. It is not a public installed header like `afs_vosAdmin.h`; it is internal to the VOS admin build.

## Risks and Test Signals

The header exposes internal OpenAFS structs directly, so changes in `lockdata.h`, VLDB entry layout, or volserver constants can break users. Compile tests for `lockprocs.c`, `vsprocs.c`, and `afs_vosAdmin.c` are the primary signal. Unit tests should confirm declarations match definitions exactly.
