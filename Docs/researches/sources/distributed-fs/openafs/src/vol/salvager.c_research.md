# sources/distributed-fs/openafs/src/vol/salvager.c

## Purpose
Implements the standalone OpenAFS salvager executable. It parses salvage options, initializes logging and the volume package, coordinates with DAFS/non-DAFS fileservers, obtains salvage locks, and invokes the core salvage routines for all partitions, one partition, or one volume.

## Important APIs, Types, And Functions
Key functions are `TimeStampLogFile`, `handleit`, and `main`. It sets global salvage behavior flags such as `debug`, `Testing`, `ListInodeOption`, `ForceSalvage`, `OKToZap`, `ShowRootFiles`, `RebuildDirs`, `forceR`, `Parallel`, `PartsPerDisk`, `tmpdir`, `ShowLog`, `ShowSuid`, `ShowMounts`, and `orphans`. It invokes `VInitVolumePackage2`, salvage locks, `DInit`, `SalvageFileSysParallel`, and `SalvageFileSys`.

## Control Flow
`main` initializes server paths, enforces root on Unix, marks that a salvage lock is needed, registers legacy command options, and dispatches. `handleit` validates `-partition`/`-volumeid`, configures logging to syslog, a timestamped file, or the standard salvage log, initializes the volume package as either full `salvager` or `volumeSalvager`, obtains the appropriate exclusive/shared salvage lock, checks DAFS compatibility and `-forceDAFS`, initializes the directory package, then runs parallel partition salvage or targeted volume salvage.

## State And Persistence
Persistent effects are repairs to volume headers, vnode indexes, directories, and NAMEI/inode metadata through `vol-salvage.c`, plus salvage logs. Runtime state is mostly global option flags consumed by the core salvage engine. `-nowrite`, `-showsuid`, and `-showmounts` force readonly/testing-style behavior.

## Dependencies And Integration Points
The program ties command parsing, logging, partition discovery, volume package setup, FSSYNC/SALVSYNC coordination, and the core salvage engine together. It includes platform-specific inode/mount headers and has NT child-salvager setup paths.

## Risks And Test Signals
Risks include unsafe standalone use against a DAFS fileserver without explicit override, option-offset fragility in legacy `cmd_AddParm` ordering, invalid volume id parsing, lock acquisition mistakes, and divergent behavior between full-partition and single-volume salvage. Tests should cover option parsing, readonly/list-inodes modes, DAFS refusal/force behavior, all-partition parallel salvage, single-volume salvage while fileserver is running, and timestamp/syslog logging.
