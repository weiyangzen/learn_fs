# sources/distributed-fs/openafs/src/volser/lockprocs_prototypes.h

## Purpose
Declares the lock/list helper APIs implemented in `lockprocs.c`.

## Important APIs
Prototypes cover VLDB entry mutation (`Lp_SetRWValue`, `Lp_SetROValue`), matching/query helpers (`Lp_Match`, `Lp_ROMatch`, `Lp_AnyMatch`, `Lp_GetRwIndex`), and queue operations (`Lp_QInit`, `Lp_QAdd`, `Lp_QScan`, `Lp_QEnumerate`, `Lp_QTraverse`).

## Control Flow, State, And Persistence
The header has no control flow. It exposes functions that mutate `nvldbentry` and `qHead`/`aqueue` objects owned by callers. No persistent state is created directly.

## Dependencies And Integration
Callers must include definitions for `struct nvldbentry`, `struct qHead`, and `struct aqueue`. This header provides compile-time linkage between volser utility modules and `lockprocs.c`.

## Risks And Test Signals
Risks are primarily declaration drift from implementation and missing includes that rely on include order. Test signals are strict-prototype builds, warning-free compilation, and caller coverage for each declared helper.
