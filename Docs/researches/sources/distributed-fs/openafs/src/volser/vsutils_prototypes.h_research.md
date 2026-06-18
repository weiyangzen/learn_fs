# sources/distributed-fs/openafs/src/volser/vsutils_prototypes.h

## Purpose

`vsutils_prototypes.h` is the small public header for `vsutils.c`. It declares the VLDB compatibility wrappers and volume-name/id helper APIs consumed by volser client code.

## Important APIs

The header exports prototypes for `VLDB_CreateEntry`, `VLDB_GetEntryByID`, `VLDB_GetEntryByName`, `VLDB_ReplaceEntry`, `VLDB_ListAttributes`, `VLDB_ListAttributesN2`, `VLDB_IsSameAddrs`, `vsu_ExtractName`, and `vsu_GetVolumeID`. The signatures expose VLDB types such as `nvldbentry`, `VldbListByAttributes`, and `nbulkentries`, so includers must already have the generated VLDB type definitions in scope.

## Control Flow and State

There is no executable control flow or local state. The include guard `_VSUTILS_PROTOTYPES_H` prevents duplicate declarations. All runtime behavior and process-global state live in `vsutils.c`.

## Dependencies and Integration Points

This header is included by `vsutils.c` and `vsprocs.c`; it is part of the volser client module’s internal/public C interface. Because it does not include the VLDB or AFS base headers itself, build order and include context matter.

## Risks and Test Signals

The main risk is declaration drift from `vsutils.c`; compiler warnings with strict prototypes are the strongest signal. API changes should be validated by building volser clients and by checking that all includers have the required type declarations before this header.
