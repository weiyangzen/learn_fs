# sources/distributed-fs/openafs/src/WINNT/client_config/drivemap.h

## Purpose
`drivemap.h` defines the drive mapping model and public API shared by the GUI tabs, global automapper dialog, command-line mapper, and logon remapping code.

## Important APIs, Types, and Functions
It defines drive-letter constants, `DRIVEMAP`, `SUBMOUNT`, and `DRIVEMAPLIST`. Public functions cover validation, querying/writing/freeing mappings, activating/inactivating drives, adding/removing submounts, path/submount translation, live submount detection, service-logon mapping operations, DOS drive mount/dismount, active-map flags, and logon-option bit manipulation.

## Control Flow
The typical workflow is `QueryDriveMapList`, inspect or edit `DRIVEMAPLIST`, `ActivateDriveMap`/`InactivateDriveMap` live state, then `WriteDriveMappings` or `AddSubMount`/`RemoveSubMount` for persistence. Logon-provider users call `TestAndDoMapShare`, `DoMapShare`, or `DoMapShareChange`.

## State and Persistence Behavior
The structs represent both persisted desired state and detected live state. `DRIVEMAP.fPersistent` controls Windows profile persistence; `fActive` records whether the mapping is currently connected. `SUBMOUNT.fInUse` prevents deletion of submounts currently referenced by live mappings.

## Dependencies and Integration Points
The header is included by `afs_config.h`, `config.h`, `RegistrySupport.cpp`, `dlg_automap.cpp`, `tab_drives.cpp`, `config.cpp`, and `afsmap.c`. It exports global username state and logon-option helpers for network-provider integration when `DRIVEMAP_DEF_H` is not set.

## Risks and Edge Cases
The API exposes mutable arrays and global variables directly, so callers can create inconsistent state. Several prototypes use default arguments, tying the header to C++ even though it is included by at least one `.c` source. Buffer ownership and expected lengths are implicit.

## Test Signals
Compile tests should validate C/C++ inclusion assumptions. API-level tests should check that each public mutator preserves `DRIVEMAPLIST` invariants and that caller-provided buffers receive normalized AFS paths/submounts.
