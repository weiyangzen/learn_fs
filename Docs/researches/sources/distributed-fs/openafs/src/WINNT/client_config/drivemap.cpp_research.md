# sources/distributed-fs/openafs/src/WINNT/client_config/drivemap.cpp

## Purpose
`drivemap.cpp` is the core Windows drive/submount mapping engine for the configuration UI, command-line mapper, and logon-provider remapping behavior. It translates AFS paths and submounts, persists user and machine mapping preferences, detects live network-drive state, and mounts/unmounts DOS drive letters or AFS shares.

## Important APIs, Types, and Functions
Major exports include `QueryDriveMapList`, `WriteDriveMappings`, `FreeDriveMapList`, `ActivateDriveMap`, `InactivateDriveMap`, `AddSubMount`, `RemoveSubMount`, `AdjustAfsPath`, `GetDriveSubmount`, `SubmountToPath`, `PathToSubmount`, `WriteActiveMap`, `ForceMapActive`, `SetBitLogonOption`, `RWLogonOption`, `DoMapShare`, `DoMapShareChange`, `GlobalMountDrive`, `MountDOSDrive`, and `DisMountDOSDrive`.

## Control Flow
Querying maps initializes all 26 drive entries, reads HKLM submount definitions, reads HKCU drive mappings, scans live network drives through `QueryDosDevice` or WNet APIs, marks active/in-use entries, and rewrites mappings if unexpected AFS drives are discovered. Activating a drive validates that the target is under the AFS mount root, asks AFSD for or creates a submount via `VIOC_MAKESUBMOUNT`, then calls `MountDOSDrive`. Logon remapping unmounts stale AFS connections, maps all submount shares, ensures `all` exists, and remaps active or forced drives after service startup.

## State and Persistence Behavior
Persistent state spans HKLM submounts, HKCU mappings, HKCU active-map flags, HKLM logon-provider options, and HKLM global automapper entries. Live state is Windows network connections or AFSIFS DOS-device definitions. Static globals track service transition state and a one-shot username override.

## Dependencies and Integration Points
The file is called by drive tabs, automapper dialogs, `config.cpp`, `tab_general.cpp`, `afsmap.c`, and service-start/stop flows. It depends on Win32 registry, SCM, WNet, QueryDosDevice/DefineDosDevice, OpenAFS pioctl interfaces, fs-utils mount-root globals, LANA NetBIOS helper code, and optional `AFSIFS` paths.

## Risks and Edge Cases
This module contains several high-risk areas: mixed TCHAR/char length calculations, many fixed `MAX_PATH` buffers with `sprintf`/`strcpy`, complex parsing of OS-version-specific LanmanRedirector device paths, and live/persistent divergence when WNet or registry writes fail. `DoMapShareChange` ignores its `removeUnknown` parameter. `ReadRegistryString` creates missing keys while reading. Some allocation/free paths assume OpenAFS `Allocate`/`Free`, others use `malloc`.

## Test Signals
Important tests include registry fixtures for submounts/mappings/active flags, live-drive detection on NT/Win2K/XP-style device paths, AFSIFS and non-AFSIFS mount/unmount behavior, service-start remapping, global automapper entries, invalid submount names, and pioctl failure paths in `PathToSubmount`.
