# sources/distributed-fs/openafs/src/libadmin/vos/vosutils.h

## Purpose

`vosutils.h` declares the internal utility functions used by the VOS admin implementation and related helper code.

## Important APIs, Types, and Functions

The header exposes VLDB wrapper functions (`VLDB_CreateEntry`, `aVLDB_GetEntryByID`, `aVLDB_GetEntryByName`, `VLDB_ReplaceEntry`, `VLDB_ListAttributes`, `VLDB_ListAttributesN2`, `VLDB_IsSameAddrs`), volume lookup/name helpers (`GetVolumeInfo`, `ValidateVolumeName`, `vsu_ExtractName`), and address helpers (`AddressMatch`, `RemoveBadAddresses`).

## Control Flow

There is no executable control flow in the header. Its function declarations describe the internal control surface used by `afs_vosAdmin.c`, `lockprocs.c`, and `vsprocs.c`.

## State and Persistence Behavior

The declared VLDB wrappers can read or mutate remote VLDB state, and some mutate compatibility state on the cell handle. Address/name helpers operate on caller-provided memory.

## Dependencies and Integration Points

It depends on `afs_Admin.h`, VLDB types, XDR/RX types through includers, and internal admin cell-handle definitions. It is internal to the VOS admin source directory rather than an installed public API.

## Risks and Test Signals

Because this header exposes old/new VLDB compatibility helpers, prototype drift would affect multiple VOS admin modules. Build tests should compile all VOS admin objects together, and focused unit tests should verify each declared helper's status-code behavior and ownership rules for allocated XDR arrays.
