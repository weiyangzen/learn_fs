# subset-b-007786 Research

Grouped research for the requested OpenAFS libadmin VOS, libafs build, Darwin KEXT plist, libafsauthent, and libafscp files. Each section preserves the original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/vos/vsprocs.c -->
# sources/distributed-fs/openafs/src/libadmin/vos/vsprocs.c

## Purpose
Implements the libadmin/VOS administrative volume procedures for OpenAFS. This is a thread-safer reimplementation of classic `volser/vsprocs.c`, exposing create, delete, move, backup, release, dump, restore, replication-site, sync, rename, zap, set-flags, partition-list, volume-list, and volserver-status operations through functions that accept an admin cell handle, Rx volserver connections, and an `afs_status_p` out-parameter instead of printing command-line diagnostics as the primary contract.

## Important APIs, Types, And Functions
The exported API surface includes `UV_NukeVolume`, `UV_CreateVolume`, `UV_DeleteVolume`, `UV_MoveVolume`, `UV_BackupVolume`, `UV_ReleaseVolume`, `UV_DumpVolume`, `UV_RestoreVolume`, `UV_AddSite`, `UV_RemoveSite`, `UV_ListPartitions`, `UV_XListVolumes`, `UV_XListOneVolume`, `UV_ListOneVolume`, `UV_SyncVldb`, `CheckVldb`, `UV_SyncServer`, `UV_VolserStatus`, `UV_VolumeZap`, `UV_SetVolume`, and `UV_RenameVolume`. Important private helpers are `UV_Bind`, `CheckAndDeleteVolume`, `ListOneVolume`, `DelVol`, `GetTrans`, `SimulateForwardMultiple`, `VolumeExists`, `ReceiveFile`, `DumpFunction`, `SendFile`, `WriteData`, `ProcessEntries`, `CheckVldbRWBK`, `CheckVldbRO`, and `GroupEntries`. It manipulates `nvldbentry`, `volintInfo`, `volintXInfo`, `volser_status`, `restoreCookie`, `destServer`, `manyDests`, `manyResults`, `partList`, `qHead`, and queue entries from `lockprocs`.

## Control Flow
Most operations follow a common pattern: read or lock a VLDB entry, open volserver transactions with `AFSVolTransCreate`, perform one or more volserver RPCs, close transactions with `AFSVolEndTrans`, update or delete VLDB entries through `VLDB_CreateEntry`, `VLDB_ReplaceEntry`, or ubik VL calls, and release cached Rx connections. Create allocates three volume ids, creates the RW volume, sets quota/status, and creates RW/RO/BK VLDB ids. Delete removes the physical volume and reconciles the VLDB slot based on whether the target was RW, RO, or backup. Move is an idempotent multi-phase clone/forward operation: lock RW VLDB, clone the source, create the destination, forward full and incremental dumps, update the VLDB, set source forwarding, then delete original, backup, and temporary clone. Backup clones or reclones the RW volume into the backup id, allocating a backup id if needed.

Release locks the RW VLDB entry, determines full versus continuation release, creates or reclones the RO source clone, marks RO sites `DONTUSE` or `NEWREPSITE`, opens transactions on destination replicas, forwards changes with `AFSVolForwardMultiple` or per-site fallback, brings replicas online, and finally clears the temporary clone and release flags. Dump and restore stream Rx dump data to or from local files using block-sized buffers and explicit Rx calls. Sync paths list volserver contents, group RW/RO/BK records by parent id, create or repair VLDB entries, and validate existing VLDB entries against file servers. Rename records the new name in VLDB first, then updates RW, backup, and every RO volume name.

## State And Persistence
Persistent state is split between the VLDB and fileserver volume headers. The code changes VLDB names, server/partition arrays, RW/RO/BK ids, `cloneId`, existence flags, operation locks, and replica flags. It also changes volserver state through transactions, volume flags such as `VTDeleteOnSalvage` and `VTOutOfService`, forwarding pointers, clone ids/types, volume dates, quota/status, and physical volume deletion. Dump/restore persist data in caller-supplied files. Runtime state is mostly transaction ids, cached Rx connections, allocated RPC result arrays, temporary clone ids, and queue structures built during sync.

## Dependencies And Integration Points
This file integrates admin handles from `afs_AdminInternal.h`, VOS wrappers from `vosutils.h`, VLDB lock/location helpers from `lockprocs.h`, ubik VL RPCs, volserver RPCs from `volint`, Rx cached connections, roken utility functions, filesystem I/O, and platform-specific stat/block-size handling. It is the implementation behind libadmin VOS entry points and must match the declarations in `vsprocs.h` and higher-level `afs_vosAdmin` callers.

## Risks And Test Signals
The highest risks are partial failure and recovery around VLDB locks, open volserver transactions, temporary clones, and source/destination deletion in move/release/restore. Several operations are intentionally idempotent, but cleanup paths can mask the original error with transaction or unlock errors, and some paths still print to `STDERR`. Name-length checks, old interface fallbacks, allocated RPC memory ownership, host byte order, volume-id reservation, and replica flag transitions are all sensitive. Useful tests include administrative integration tests for create/delete, interrupted move recovery, backup reclone, full and incremental release, full/incremental restore, dump file write/read failures, add/remove site limits, syncvldb/syncserver repair of stale entries, rename across RW/BK/RO volumes, partition-list old/new RPC fallback, and volserver monitor output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/vos/vsprocs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/vos/vsprocs.h -->
# sources/distributed-fs/openafs/src/libadmin/vos/vsprocs.h

## Purpose
Declares the libadmin VOS volume-operation API implemented in `vsprocs.c`, along with the broad OpenAFS, Rx, ubik, VLDB, volserver, and admin includes required by those signatures. It is the public internal header for code that wants to call the UV-style administrative procedures.

## Important APIs, Types, And Functions
The header exposes prototypes for volume lifecycle (`UV_CreateVolume`, `UV_DeleteVolume`, `UV_NukeVolume`, `UV_VolumeZap`), movement and replication (`UV_MoveVolume`, `UV_BackupVolume`, `UV_ReleaseVolume`, `UV_AddSite`, `UV_RemoveSite`), dump/restore (`UV_DumpVolume`, `UV_RestoreVolume`), listing (`UV_ListPartitions`, `UV_XListVolumes`, `UV_XListOneVolume`, `UV_ListOneVolume`, `UV_VolserStatus`), synchronization (`UV_SyncVldb`, `CheckVldb`, `UV_SyncServer`), metadata changes (`UV_SetVolume`, `UV_RenameVolume`), and the `CLOCKSKEW` constant used for incremental dump safety.

## Control Flow
The header itself has no runtime flow. Its signatures establish the calling convention used by libadmin: functions return boolean-like success, place detailed OpenAFS status in `afs_status_p`, and accept either a cell handle, an existing volserver Rx connection, or server/partition ids depending on whether the function must touch VLDB, volserver, or both.

## State And Persistence
No state is stored in the header. The exposed operations manipulate persistent VLDB entries, volume headers, volume transactions, dump files, and replica state through the implementation.

## Dependencies And Integration Points
Consumers inherit dependencies on `rx`, `ubik`, `vlserver`, `volser`, `vldbint`, `afs_Admin`, `kautils`, `cellconfig`, `afsint`, and platform socket/file headers. Signature drift here breaks callers in the admin library and any VOS administration wrappers.

## Risks And Test Signals
Risk centers on declaration/implementation mismatch and excessive include coupling. Build coverage of `src/libadmin/vos`, plus caller tests that compile against only this header, are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/vos/vsprocs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/Makefile.common.in -->
# sources/distributed-fs/openafs/src/libafs/Makefile.common.in

## Purpose
Defines common kernel-libafs build inputs shared by all platform `MakefileProto.*.in` templates. It centralizes include paths, generic build rules, common object lists for libafs, NFS-translator, non-NFS, and PAG-manager variants, per-object compile rules, crypto support objects, generated RPC/XDR objects, platform-specific object hooks, and cleanup behavior.

## Important APIs, Types, And Functions
The important make variables are `COMMON_INCLUDE`, `AFSAOBJS`, `AFSNFSOBJS`, `AFSNONFSOBJS`, `AFSPAGOBJS`, `AFS_OS_OBJS`, `AFS_OS_NFSOBJS`, `AFS_OS_NONFSOBJS`, and `AFS_OS_PAGOBJS`. Rules define `CRULE_NOOPT` and `CRULE_OPT` usage for many source files from `afs`, `afs/VNOPS`, `rx`, `rxkad`, `rxstat`, `fsint`, `vlserver`, `sys`, `util`, and Heimdal crypto sources. Targets include `system`, `install`, `dest`, `all`, single-directory wrappers, `depsrcs`, and `clean`.

## Control Flow
Platform makefiles include this file after setting compiler flags, object hooks, module names, and directory targets. `all` runs setup and platform component directories. Single-directory targets enter `$(KOBJ)` and delegate to `_libafs` targets. Object rules compile common code from the source or generated object tree, selectively using optimized or non-optimized rules. Platform-specific object rules are intentionally common here so platform makefiles only select which OS objects are active.

## State And Persistence
The file creates build artifacts in platform object directories and installs no persistent runtime state by itself. It removes generated include symlinks and build directories during `clean`. The object lists persist the build contract for which code is linked into each kernel module flavor.

## Dependencies And Integration Points
It is included by every `MakefileProto` in `src/libafs`. It depends on `Makefile.config`, generated RPC sources under `TOP_OBJDIR`, kernel crypto sources, the rx/rxkad trees, OS-specific `afs/$(MKAFS_OSTYPE)` source directories, and `Makefile.version` for component version generation.

## Risks And Test Signals
Risks include missing source/object mappings, duplicated object names across variants, incorrect optimization selection for fragile kernel code, include-path ordering bugs, and platform makefiles relying on variables defined before inclusion. Test signals are successful kernel-module builds for representative platforms, Linux Kbuild generation, NFS/non-NFS/PAG object coverage, clean rebuilds after `make clean`, and generated RPC dependency freshness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/Makefile.common.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/MakefileProto.AIX.in -->
# sources/distributed-fs/openafs/src/libafs/MakefileProto.AIX.in

## Purpose
Platform-specific kernel-libafs makefile prototype for AIX. It builds 32-bit and/or 64-bit `afs.ext` kernel extensions, with optional historical iauth/NFS authenticator objects, AIX import files, binder/linker flags, and per-bit `MODLOAD-*` directories. The file is processed with OpenAFS' angle-bracket system-name conditionals before becoming the concrete build makefile.

## Important APIs, Types, And Functions
Key make interfaces are `AFS_OS_OBJS`, `AFS_OS_NFSOBJS`, `AFS_OS_NONFSOBJS`, compiler/linker flag variables, `KOBJ`, `COMPDIRS`, `INSTDIRS`, `DESTDIRS`, `setup`, `libafs`, `install_libafs`, and `dest_libafs`. Notable platform-specific details include multi-bit loops, AIX export/import files, `osi_assem` source selection, and strip/map installation.

## Control Flow
The generated makefile prepares kernel header symlinks and object directories in `setup`, includes `Makefile.common`, and delegates common object compilation to that shared file. Platform targets then link, archive, install, or skip the selected libafs flavor according to this platform's kernel-module conventions.

## State And Persistence
Persistent output is limited to build/install artifacts such as kernel extension objects, archives, `.ko` files, maps/debug bundles, module metadata, and staged files under `DESTDIR` or `DEST`. Runtime AFS state is not touched; this file only shapes the build tree.

## Dependencies And Integration Points
The template depends on `Makefile.config`, `Makefile.common`, platform kernel headers and toolchains, generated OpenAFS RPC sources, and OS-specific source files under `src/afs/<ostype>`. It is selected by OpenAFS configure/sysname logic and participates in the top-level libafs build.

## Risks And Test Signals
Risks include stale platform flags, missing kernel headers, bitness or architecture mismatches, unsupported NFS-translator assumptions, path/symlink drift, and divergence from `Makefile.common` object names. Useful signals are configure output for this sysname, a clean `make libafs`, install/dest smoke checks, and inspection of module load/link errors on the target OS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/MakefileProto.AIX.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/MakefileProto.DARWIN.in -->
# sources/distributed-fs/openafs/src/libafs/MakefileProto.DARWIN.in

## Purpose
Platform-specific kernel-libafs makefile prototype for Darwin/macOS. It builds the non-NFS AFS kernel extension object for multiple selectable architectures, creates fat objects via `lipo`, installs `afs.kext`, and optionally generates dSYM bundles. The file is processed with OpenAFS' angle-bracket system-name conditionals before becoming the concrete build makefile.

## Important APIs, Types, And Functions
Key make interfaces are `AFS_OS_OBJS`, `AFS_OS_NFSOBJS`, `AFS_OS_NONFSOBJS`, compiler/linker flag variables, `KOBJ`, `COMPDIRS`, `INSTDIRS`, `DESTDIRS`, `setup`, `libafs`, `install_libafs`, and `dest_libafs`. Notable platform-specific details include architecture-specific compile commands, arm64-to-arm64e kernel linking, KEXT `Info.plist`, `dsymutil`, and Darwin kernel header symlinks.

## Control Flow
The generated makefile prepares kernel header symlinks and object directories in `setup`, includes `Makefile.common`, and delegates common object compilation to that shared file. Platform targets then link, archive, install, or skip the selected libafs flavor according to this platform's kernel-module conventions.

## State And Persistence
Persistent output is limited to build/install artifacts such as kernel extension objects, archives, `.ko` files, maps/debug bundles, module metadata, and staged files under `DESTDIR` or `DEST`. Runtime AFS state is not touched; this file only shapes the build tree.

## Dependencies And Integration Points
The template depends on `Makefile.config`, `Makefile.common`, platform kernel headers and toolchains, generated OpenAFS RPC sources, and OS-specific source files under `src/afs/<ostype>`. It is selected by OpenAFS configure/sysname logic and participates in the top-level libafs build.

## Risks And Test Signals
Risks include stale platform flags, missing kernel headers, bitness or architecture mismatches, unsupported NFS-translator assumptions, path/symlink drift, and divergence from `Makefile.common` object names. Useful signals are configure output for this sysname, a clean `make libafs`, install/dest smoke checks, and inspection of module load/link errors on the target OS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/MakefileProto.DARWIN.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/MakefileProto.DFBSD.in -->
# sources/distributed-fs/openafs/src/libafs/MakefileProto.DFBSD.in

## Purpose
Platform-specific kernel-libafs makefile prototype for DragonFly BSD. It contains a mostly disabled/skipping kernel-module template for DragonFly BSD while preserving object lists and install/dest placeholders. The file is processed with OpenAFS' angle-bracket system-name conditionals before becoming the concrete build makefile.

## Important APIs, Types, And Functions
Key make interfaces are `AFS_OS_OBJS`, `AFS_OS_NFSOBJS`, `AFS_OS_NONFSOBJS`, compiler/linker flag variables, `KOBJ`, `COMPDIRS`, `INSTDIRS`, `DESTDIRS`, `setup`, `libafs`, `install_libafs`, and `dest_libafs`. Notable platform-specific details include the `all/setup/install` skip targets, non-NFS-only intent, and placeholder `.ko` rules that currently echo rather than link.

## Control Flow
The generated makefile prepares kernel header symlinks and object directories in `setup`, includes `Makefile.common`, and delegates common object compilation to that shared file. Platform targets then link, archive, install, or skip the selected libafs flavor according to this platform's kernel-module conventions.

## State And Persistence
Persistent output is limited to build/install artifacts such as kernel extension objects, archives, `.ko` files, maps/debug bundles, module metadata, and staged files under `DESTDIR` or `DEST`. Runtime AFS state is not touched; this file only shapes the build tree.

## Dependencies And Integration Points
The template depends on `Makefile.config`, `Makefile.common`, platform kernel headers and toolchains, generated OpenAFS RPC sources, and OS-specific source files under `src/afs/<ostype>`. It is selected by OpenAFS configure/sysname logic and participates in the top-level libafs build.

## Risks And Test Signals
Risks include stale platform flags, missing kernel headers, bitness or architecture mismatches, unsupported NFS-translator assumptions, path/symlink drift, and divergence from `Makefile.common` object names. Useful signals are configure output for this sysname, a clean `make libafs`, install/dest smoke checks, and inspection of module load/link errors on the target OS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/MakefileProto.DFBSD.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/MakefileProto.FBSD.in -->
# sources/distributed-fs/openafs/src/libafs/MakefileProto.FBSD.in

## Purpose
Platform-specific kernel-libafs makefile prototype for FreeBSD. It adapts libafs to the FreeBSD `bsd.kmod.mk` build system, generating a kernel build directory when needed and producing a non-NFS `libafs.ko`. The file is processed with OpenAFS' angle-bracket system-name conditionals before becoming the concrete build makefile.

## Important APIs, Types, And Functions
Key make interfaces are `AFS_OS_OBJS`, `AFS_OS_NFSOBJS`, `AFS_OS_NONFSOBJS`, compiler/linker flag variables, `KOBJ`, `COMPDIRS`, `INSTDIRS`, `DESTDIRS`, `setup`, `libafs`, `install_libafs`, and `dest_libafs`. Notable platform-specific details include `vnode_if.h`, `GEN_KBLD_DIR`, copied Makefile plus appended `bsd.kmod.mk`, `KMODDIR`, debug symbol directories, and `KERNBUILDDIR` selection.

## Control Flow
The generated makefile prepares kernel header symlinks and object directories in `setup`, includes `Makefile.common`, and delegates common object compilation to that shared file. Platform targets then link, archive, install, or skip the selected libafs flavor according to this platform's kernel-module conventions.

## State And Persistence
Persistent output is limited to build/install artifacts such as kernel extension objects, archives, `.ko` files, maps/debug bundles, module metadata, and staged files under `DESTDIR` or `DEST`. Runtime AFS state is not touched; this file only shapes the build tree.

## Dependencies And Integration Points
The template depends on `Makefile.config`, `Makefile.common`, platform kernel headers and toolchains, generated OpenAFS RPC sources, and OS-specific source files under `src/afs/<ostype>`. It is selected by OpenAFS configure/sysname logic and participates in the top-level libafs build.

## Risks And Test Signals
Risks include stale platform flags, missing kernel headers, bitness or architecture mismatches, unsupported NFS-translator assumptions, path/symlink drift, and divergence from `Makefile.common` object names. Useful signals are configure output for this sysname, a clean `make libafs`, install/dest smoke checks, and inspection of module load/link errors on the target OS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/MakefileProto.FBSD.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/MakefileProto.HPUX.in -->
# sources/distributed-fs/openafs/src/libafs/MakefileProto.HPUX.in

## Purpose
Platform-specific kernel-libafs makefile prototype for HP-UX. It builds static archives or DDK-linked modules for HP-UX PA-RISC/IPF variants across supported bitnesses, with separate NFS and non-NFS metadata objects on 11.23. The file is processed with OpenAFS' angle-bracket system-name conditionals before becoming the concrete build makefile.

## Important APIs, Types, And Functions
Key make interfaces are `AFS_OS_OBJS`, `AFS_OS_NFSOBJS`, `AFS_OS_NONFSOBJS`, compiler/linker flag variables, `KOBJ`, `COMPDIRS`, `INSTDIRS`, `DESTDIRS`, `setup`, `libafs`, `install_libafs`, and `dest_libafs`. Notable platform-specific details include HP compiler kernel flags, `MODLINK`/`MODMETA`, per-bit `STATIC.*` directories, DDK sample flags, and HP include symlink setup.

## Control Flow
The generated makefile prepares kernel header symlinks and object directories in `setup`, includes `Makefile.common`, and delegates common object compilation to that shared file. Platform targets then link, archive, install, or skip the selected libafs flavor according to this platform's kernel-module conventions.

## State And Persistence
Persistent output is limited to build/install artifacts such as kernel extension objects, archives, `.ko` files, maps/debug bundles, module metadata, and staged files under `DESTDIR` or `DEST`. Runtime AFS state is not touched; this file only shapes the build tree.

## Dependencies And Integration Points
The template depends on `Makefile.config`, `Makefile.common`, platform kernel headers and toolchains, generated OpenAFS RPC sources, and OS-specific source files under `src/afs/<ostype>`. It is selected by OpenAFS configure/sysname logic and participates in the top-level libafs build.

## Risks And Test Signals
Risks include stale platform flags, missing kernel headers, bitness or architecture mismatches, unsupported NFS-translator assumptions, path/symlink drift, and divergence from `Makefile.common` object names. Useful signals are configure output for this sysname, a clean `make libafs`, install/dest smoke checks, and inspection of module load/link errors on the target OS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/MakefileProto.HPUX.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/MakefileProto.IRIX.in -->
# sources/distributed-fs/openafs/src/libafs/MakefileProto.IRIX.in

## Purpose
Platform-specific kernel-libafs makefile prototype for IRIX. It builds IRIX static and modload non-NFS libafs variants for many SGI IP board families using board-specific compiler/linker flags. The file is processed with OpenAFS' angle-bracket system-name conditionals before becoming the concrete build makefile.

## Important APIs, Types, And Functions
Key make interfaces are `AFS_OS_OBJS`, `AFS_OS_NFSOBJS`, `AFS_OS_NONFSOBJS`, compiler/linker flag variables, `KOBJ`, `COMPDIRS`, `INSTDIRS`, `DESTDIRS`, `setup`, `libafs`, `install_libafs`, and `dest_libafs`. Notable platform-specific details include IP19/IP20/IP21/IP22/IP25/IP26/IP27/IP28/IP30/IP32/IP35 flag selection, `STATIC.*` and `MODLOAD.*` directories, SGI install copy/link files, and archive/relocatable outputs.

## Control Flow
The generated makefile prepares kernel header symlinks and object directories in `setup`, includes `Makefile.common`, and delegates common object compilation to that shared file. Platform targets then link, archive, install, or skip the selected libafs flavor according to this platform's kernel-module conventions.

## State And Persistence
Persistent output is limited to build/install artifacts such as kernel extension objects, archives, `.ko` files, maps/debug bundles, module metadata, and staged files under `DESTDIR` or `DEST`. Runtime AFS state is not touched; this file only shapes the build tree.

## Dependencies And Integration Points
The template depends on `Makefile.config`, `Makefile.common`, platform kernel headers and toolchains, generated OpenAFS RPC sources, and OS-specific source files under `src/afs/<ostype>`. It is selected by OpenAFS configure/sysname logic and participates in the top-level libafs build.

## Risks And Test Signals
Risks include stale platform flags, missing kernel headers, bitness or architecture mismatches, unsupported NFS-translator assumptions, path/symlink drift, and divergence from `Makefile.common` object names. Useful signals are configure output for this sysname, a clean `make libafs`, install/dest smoke checks, and inspection of module load/link errors on the target OS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/MakefileProto.IRIX.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/MakefileProto.LINUX.in -->
# sources/distributed-fs/openafs/src/libafs/MakefileProto.LINUX.in

## Purpose
Platform-specific kernel-libafs makefile prototype for Linux. It builds Linux libafs and afspag kernel modules, using legacy direct `ld -r` rules for old kernels and Kbuild-generated Makefiles for Linux 2.6+ kernels. The file is processed with OpenAFS' angle-bracket system-name conditionals before becoming the concrete build makefile.

## Important APIs, Types, And Functions
Key make interfaces are `AFS_OS_OBJS`, `AFS_OS_NFSOBJS`, `AFS_OS_NONFSOBJS`, compiler/linker flag variables, `KOBJ`, `COMPDIRS`, `INSTDIRS`, `DESTDIRS`, `setup`, `libafs`, `install_libafs`, and `dest_libafs`. Notable platform-specific details include kernel header symlink setup, architecture-specific `asm` links, `make_kbuild_makefile.pl`, `.makelog` warning/failure scanning, packaging-friendly install paths, and `SPARSE_MAKEFLAGS`.

## Control Flow
The generated makefile prepares kernel header symlinks and object directories in `setup`, includes `Makefile.common`, and delegates common object compilation to that shared file. Platform targets then link, archive, install, or skip the selected libafs flavor according to this platform's kernel-module conventions.

## State And Persistence
Persistent output is limited to build/install artifacts such as kernel extension objects, archives, `.ko` files, maps/debug bundles, module metadata, and staged files under `DESTDIR` or `DEST`. Runtime AFS state is not touched; this file only shapes the build tree.

## Dependencies And Integration Points
The template depends on `Makefile.config`, `Makefile.common`, platform kernel headers and toolchains, generated OpenAFS RPC sources, and OS-specific source files under `src/afs/<ostype>`. It is selected by OpenAFS configure/sysname logic and participates in the top-level libafs build.

## Risks And Test Signals
Risks include stale platform flags, missing kernel headers, bitness or architecture mismatches, unsupported NFS-translator assumptions, path/symlink drift, and divergence from `Makefile.common` object names. Useful signals are configure output for this sysname, a clean `make libafs`, install/dest smoke checks, and inspection of module load/link errors on the target OS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/MakefileProto.LINUX.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/MakefileProto.NBSD.in -->
# sources/distributed-fs/openafs/src/libafs/MakefileProto.NBSD.in

## Purpose
Platform-specific kernel-libafs makefile prototype for NetBSD. It defines NetBSD LKM build settings and a non-NFS `libafs.nonfs.o` path for selected i386 NetBSD versions while warning or skipping unsupported systems. The file is processed with OpenAFS' angle-bracket system-name conditionals before becoming the concrete build makefile.

## Important APIs, Types, And Functions
Key make interfaces are `AFS_OS_OBJS`, `AFS_OS_NFSOBJS`, `AFS_OS_NONFSOBJS`, compiler/linker flag variables, `KOBJ`, `COMPDIRS`, `INSTDIRS`, `DESTDIRS`, `setup`, `libafs`, `install_libafs`, and `dest_libafs`. Notable platform-specific details include NetBSD kernel source/build include paths, generated `sec_net.h`, symlinks into `net`, `netinet`, `ufs`, `vm`, and selected direct links into `/usr/include` compatibility headers.

## Control Flow
The generated makefile prepares kernel header symlinks and object directories in `setup`, includes `Makefile.common`, and delegates common object compilation to that shared file. Platform targets then link, archive, install, or skip the selected libafs flavor according to this platform's kernel-module conventions.

## State And Persistence
Persistent output is limited to build/install artifacts such as kernel extension objects, archives, `.ko` files, maps/debug bundles, module metadata, and staged files under `DESTDIR` or `DEST`. Runtime AFS state is not touched; this file only shapes the build tree.

## Dependencies And Integration Points
The template depends on `Makefile.config`, `Makefile.common`, platform kernel headers and toolchains, generated OpenAFS RPC sources, and OS-specific source files under `src/afs/<ostype>`. It is selected by OpenAFS configure/sysname logic and participates in the top-level libafs build.

## Risks And Test Signals
Risks include stale platform flags, missing kernel headers, bitness or architecture mismatches, unsupported NFS-translator assumptions, path/symlink drift, and divergence from `Makefile.common` object names. Useful signals are configure output for this sysname, a clean `make libafs`, install/dest smoke checks, and inspection of module load/link errors on the target OS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/MakefileProto.NBSD.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/MakefileProto.OBSD.in -->
# sources/distributed-fs/openafs/src/libafs/MakefileProto.OBSD.in

## Purpose
Platform-specific kernel-libafs makefile prototype for OpenBSD. It builds the OpenBSD non-NFS `libafs.o` LKM object with OpenBSD-specific kernel flags and include symlink setup. The file is processed with OpenAFS' angle-bracket system-name conditionals before becoming the concrete build makefile.

## Important APIs, Types, And Functions
Key make interfaces are `AFS_OS_OBJS`, `AFS_OS_NFSOBJS`, `AFS_OS_NONFSOBJS`, compiler/linker flag variables, `KOBJ`, `COMPDIRS`, `INSTDIRS`, `DESTDIRS`, `setup`, `libafs`, `install_libafs`, and `dest_libafs`. Notable platform-specific details include Jim Rees OpenBSD template, `KFLAGS`, LKM diagnostics defines, `sec_net.h`, `TOP_SRCDIR` override, and simple `ld -r` linking.

## Control Flow
The generated makefile prepares kernel header symlinks and object directories in `setup`, includes `Makefile.common`, and delegates common object compilation to that shared file. Platform targets then link, archive, install, or skip the selected libafs flavor according to this platform's kernel-module conventions.

## State And Persistence
Persistent output is limited to build/install artifacts such as kernel extension objects, archives, `.ko` files, maps/debug bundles, module metadata, and staged files under `DESTDIR` or `DEST`. Runtime AFS state is not touched; this file only shapes the build tree.

## Dependencies And Integration Points
The template depends on `Makefile.config`, `Makefile.common`, platform kernel headers and toolchains, generated OpenAFS RPC sources, and OS-specific source files under `src/afs/<ostype>`. It is selected by OpenAFS configure/sysname logic and participates in the top-level libafs build.

## Risks And Test Signals
Risks include stale platform flags, missing kernel headers, bitness or architecture mismatches, unsupported NFS-translator assumptions, path/symlink drift, and divergence from `Makefile.common` object names. Useful signals are configure output for this sysname, a clean `make libafs`, install/dest smoke checks, and inspection of module load/link errors on the target OS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/MakefileProto.OBSD.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/MakefileProto.SOLARIS.in -->
# sources/distributed-fs/openafs/src/libafs/MakefileProto.SOLARIS.in

## Purpose
Platform-specific kernel-libafs makefile prototype for Solaris. It builds Solaris 32-bit and/or 64-bit NFS and non-NFS libafs relocatable module objects with platform-specific compiler and linker flags. The file is processed with OpenAFS' angle-bracket system-name conditionals before becoming the concrete build makefile.

## Important APIs, Types, And Functions
Key make interfaces are `AFS_OS_OBJS`, `AFS_OS_NFSOBJS`, `AFS_OS_NONFSOBJS`, compiler/linker flag variables, `KOBJ`, `COMPDIRS`, `INSTDIRS`, `DESTDIRS`, `setup`, `libafs`, `install_libafs`, and `dest_libafs`. Notable platform-specific details include Sun Studio kernel flags, `MODLOAD32`/`MODLOAD64`, x86/SPARC architecture options, Solaris module dependency `-N` linker flags, and `LD_WRAPPER` debug flag propagation.

## Control Flow
The generated makefile prepares kernel header symlinks and object directories in `setup`, includes `Makefile.common`, and delegates common object compilation to that shared file. Platform targets then link, archive, install, or skip the selected libafs flavor according to this platform's kernel-module conventions.

## State And Persistence
Persistent output is limited to build/install artifacts such as kernel extension objects, archives, `.ko` files, maps/debug bundles, module metadata, and staged files under `DESTDIR` or `DEST`. Runtime AFS state is not touched; this file only shapes the build tree.

## Dependencies And Integration Points
The template depends on `Makefile.config`, `Makefile.common`, platform kernel headers and toolchains, generated OpenAFS RPC sources, and OS-specific source files under `src/afs/<ostype>`. It is selected by OpenAFS configure/sysname logic and participates in the top-level libafs build.

## Risks And Test Signals
Risks include stale platform flags, missing kernel headers, bitness or architecture mismatches, unsupported NFS-translator assumptions, path/symlink drift, and divergence from `Makefile.common` object names. Useful signals are configure output for this sysname, a clean `make libafs`, install/dest smoke checks, and inspection of module load/link errors on the target OS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/MakefileProto.SOLARIS.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.arm_darwin_100.plist.in -->
# sources/distributed-fs/openafs/src/libafs/afs.arm_darwin_100.plist.in

## Purpose
Darwin kernel-extension property-list template for the OpenAFS `afs` KEXT on the `arm` architecture family and Darwin `100` sysname. It supplies the bundle metadata copied by the Darwin libafs install/dest rules.

## Important APIs, Types, And Functions
The plist defines `CFBundleExecutable` `afs`, `CFBundleIdentifier` `org.openafs.filesystems.afs`, `CFBundleName` `afs`, `CFBundlePackageType` `KEXT`, version placeholders `@MACOS_VERSION@`, and `OSBundleLibraries` dependencies. This variant declares `com.apple.kpi.bsd`, `com.apple.kpi.mach`, and `com.apple.kpi.libkern` at `8.0.x`, with `CFBundleInfoDictionaryVersion` `8.0`.

## Control Flow
There is no executable flow. Configure/substitution fills `@MACOS_VERSION@`, Darwin make rules install the file as `Contents/Info.plist` inside `afs.kext`, and macOS KEXT loading uses the bundle keys and kernel-library dependency versions.

## State And Persistence
The file persists bundle identity and load requirements in the installed KEXT. It does not store runtime cache state or credentials.

## Dependencies And Integration Points
It integrates with `MakefileProto.DARWIN.in`, the generated Darwin `Info.plist`, Apple's KEXT loader, and the built `Contents/MacOS/afs` kernel binary. The architecture and Darwin version in the filename are the selection mechanism.

## Risks And Test Signals
Risks are stale kernel dependency versions, wrong architecture/sysname selection, malformed XML/plist syntax, and placeholder substitution failures. Test signals include `plutil` validation, correct `Info.plist` placement in `afs.kext`, successful code signing or local development loading where applicable, and KEXT load diagnostics that accept the declared KPI/kernel dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.arm_darwin_100.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.arm_darwin_200.plist.in -->
# sources/distributed-fs/openafs/src/libafs/afs.arm_darwin_200.plist.in

## Purpose
Darwin kernel-extension property-list template for the OpenAFS `afs` KEXT on the `arm` architecture family and Darwin `200` sysname. It supplies the bundle metadata copied by the Darwin libafs install/dest rules.

## Important APIs, Types, And Functions
The plist defines `CFBundleExecutable` `afs`, `CFBundleIdentifier` `org.openafs.filesystems.afs`, `CFBundleName` `afs`, `CFBundlePackageType` `KEXT`, version placeholders `@MACOS_VERSION@`, and `OSBundleLibraries` dependencies. This variant declares `com.apple.kpi.bsd`, `com.apple.kpi.mach`, and `com.apple.kpi.libkern` at `8.0.x`, with `CFBundleInfoDictionaryVersion` `8.0`.

## Control Flow
There is no executable flow. Configure/substitution fills `@MACOS_VERSION@`, Darwin make rules install the file as `Contents/Info.plist` inside `afs.kext`, and macOS KEXT loading uses the bundle keys and kernel-library dependency versions.

## State And Persistence
The file persists bundle identity and load requirements in the installed KEXT. It does not store runtime cache state or credentials.

## Dependencies And Integration Points
It integrates with `MakefileProto.DARWIN.in`, the generated Darwin `Info.plist`, Apple's KEXT loader, and the built `Contents/MacOS/afs` kernel binary. The architecture and Darwin version in the filename are the selection mechanism.

## Risks And Test Signals
Risks are stale kernel dependency versions, wrong architecture/sysname selection, malformed XML/plist syntax, and placeholder substitution failures. Test signals include `plutil` validation, correct `Info.plist` placement in `afs.kext`, successful code signing or local development loading where applicable, and KEXT load diagnostics that accept the declared KPI/kernel dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.arm_darwin_200.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.arm_darwin_210.plist.in -->
# sources/distributed-fs/openafs/src/libafs/afs.arm_darwin_210.plist.in

## Purpose
Darwin kernel-extension property-list template for the OpenAFS `afs` KEXT on the `arm` architecture family and Darwin `210` sysname. It supplies the bundle metadata copied by the Darwin libafs install/dest rules.

## Important APIs, Types, And Functions
The plist defines `CFBundleExecutable` `afs`, `CFBundleIdentifier` `org.openafs.filesystems.afs`, `CFBundleName` `afs`, `CFBundlePackageType` `KEXT`, version placeholders `@MACOS_VERSION@`, and `OSBundleLibraries` dependencies. This variant declares `com.apple.kpi.bsd`, `com.apple.kpi.mach`, and `com.apple.kpi.libkern` at `8.0.x`, with `CFBundleInfoDictionaryVersion` `8.0`.

## Control Flow
There is no executable flow. Configure/substitution fills `@MACOS_VERSION@`, Darwin make rules install the file as `Contents/Info.plist` inside `afs.kext`, and macOS KEXT loading uses the bundle keys and kernel-library dependency versions.

## State And Persistence
The file persists bundle identity and load requirements in the installed KEXT. It does not store runtime cache state or credentials.

## Dependencies And Integration Points
It integrates with `MakefileProto.DARWIN.in`, the generated Darwin `Info.plist`, Apple's KEXT loader, and the built `Contents/MacOS/afs` kernel binary. The architecture and Darwin version in the filename are the selection mechanism.

## Risks And Test Signals
Risks are stale kernel dependency versions, wrong architecture/sysname selection, malformed XML/plist syntax, and placeholder substitution failures. Test signals include `plutil` validation, correct `Info.plist` placement in `afs.kext`, successful code signing or local development loading where applicable, and KEXT load diagnostics that accept the declared KPI/kernel dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.arm_darwin_210.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.arm_darwin_220.plist.in -->
# sources/distributed-fs/openafs/src/libafs/afs.arm_darwin_220.plist.in

## Purpose
Darwin kernel-extension property-list template for the OpenAFS `afs` KEXT on the `arm` architecture family and Darwin `220` sysname. It supplies the bundle metadata copied by the Darwin libafs install/dest rules.

## Important APIs, Types, And Functions
The plist defines `CFBundleExecutable` `afs`, `CFBundleIdentifier` `org.openafs.filesystems.afs`, `CFBundleName` `afs`, `CFBundlePackageType` `KEXT`, version placeholders `@MACOS_VERSION@`, and `OSBundleLibraries` dependencies. This variant declares `com.apple.kpi.bsd`, `com.apple.kpi.mach`, and `com.apple.kpi.libkern` at `8.0.x`, with `CFBundleInfoDictionaryVersion` `8.0`.

## Control Flow
There is no executable flow. Configure/substitution fills `@MACOS_VERSION@`, Darwin make rules install the file as `Contents/Info.plist` inside `afs.kext`, and macOS KEXT loading uses the bundle keys and kernel-library dependency versions.

## State And Persistence
The file persists bundle identity and load requirements in the installed KEXT. It does not store runtime cache state or credentials.

## Dependencies And Integration Points
It integrates with `MakefileProto.DARWIN.in`, the generated Darwin `Info.plist`, Apple's KEXT loader, and the built `Contents/MacOS/afs` kernel binary. The architecture and Darwin version in the filename are the selection mechanism.

## Risks And Test Signals
Risks are stale kernel dependency versions, wrong architecture/sysname selection, malformed XML/plist syntax, and placeholder substitution failures. Test signals include `plutil` validation, correct `Info.plist` placement in `afs.kext`, successful code signing or local development loading where applicable, and KEXT load diagnostics that accept the declared KPI/kernel dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.arm_darwin_220.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.arm_darwin_230.plist.in -->
# sources/distributed-fs/openafs/src/libafs/afs.arm_darwin_230.plist.in

## Purpose
Darwin kernel-extension property-list template for the OpenAFS `afs` KEXT on the `arm` architecture family and Darwin `230` sysname. It supplies the bundle metadata copied by the Darwin libafs install/dest rules.

## Important APIs, Types, And Functions
The plist defines `CFBundleExecutable` `afs`, `CFBundleIdentifier` `org.openafs.filesystems.afs`, `CFBundleName` `afs`, `CFBundlePackageType` `KEXT`, version placeholders `@MACOS_VERSION@`, and `OSBundleLibraries` dependencies. This variant declares `com.apple.kpi.bsd`, `com.apple.kpi.mach`, and `com.apple.kpi.libkern` at `8.0.x`, with `CFBundleInfoDictionaryVersion` `8.0`.

## Control Flow
There is no executable flow. Configure/substitution fills `@MACOS_VERSION@`, Darwin make rules install the file as `Contents/Info.plist` inside `afs.kext`, and macOS KEXT loading uses the bundle keys and kernel-library dependency versions.

## State And Persistence
The file persists bundle identity and load requirements in the installed KEXT. It does not store runtime cache state or credentials.

## Dependencies And Integration Points
It integrates with `MakefileProto.DARWIN.in`, the generated Darwin `Info.plist`, Apple's KEXT loader, and the built `Contents/MacOS/afs` kernel binary. The architecture and Darwin version in the filename are the selection mechanism.

## Risks And Test Signals
Risks are stale kernel dependency versions, wrong architecture/sysname selection, malformed XML/plist syntax, and placeholder substitution failures. Test signals include `plutil` validation, correct `Info.plist` placement in `afs.kext`, successful code signing or local development loading where applicable, and KEXT load diagnostics that accept the declared KPI/kernel dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.arm_darwin_230.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.arm_darwin_240.plist.in -->
# sources/distributed-fs/openafs/src/libafs/afs.arm_darwin_240.plist.in

## Purpose
Darwin kernel-extension property-list template for the OpenAFS `afs` KEXT on the `arm` architecture family and Darwin `240` sysname. It supplies the bundle metadata copied by the Darwin libafs install/dest rules.

## Important APIs, Types, And Functions
The plist defines `CFBundleExecutable` `afs`, `CFBundleIdentifier` `org.openafs.filesystems.afs`, `CFBundleName` `afs`, `CFBundlePackageType` `KEXT`, version placeholders `@MACOS_VERSION@`, and `OSBundleLibraries` dependencies. This variant declares `com.apple.kpi.bsd`, `com.apple.kpi.mach`, and `com.apple.kpi.libkern` at `8.0.x`, with `CFBundleInfoDictionaryVersion` `8.0`.

## Control Flow
There is no executable flow. Configure/substitution fills `@MACOS_VERSION@`, Darwin make rules install the file as `Contents/Info.plist` inside `afs.kext`, and macOS KEXT loading uses the bundle keys and kernel-library dependency versions.

## State And Persistence
The file persists bundle identity and load requirements in the installed KEXT. It does not store runtime cache state or credentials.

## Dependencies And Integration Points
It integrates with `MakefileProto.DARWIN.in`, the generated Darwin `Info.plist`, Apple's KEXT loader, and the built `Contents/MacOS/afs` kernel binary. The architecture and Darwin version in the filename are the selection mechanism.

## Risks And Test Signals
Risks are stale kernel dependency versions, wrong architecture/sysname selection, malformed XML/plist syntax, and placeholder substitution failures. Test signals include `plutil` validation, correct `Info.plist` placement in `afs.kext`, successful code signing or local development loading where applicable, and KEXT load diagnostics that accept the declared KPI/kernel dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.arm_darwin_240.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.arm_darwin_250.plist.in -->
# sources/distributed-fs/openafs/src/libafs/afs.arm_darwin_250.plist.in

## Purpose
Darwin kernel-extension property-list template for the OpenAFS `afs` KEXT on the `arm` architecture family and Darwin `250` sysname. It supplies the bundle metadata copied by the Darwin libafs install/dest rules.

## Important APIs, Types, And Functions
The plist defines `CFBundleExecutable` `afs`, `CFBundleIdentifier` `org.openafs.filesystems.afs`, `CFBundleName` `afs`, `CFBundlePackageType` `KEXT`, version placeholders `@MACOS_VERSION@`, and `OSBundleLibraries` dependencies. This variant declares `com.apple.kpi.bsd`, `com.apple.kpi.mach`, and `com.apple.kpi.libkern` at `8.0.x`, with `CFBundleInfoDictionaryVersion` `8.0`.

## Control Flow
There is no executable flow. Configure/substitution fills `@MACOS_VERSION@`, Darwin make rules install the file as `Contents/Info.plist` inside `afs.kext`, and macOS KEXT loading uses the bundle keys and kernel-library dependency versions.

## State And Persistence
The file persists bundle identity and load requirements in the installed KEXT. It does not store runtime cache state or credentials.

## Dependencies And Integration Points
It integrates with `MakefileProto.DARWIN.in`, the generated Darwin `Info.plist`, Apple's KEXT loader, and the built `Contents/MacOS/afs` kernel binary. The architecture and Darwin version in the filename are the selection mechanism.

## Risks And Test Signals
Risks are stale kernel dependency versions, wrong architecture/sysname selection, malformed XML/plist syntax, and placeholder substitution failures. Test signals include `plutil` validation, correct `Info.plist` placement in `afs.kext`, successful code signing or local development loading where applicable, and KEXT load diagnostics that accept the declared KPI/kernel dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.arm_darwin_250.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.ppc_darwin_70.plist.in -->
# sources/distributed-fs/openafs/src/libafs/afs.ppc_darwin_70.plist.in

## Purpose
Darwin kernel-extension property-list template for the OpenAFS `afs` KEXT on the `ppc` architecture family and Darwin `70` sysname. It supplies the bundle metadata copied by the Darwin libafs install/dest rules.

## Important APIs, Types, And Functions
The plist defines `CFBundleExecutable` `afs`, `CFBundleIdentifier` `org.openafs.filesystems.afs`, `CFBundleName` `afs`, `CFBundlePackageType` `KEXT`, version placeholders `@MACOS_VERSION@`, and `OSBundleLibraries` dependencies. This variant declares `com.apple.kernel.bsd` and `com.apple.kernel.mach` at `6.9.9`, with `CFBundleInfoDictionaryVersion` `6.0`.

## Control Flow
There is no executable flow. Configure/substitution fills `@MACOS_VERSION@`, Darwin make rules install the file as `Contents/Info.plist` inside `afs.kext`, and macOS KEXT loading uses the bundle keys and kernel-library dependency versions.

## State And Persistence
The file persists bundle identity and load requirements in the installed KEXT. It does not store runtime cache state or credentials.

## Dependencies And Integration Points
It integrates with `MakefileProto.DARWIN.in`, the generated Darwin `Info.plist`, Apple's KEXT loader, and the built `Contents/MacOS/afs` kernel binary. The architecture and Darwin version in the filename are the selection mechanism.

## Risks And Test Signals
Risks are stale kernel dependency versions, wrong architecture/sysname selection, malformed XML/plist syntax, and placeholder substitution failures. Test signals include `plutil` validation, correct `Info.plist` placement in `afs.kext`, successful code signing or local development loading where applicable, and KEXT load diagnostics that accept the declared KPI/kernel dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.ppc_darwin_70.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.ppc_darwin_80.plist.in -->
# sources/distributed-fs/openafs/src/libafs/afs.ppc_darwin_80.plist.in

## Purpose
Darwin kernel-extension property-list template for the OpenAFS `afs` KEXT on the `ppc` architecture family and Darwin `80` sysname. It supplies the bundle metadata copied by the Darwin libafs install/dest rules.

## Important APIs, Types, And Functions
The plist defines `CFBundleExecutable` `afs`, `CFBundleIdentifier` `org.openafs.filesystems.afs`, `CFBundleName` `afs`, `CFBundlePackageType` `KEXT`, version placeholders `@MACOS_VERSION@`, and `OSBundleLibraries` dependencies. This variant declares `com.apple.kpi.bsd`, `com.apple.kpi.mach`, and `com.apple.kpi.libkern` at `8.0.x`, with `CFBundleInfoDictionaryVersion` `8.0`.

## Control Flow
There is no executable flow. Configure/substitution fills `@MACOS_VERSION@`, Darwin make rules install the file as `Contents/Info.plist` inside `afs.kext`, and macOS KEXT loading uses the bundle keys and kernel-library dependency versions.

## State And Persistence
The file persists bundle identity and load requirements in the installed KEXT. It does not store runtime cache state or credentials.

## Dependencies And Integration Points
It integrates with `MakefileProto.DARWIN.in`, the generated Darwin `Info.plist`, Apple's KEXT loader, and the built `Contents/MacOS/afs` kernel binary. The architecture and Darwin version in the filename are the selection mechanism.

## Risks And Test Signals
Risks are stale kernel dependency versions, wrong architecture/sysname selection, malformed XML/plist syntax, and placeholder substitution failures. Test signals include `plutil` validation, correct `Info.plist` placement in `afs.kext`, successful code signing or local development loading where applicable, and KEXT load diagnostics that accept the declared KPI/kernel dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.ppc_darwin_80.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.ppc_darwin_90.plist.in -->
# sources/distributed-fs/openafs/src/libafs/afs.ppc_darwin_90.plist.in

## Purpose
Darwin kernel-extension property-list template for the OpenAFS `afs` KEXT on the `ppc` architecture family and Darwin `90` sysname. It supplies the bundle metadata copied by the Darwin libafs install/dest rules.

## Important APIs, Types, And Functions
The plist defines `CFBundleExecutable` `afs`, `CFBundleIdentifier` `org.openafs.filesystems.afs`, `CFBundleName` `afs`, `CFBundlePackageType` `KEXT`, version placeholders `@MACOS_VERSION@`, and `OSBundleLibraries` dependencies. This variant declares `com.apple.kpi.bsd`, `com.apple.kpi.mach`, and `com.apple.kpi.libkern` at `8.0.x`, with `CFBundleInfoDictionaryVersion` `8.0`.

## Control Flow
There is no executable flow. Configure/substitution fills `@MACOS_VERSION@`, Darwin make rules install the file as `Contents/Info.plist` inside `afs.kext`, and macOS KEXT loading uses the bundle keys and kernel-library dependency versions.

## State And Persistence
The file persists bundle identity and load requirements in the installed KEXT. It does not store runtime cache state or credentials.

## Dependencies And Integration Points
It integrates with `MakefileProto.DARWIN.in`, the generated Darwin `Info.plist`, Apple's KEXT loader, and the built `Contents/MacOS/afs` kernel binary. The architecture and Darwin version in the filename are the selection mechanism.

## Risks And Test Signals
Risks are stale kernel dependency versions, wrong architecture/sysname selection, malformed XML/plist syntax, and placeholder substitution failures. Test signals include `plutil` validation, correct `Info.plist` placement in `afs.kext`, successful code signing or local development loading where applicable, and KEXT load diagnostics that accept the declared KPI/kernel dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.ppc_darwin_90.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_100.plist.in -->
# sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_100.plist.in

## Purpose
Darwin kernel-extension property-list template for the OpenAFS `afs` KEXT on the `x86` architecture family and Darwin `100` sysname. It supplies the bundle metadata copied by the Darwin libafs install/dest rules.

## Important APIs, Types, And Functions
The plist defines `CFBundleExecutable` `afs`, `CFBundleIdentifier` `org.openafs.filesystems.afs`, `CFBundleName` `afs`, `CFBundlePackageType` `KEXT`, version placeholders `@MACOS_VERSION@`, and `OSBundleLibraries` dependencies. This variant declares `com.apple.kpi.bsd`, `com.apple.kpi.mach`, and `com.apple.kpi.libkern` at `8.0.x`, with `CFBundleInfoDictionaryVersion` `8.0`.

## Control Flow
There is no executable flow. Configure/substitution fills `@MACOS_VERSION@`, Darwin make rules install the file as `Contents/Info.plist` inside `afs.kext`, and macOS KEXT loading uses the bundle keys and kernel-library dependency versions.

## State And Persistence
The file persists bundle identity and load requirements in the installed KEXT. It does not store runtime cache state or credentials.

## Dependencies And Integration Points
It integrates with `MakefileProto.DARWIN.in`, the generated Darwin `Info.plist`, Apple's KEXT loader, and the built `Contents/MacOS/afs` kernel binary. The architecture and Darwin version in the filename are the selection mechanism.

## Risks And Test Signals
Risks are stale kernel dependency versions, wrong architecture/sysname selection, malformed XML/plist syntax, and placeholder substitution failures. Test signals include `plutil` validation, correct `Info.plist` placement in `afs.kext`, successful code signing or local development loading where applicable, and KEXT load diagnostics that accept the declared KPI/kernel dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_100.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_110.plist.in -->
# sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_110.plist.in

## Purpose
Darwin kernel-extension property-list template for the OpenAFS `afs` KEXT on the `x86` architecture family and Darwin `110` sysname. It supplies the bundle metadata copied by the Darwin libafs install/dest rules.

## Important APIs, Types, And Functions
The plist defines `CFBundleExecutable` `afs`, `CFBundleIdentifier` `org.openafs.filesystems.afs`, `CFBundleName` `afs`, `CFBundlePackageType` `KEXT`, version placeholders `@MACOS_VERSION@`, and `OSBundleLibraries` dependencies. This variant declares `com.apple.kpi.bsd`, `com.apple.kpi.mach`, and `com.apple.kpi.libkern` at `8.0.x`, with `CFBundleInfoDictionaryVersion` `8.0`.

## Control Flow
There is no executable flow. Configure/substitution fills `@MACOS_VERSION@`, Darwin make rules install the file as `Contents/Info.plist` inside `afs.kext`, and macOS KEXT loading uses the bundle keys and kernel-library dependency versions.

## State And Persistence
The file persists bundle identity and load requirements in the installed KEXT. It does not store runtime cache state or credentials.

## Dependencies And Integration Points
It integrates with `MakefileProto.DARWIN.in`, the generated Darwin `Info.plist`, Apple's KEXT loader, and the built `Contents/MacOS/afs` kernel binary. The architecture and Darwin version in the filename are the selection mechanism.

## Risks And Test Signals
Risks are stale kernel dependency versions, wrong architecture/sysname selection, malformed XML/plist syntax, and placeholder substitution failures. Test signals include `plutil` validation, correct `Info.plist` placement in `afs.kext`, successful code signing or local development loading where applicable, and KEXT load diagnostics that accept the declared KPI/kernel dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_110.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_120.plist.in -->
# sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_120.plist.in

## Purpose
Darwin kernel-extension property-list template for the OpenAFS `afs` KEXT on the `x86` architecture family and Darwin `120` sysname. It supplies the bundle metadata copied by the Darwin libafs install/dest rules.

## Important APIs, Types, And Functions
The plist defines `CFBundleExecutable` `afs`, `CFBundleIdentifier` `org.openafs.filesystems.afs`, `CFBundleName` `afs`, `CFBundlePackageType` `KEXT`, version placeholders `@MACOS_VERSION@`, and `OSBundleLibraries` dependencies. This variant declares `com.apple.kpi.bsd`, `com.apple.kpi.mach`, and `com.apple.kpi.libkern` at `8.0.x`, with `CFBundleInfoDictionaryVersion` `8.0`.

## Control Flow
There is no executable flow. Configure/substitution fills `@MACOS_VERSION@`, Darwin make rules install the file as `Contents/Info.plist` inside `afs.kext`, and macOS KEXT loading uses the bundle keys and kernel-library dependency versions.

## State And Persistence
The file persists bundle identity and load requirements in the installed KEXT. It does not store runtime cache state or credentials.

## Dependencies And Integration Points
It integrates with `MakefileProto.DARWIN.in`, the generated Darwin `Info.plist`, Apple's KEXT loader, and the built `Contents/MacOS/afs` kernel binary. The architecture and Darwin version in the filename are the selection mechanism.

## Risks And Test Signals
Risks are stale kernel dependency versions, wrong architecture/sysname selection, malformed XML/plist syntax, and placeholder substitution failures. Test signals include `plutil` validation, correct `Info.plist` placement in `afs.kext`, successful code signing or local development loading where applicable, and KEXT load diagnostics that accept the declared KPI/kernel dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_120.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_130.plist.in -->
# sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_130.plist.in

## Purpose
Darwin kernel-extension property-list template for the OpenAFS `afs` KEXT on the `x86` architecture family and Darwin `130` sysname. It supplies the bundle metadata copied by the Darwin libafs install/dest rules.

## Important APIs, Types, And Functions
The plist defines `CFBundleExecutable` `afs`, `CFBundleIdentifier` `org.openafs.filesystems.afs`, `CFBundleName` `afs`, `CFBundlePackageType` `KEXT`, version placeholders `@MACOS_VERSION@`, and `OSBundleLibraries` dependencies. This variant declares `com.apple.kpi.bsd`, `com.apple.kpi.mach`, and `com.apple.kpi.libkern` at `8.0.x`, with `CFBundleInfoDictionaryVersion` `8.0`.

## Control Flow
There is no executable flow. Configure/substitution fills `@MACOS_VERSION@`, Darwin make rules install the file as `Contents/Info.plist` inside `afs.kext`, and macOS KEXT loading uses the bundle keys and kernel-library dependency versions.

## State And Persistence
The file persists bundle identity and load requirements in the installed KEXT. It does not store runtime cache state or credentials.

## Dependencies And Integration Points
It integrates with `MakefileProto.DARWIN.in`, the generated Darwin `Info.plist`, Apple's KEXT loader, and the built `Contents/MacOS/afs` kernel binary. The architecture and Darwin version in the filename are the selection mechanism.

## Risks And Test Signals
Risks are stale kernel dependency versions, wrong architecture/sysname selection, malformed XML/plist syntax, and placeholder substitution failures. Test signals include `plutil` validation, correct `Info.plist` placement in `afs.kext`, successful code signing or local development loading where applicable, and KEXT load diagnostics that accept the declared KPI/kernel dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_130.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_140.plist.in -->
# sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_140.plist.in

## Purpose
Darwin kernel-extension property-list template for the OpenAFS `afs` KEXT on the `x86` architecture family and Darwin `140` sysname. It supplies the bundle metadata copied by the Darwin libafs install/dest rules.

## Important APIs, Types, And Functions
The plist defines `CFBundleExecutable` `afs`, `CFBundleIdentifier` `org.openafs.filesystems.afs`, `CFBundleName` `afs`, `CFBundlePackageType` `KEXT`, version placeholders `@MACOS_VERSION@`, and `OSBundleLibraries` dependencies. This variant declares `com.apple.kpi.bsd`, `com.apple.kpi.mach`, and `com.apple.kpi.libkern` at `8.0.x`, with `CFBundleInfoDictionaryVersion` `8.0`.

## Control Flow
There is no executable flow. Configure/substitution fills `@MACOS_VERSION@`, Darwin make rules install the file as `Contents/Info.plist` inside `afs.kext`, and macOS KEXT loading uses the bundle keys and kernel-library dependency versions.

## State And Persistence
The file persists bundle identity and load requirements in the installed KEXT. It does not store runtime cache state or credentials.

## Dependencies And Integration Points
It integrates with `MakefileProto.DARWIN.in`, the generated Darwin `Info.plist`, Apple's KEXT loader, and the built `Contents/MacOS/afs` kernel binary. The architecture and Darwin version in the filename are the selection mechanism.

## Risks And Test Signals
Risks are stale kernel dependency versions, wrong architecture/sysname selection, malformed XML/plist syntax, and placeholder substitution failures. Test signals include `plutil` validation, correct `Info.plist` placement in `afs.kext`, successful code signing or local development loading where applicable, and KEXT load diagnostics that accept the declared KPI/kernel dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_140.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_150.plist.in -->
# sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_150.plist.in

## Purpose
Darwin kernel-extension property-list template for the OpenAFS `afs` KEXT on the `x86` architecture family and Darwin `150` sysname. It supplies the bundle metadata copied by the Darwin libafs install/dest rules.

## Important APIs, Types, And Functions
The plist defines `CFBundleExecutable` `afs`, `CFBundleIdentifier` `org.openafs.filesystems.afs`, `CFBundleName` `afs`, `CFBundlePackageType` `KEXT`, version placeholders `@MACOS_VERSION@`, and `OSBundleLibraries` dependencies. This variant declares `com.apple.kpi.bsd`, `com.apple.kpi.mach`, and `com.apple.kpi.libkern` at `8.0.x`, with `CFBundleInfoDictionaryVersion` `8.0`.

## Control Flow
There is no executable flow. Configure/substitution fills `@MACOS_VERSION@`, Darwin make rules install the file as `Contents/Info.plist` inside `afs.kext`, and macOS KEXT loading uses the bundle keys and kernel-library dependency versions.

## State And Persistence
The file persists bundle identity and load requirements in the installed KEXT. It does not store runtime cache state or credentials.

## Dependencies And Integration Points
It integrates with `MakefileProto.DARWIN.in`, the generated Darwin `Info.plist`, Apple's KEXT loader, and the built `Contents/MacOS/afs` kernel binary. The architecture and Darwin version in the filename are the selection mechanism.

## Risks And Test Signals
Risks are stale kernel dependency versions, wrong architecture/sysname selection, malformed XML/plist syntax, and placeholder substitution failures. Test signals include `plutil` validation, correct `Info.plist` placement in `afs.kext`, successful code signing or local development loading where applicable, and KEXT load diagnostics that accept the declared KPI/kernel dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_150.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_160.plist.in -->
# sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_160.plist.in

## Purpose
Darwin kernel-extension property-list template for the OpenAFS `afs` KEXT on the `x86` architecture family and Darwin `160` sysname. It supplies the bundle metadata copied by the Darwin libafs install/dest rules.

## Important APIs, Types, And Functions
The plist defines `CFBundleExecutable` `afs`, `CFBundleIdentifier` `org.openafs.filesystems.afs`, `CFBundleName` `afs`, `CFBundlePackageType` `KEXT`, version placeholders `@MACOS_VERSION@`, and `OSBundleLibraries` dependencies. This variant declares `com.apple.kpi.bsd`, `com.apple.kpi.mach`, and `com.apple.kpi.libkern` at `8.0.x`, with `CFBundleInfoDictionaryVersion` `8.0`.

## Control Flow
There is no executable flow. Configure/substitution fills `@MACOS_VERSION@`, Darwin make rules install the file as `Contents/Info.plist` inside `afs.kext`, and macOS KEXT loading uses the bundle keys and kernel-library dependency versions.

## State And Persistence
The file persists bundle identity and load requirements in the installed KEXT. It does not store runtime cache state or credentials.

## Dependencies And Integration Points
It integrates with `MakefileProto.DARWIN.in`, the generated Darwin `Info.plist`, Apple's KEXT loader, and the built `Contents/MacOS/afs` kernel binary. The architecture and Darwin version in the filename are the selection mechanism.

## Risks And Test Signals
Risks are stale kernel dependency versions, wrong architecture/sysname selection, malformed XML/plist syntax, and placeholder substitution failures. Test signals include `plutil` validation, correct `Info.plist` placement in `afs.kext`, successful code signing or local development loading where applicable, and KEXT load diagnostics that accept the declared KPI/kernel dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_160.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_170.plist.in -->
# sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_170.plist.in

## Purpose
Darwin kernel-extension property-list template for the OpenAFS `afs` KEXT on the `x86` architecture family and Darwin `170` sysname. It supplies the bundle metadata copied by the Darwin libafs install/dest rules.

## Important APIs, Types, And Functions
The plist defines `CFBundleExecutable` `afs`, `CFBundleIdentifier` `org.openafs.filesystems.afs`, `CFBundleName` `afs`, `CFBundlePackageType` `KEXT`, version placeholders `@MACOS_VERSION@`, and `OSBundleLibraries` dependencies. This variant declares `com.apple.kpi.bsd`, `com.apple.kpi.mach`, and `com.apple.kpi.libkern` at `8.0.x`, with `CFBundleInfoDictionaryVersion` `8.0`.

## Control Flow
There is no executable flow. Configure/substitution fills `@MACOS_VERSION@`, Darwin make rules install the file as `Contents/Info.plist` inside `afs.kext`, and macOS KEXT loading uses the bundle keys and kernel-library dependency versions.

## State And Persistence
The file persists bundle identity and load requirements in the installed KEXT. It does not store runtime cache state or credentials.

## Dependencies And Integration Points
It integrates with `MakefileProto.DARWIN.in`, the generated Darwin `Info.plist`, Apple's KEXT loader, and the built `Contents/MacOS/afs` kernel binary. The architecture and Darwin version in the filename are the selection mechanism.

## Risks And Test Signals
Risks are stale kernel dependency versions, wrong architecture/sysname selection, malformed XML/plist syntax, and placeholder substitution failures. Test signals include `plutil` validation, correct `Info.plist` placement in `afs.kext`, successful code signing or local development loading where applicable, and KEXT load diagnostics that accept the declared KPI/kernel dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_170.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_180.plist.in -->
# sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_180.plist.in

## Purpose
Darwin kernel-extension property-list template for the OpenAFS `afs` KEXT on the `x86` architecture family and Darwin `180` sysname. It supplies the bundle metadata copied by the Darwin libafs install/dest rules.

## Important APIs, Types, And Functions
The plist defines `CFBundleExecutable` `afs`, `CFBundleIdentifier` `org.openafs.filesystems.afs`, `CFBundleName` `afs`, `CFBundlePackageType` `KEXT`, version placeholders `@MACOS_VERSION@`, and `OSBundleLibraries` dependencies. This variant declares `com.apple.kpi.bsd`, `com.apple.kpi.mach`, and `com.apple.kpi.libkern` at `8.0.x`, with `CFBundleInfoDictionaryVersion` `8.0`.

## Control Flow
There is no executable flow. Configure/substitution fills `@MACOS_VERSION@`, Darwin make rules install the file as `Contents/Info.plist` inside `afs.kext`, and macOS KEXT loading uses the bundle keys and kernel-library dependency versions.

## State And Persistence
The file persists bundle identity and load requirements in the installed KEXT. It does not store runtime cache state or credentials.

## Dependencies And Integration Points
It integrates with `MakefileProto.DARWIN.in`, the generated Darwin `Info.plist`, Apple's KEXT loader, and the built `Contents/MacOS/afs` kernel binary. The architecture and Darwin version in the filename are the selection mechanism.

## Risks And Test Signals
Risks are stale kernel dependency versions, wrong architecture/sysname selection, malformed XML/plist syntax, and placeholder substitution failures. Test signals include `plutil` validation, correct `Info.plist` placement in `afs.kext`, successful code signing or local development loading where applicable, and KEXT load diagnostics that accept the declared KPI/kernel dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_180.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_190.plist.in -->
# sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_190.plist.in

## Purpose
Darwin kernel-extension property-list template for the OpenAFS `afs` KEXT on the `x86` architecture family and Darwin `190` sysname. It supplies the bundle metadata copied by the Darwin libafs install/dest rules.

## Important APIs, Types, And Functions
The plist defines `CFBundleExecutable` `afs`, `CFBundleIdentifier` `org.openafs.filesystems.afs`, `CFBundleName` `afs`, `CFBundlePackageType` `KEXT`, version placeholders `@MACOS_VERSION@`, and `OSBundleLibraries` dependencies. This variant declares `com.apple.kpi.bsd`, `com.apple.kpi.mach`, and `com.apple.kpi.libkern` at `8.0.x`, with `CFBundleInfoDictionaryVersion` `8.0`.

## Control Flow
There is no executable flow. Configure/substitution fills `@MACOS_VERSION@`, Darwin make rules install the file as `Contents/Info.plist` inside `afs.kext`, and macOS KEXT loading uses the bundle keys and kernel-library dependency versions.

## State And Persistence
The file persists bundle identity and load requirements in the installed KEXT. It does not store runtime cache state or credentials.

## Dependencies And Integration Points
It integrates with `MakefileProto.DARWIN.in`, the generated Darwin `Info.plist`, Apple's KEXT loader, and the built `Contents/MacOS/afs` kernel binary. The architecture and Darwin version in the filename are the selection mechanism.

## Risks And Test Signals
Risks are stale kernel dependency versions, wrong architecture/sysname selection, malformed XML/plist syntax, and placeholder substitution failures. Test signals include `plutil` validation, correct `Info.plist` placement in `afs.kext`, successful code signing or local development loading where applicable, and KEXT load diagnostics that accept the declared KPI/kernel dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_190.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_200.plist.in -->
# sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_200.plist.in

## Purpose
Darwin kernel-extension property-list template for the OpenAFS `afs` KEXT on the `x86` architecture family and Darwin `200` sysname. It supplies the bundle metadata copied by the Darwin libafs install/dest rules.

## Important APIs, Types, And Functions
The plist defines `CFBundleExecutable` `afs`, `CFBundleIdentifier` `org.openafs.filesystems.afs`, `CFBundleName` `afs`, `CFBundlePackageType` `KEXT`, version placeholders `@MACOS_VERSION@`, and `OSBundleLibraries` dependencies. This variant declares `com.apple.kpi.bsd`, `com.apple.kpi.mach`, and `com.apple.kpi.libkern` at `8.0.x`, with `CFBundleInfoDictionaryVersion` `8.0`.

## Control Flow
There is no executable flow. Configure/substitution fills `@MACOS_VERSION@`, Darwin make rules install the file as `Contents/Info.plist` inside `afs.kext`, and macOS KEXT loading uses the bundle keys and kernel-library dependency versions.

## State And Persistence
The file persists bundle identity and load requirements in the installed KEXT. It does not store runtime cache state or credentials.

## Dependencies And Integration Points
It integrates with `MakefileProto.DARWIN.in`, the generated Darwin `Info.plist`, Apple's KEXT loader, and the built `Contents/MacOS/afs` kernel binary. The architecture and Darwin version in the filename are the selection mechanism.

## Risks And Test Signals
Risks are stale kernel dependency versions, wrong architecture/sysname selection, malformed XML/plist syntax, and placeholder substitution failures. Test signals include `plutil` validation, correct `Info.plist` placement in `afs.kext`, successful code signing or local development loading where applicable, and KEXT load diagnostics that accept the declared KPI/kernel dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_200.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_210.plist.in -->
# sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_210.plist.in

## Purpose
Darwin kernel-extension property-list template for the OpenAFS `afs` KEXT on the `x86` architecture family and Darwin `210` sysname. It supplies the bundle metadata copied by the Darwin libafs install/dest rules.

## Important APIs, Types, And Functions
The plist defines `CFBundleExecutable` `afs`, `CFBundleIdentifier` `org.openafs.filesystems.afs`, `CFBundleName` `afs`, `CFBundlePackageType` `KEXT`, version placeholders `@MACOS_VERSION@`, and `OSBundleLibraries` dependencies. This variant declares `com.apple.kpi.bsd`, `com.apple.kpi.mach`, and `com.apple.kpi.libkern` at `8.0.x`, with `CFBundleInfoDictionaryVersion` `8.0`.

## Control Flow
There is no executable flow. Configure/substitution fills `@MACOS_VERSION@`, Darwin make rules install the file as `Contents/Info.plist` inside `afs.kext`, and macOS KEXT loading uses the bundle keys and kernel-library dependency versions.

## State And Persistence
The file persists bundle identity and load requirements in the installed KEXT. It does not store runtime cache state or credentials.

## Dependencies And Integration Points
It integrates with `MakefileProto.DARWIN.in`, the generated Darwin `Info.plist`, Apple's KEXT loader, and the built `Contents/MacOS/afs` kernel binary. The architecture and Darwin version in the filename are the selection mechanism.

## Risks And Test Signals
Risks are stale kernel dependency versions, wrong architecture/sysname selection, malformed XML/plist syntax, and placeholder substitution failures. Test signals include `plutil` validation, correct `Info.plist` placement in `afs.kext`, successful code signing or local development loading where applicable, and KEXT load diagnostics that accept the declared KPI/kernel dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_210.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_220.plist.in -->
# sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_220.plist.in

## Purpose
Darwin kernel-extension property-list template for the OpenAFS `afs` KEXT on the `x86` architecture family and Darwin `220` sysname. It supplies the bundle metadata copied by the Darwin libafs install/dest rules.

## Important APIs, Types, And Functions
The plist defines `CFBundleExecutable` `afs`, `CFBundleIdentifier` `org.openafs.filesystems.afs`, `CFBundleName` `afs`, `CFBundlePackageType` `KEXT`, version placeholders `@MACOS_VERSION@`, and `OSBundleLibraries` dependencies. This variant declares `com.apple.kpi.bsd`, `com.apple.kpi.mach`, and `com.apple.kpi.libkern` at `8.0.x`, with `CFBundleInfoDictionaryVersion` `8.0`.

## Control Flow
There is no executable flow. Configure/substitution fills `@MACOS_VERSION@`, Darwin make rules install the file as `Contents/Info.plist` inside `afs.kext`, and macOS KEXT loading uses the bundle keys and kernel-library dependency versions.

## State And Persistence
The file persists bundle identity and load requirements in the installed KEXT. It does not store runtime cache state or credentials.

## Dependencies And Integration Points
It integrates with `MakefileProto.DARWIN.in`, the generated Darwin `Info.plist`, Apple's KEXT loader, and the built `Contents/MacOS/afs` kernel binary. The architecture and Darwin version in the filename are the selection mechanism.

## Risks And Test Signals
Risks are stale kernel dependency versions, wrong architecture/sysname selection, malformed XML/plist syntax, and placeholder substitution failures. Test signals include `plutil` validation, correct `Info.plist` placement in `afs.kext`, successful code signing or local development loading where applicable, and KEXT load diagnostics that accept the declared KPI/kernel dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_220.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_230.plist.in -->
# sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_230.plist.in

## Purpose
Darwin kernel-extension property-list template for the OpenAFS `afs` KEXT on the `x86` architecture family and Darwin `230` sysname. It supplies the bundle metadata copied by the Darwin libafs install/dest rules.

## Important APIs, Types, And Functions
The plist defines `CFBundleExecutable` `afs`, `CFBundleIdentifier` `org.openafs.filesystems.afs`, `CFBundleName` `afs`, `CFBundlePackageType` `KEXT`, version placeholders `@MACOS_VERSION@`, and `OSBundleLibraries` dependencies. This variant declares `com.apple.kpi.bsd`, `com.apple.kpi.mach`, and `com.apple.kpi.libkern` at `8.0.x`, with `CFBundleInfoDictionaryVersion` `8.0`.

## Control Flow
There is no executable flow. Configure/substitution fills `@MACOS_VERSION@`, Darwin make rules install the file as `Contents/Info.plist` inside `afs.kext`, and macOS KEXT loading uses the bundle keys and kernel-library dependency versions.

## State And Persistence
The file persists bundle identity and load requirements in the installed KEXT. It does not store runtime cache state or credentials.

## Dependencies And Integration Points
It integrates with `MakefileProto.DARWIN.in`, the generated Darwin `Info.plist`, Apple's KEXT loader, and the built `Contents/MacOS/afs` kernel binary. The architecture and Darwin version in the filename are the selection mechanism.

## Risks And Test Signals
Risks are stale kernel dependency versions, wrong architecture/sysname selection, malformed XML/plist syntax, and placeholder substitution failures. Test signals include `plutil` validation, correct `Info.plist` placement in `afs.kext`, successful code signing or local development loading where applicable, and KEXT load diagnostics that accept the declared KPI/kernel dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_230.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_240.plist.in -->
# sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_240.plist.in

## Purpose
Darwin kernel-extension property-list template for the OpenAFS `afs` KEXT on the `x86` architecture family and Darwin `240` sysname. It supplies the bundle metadata copied by the Darwin libafs install/dest rules.

## Important APIs, Types, And Functions
The plist defines `CFBundleExecutable` `afs`, `CFBundleIdentifier` `org.openafs.filesystems.afs`, `CFBundleName` `afs`, `CFBundlePackageType` `KEXT`, version placeholders `@MACOS_VERSION@`, and `OSBundleLibraries` dependencies. This variant declares `com.apple.kpi.bsd`, `com.apple.kpi.mach`, and `com.apple.kpi.libkern` at `8.0.x`, with `CFBundleInfoDictionaryVersion` `8.0`.

## Control Flow
There is no executable flow. Configure/substitution fills `@MACOS_VERSION@`, Darwin make rules install the file as `Contents/Info.plist` inside `afs.kext`, and macOS KEXT loading uses the bundle keys and kernel-library dependency versions.

## State And Persistence
The file persists bundle identity and load requirements in the installed KEXT. It does not store runtime cache state or credentials.

## Dependencies And Integration Points
It integrates with `MakefileProto.DARWIN.in`, the generated Darwin `Info.plist`, Apple's KEXT loader, and the built `Contents/MacOS/afs` kernel binary. The architecture and Darwin version in the filename are the selection mechanism.

## Risks And Test Signals
Risks are stale kernel dependency versions, wrong architecture/sysname selection, malformed XML/plist syntax, and placeholder substitution failures. Test signals include `plutil` validation, correct `Info.plist` placement in `afs.kext`, successful code signing or local development loading where applicable, and KEXT load diagnostics that accept the declared KPI/kernel dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_240.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_250.plist.in -->
# sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_250.plist.in

## Purpose
Darwin kernel-extension property-list template for the OpenAFS `afs` KEXT on the `x86` architecture family and Darwin `250` sysname. It supplies the bundle metadata copied by the Darwin libafs install/dest rules.

## Important APIs, Types, And Functions
The plist defines `CFBundleExecutable` `afs`, `CFBundleIdentifier` `org.openafs.filesystems.afs`, `CFBundleName` `afs`, `CFBundlePackageType` `KEXT`, version placeholders `@MACOS_VERSION@`, and `OSBundleLibraries` dependencies. This variant declares `com.apple.kpi.bsd`, `com.apple.kpi.mach`, and `com.apple.kpi.libkern` at `8.0.x`, with `CFBundleInfoDictionaryVersion` `8.0`.

## Control Flow
There is no executable flow. Configure/substitution fills `@MACOS_VERSION@`, Darwin make rules install the file as `Contents/Info.plist` inside `afs.kext`, and macOS KEXT loading uses the bundle keys and kernel-library dependency versions.

## State And Persistence
The file persists bundle identity and load requirements in the installed KEXT. It does not store runtime cache state or credentials.

## Dependencies And Integration Points
It integrates with `MakefileProto.DARWIN.in`, the generated Darwin `Info.plist`, Apple's KEXT loader, and the built `Contents/MacOS/afs` kernel binary. The architecture and Darwin version in the filename are the selection mechanism.

## Risks And Test Signals
Risks are stale kernel dependency versions, wrong architecture/sysname selection, malformed XML/plist syntax, and placeholder substitution failures. Test signals include `plutil` validation, correct `Info.plist` placement in `afs.kext`, successful code signing or local development loading where applicable, and KEXT load diagnostics that accept the declared KPI/kernel dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_250.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_80.plist.in -->
# sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_80.plist.in

## Purpose
Darwin kernel-extension property-list template for the OpenAFS `afs` KEXT on the `x86` architecture family and Darwin `80` sysname. It supplies the bundle metadata copied by the Darwin libafs install/dest rules.

## Important APIs, Types, And Functions
The plist defines `CFBundleExecutable` `afs`, `CFBundleIdentifier` `org.openafs.filesystems.afs`, `CFBundleName` `afs`, `CFBundlePackageType` `KEXT`, version placeholders `@MACOS_VERSION@`, and `OSBundleLibraries` dependencies. This variant declares `com.apple.kpi.bsd`, `com.apple.kpi.mach`, and `com.apple.kpi.libkern` at `8.0.x`, with `CFBundleInfoDictionaryVersion` `8.0`.

## Control Flow
There is no executable flow. Configure/substitution fills `@MACOS_VERSION@`, Darwin make rules install the file as `Contents/Info.plist` inside `afs.kext`, and macOS KEXT loading uses the bundle keys and kernel-library dependency versions.

## State And Persistence
The file persists bundle identity and load requirements in the installed KEXT. It does not store runtime cache state or credentials.

## Dependencies And Integration Points
It integrates with `MakefileProto.DARWIN.in`, the generated Darwin `Info.plist`, Apple's KEXT loader, and the built `Contents/MacOS/afs` kernel binary. The architecture and Darwin version in the filename are the selection mechanism.

## Risks And Test Signals
Risks are stale kernel dependency versions, wrong architecture/sysname selection, malformed XML/plist syntax, and placeholder substitution failures. Test signals include `plutil` validation, correct `Info.plist` placement in `afs.kext`, successful code signing or local development loading where applicable, and KEXT load diagnostics that accept the declared KPI/kernel dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_80.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_90.plist.in -->
# sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_90.plist.in

## Purpose
Darwin kernel-extension property-list template for the OpenAFS `afs` KEXT on the `x86` architecture family and Darwin `90` sysname. It supplies the bundle metadata copied by the Darwin libafs install/dest rules.

## Important APIs, Types, And Functions
The plist defines `CFBundleExecutable` `afs`, `CFBundleIdentifier` `org.openafs.filesystems.afs`, `CFBundleName` `afs`, `CFBundlePackageType` `KEXT`, version placeholders `@MACOS_VERSION@`, and `OSBundleLibraries` dependencies. This variant declares `com.apple.kpi.bsd`, `com.apple.kpi.mach`, and `com.apple.kpi.libkern` at `8.0.x`, with `CFBundleInfoDictionaryVersion` `8.0`.

## Control Flow
There is no executable flow. Configure/substitution fills `@MACOS_VERSION@`, Darwin make rules install the file as `Contents/Info.plist` inside `afs.kext`, and macOS KEXT loading uses the bundle keys and kernel-library dependency versions.

## State And Persistence
The file persists bundle identity and load requirements in the installed KEXT. It does not store runtime cache state or credentials.

## Dependencies And Integration Points
It integrates with `MakefileProto.DARWIN.in`, the generated Darwin `Info.plist`, Apple's KEXT loader, and the built `Contents/MacOS/afs` kernel binary. The architecture and Darwin version in the filename are the selection mechanism.

## Risks And Test Signals
Risks are stale kernel dependency versions, wrong architecture/sysname selection, malformed XML/plist syntax, and placeholder substitution failures. Test signals include `plutil` validation, correct `Info.plist` placement in `afs.kext`, successful code signing or local development loading where applicable, and KEXT load diagnostics that accept the declared KPI/kernel dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_90.plist.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/make_kbuild_makefile.pl -->
# sources/distributed-fs/openafs/src/libafs/make_kbuild_makefile.pl

## Purpose
Generates a Linux 2.6+ Kbuild-compatible Makefile for OpenAFS kernel modules. It scans the already-generated libafs makefiles, resolves object lists and source dependencies, symlinks source files into the kernel build directory, creates compatibility include shims when needed, and writes Kbuild object/CFLAGS assignments for `libafs` and `afspag`.

## Important APIs, Types, And Functions
The command-line contract is `make_kbuild_makefile.pl KDIR TARG Makefiles...`. Important variables parsed from makefiles include `TOP_OBJDIR`, `TOP_SRCDIR`, `AFSAOBJS`, `AFSNFSOBJS`, `AFSPAGOBJS`, `COMMON_INCLUDE`, `CFLAGS`, `LINUX_KERNEL_PATH`, and `LINUX_KBUILD_CFLAGS_VAR`. Internal maps are `%vars`, `%deps`, `%all_objs`, `%remap`, and `%seen`.

## Control Flow
The script reads each makefile line-by-line, joins continuations, ignores comments, substitutes previously-seen `$(VAR)`/`${VAR}` references, stores variable assignments, and records `.o: .c` or `.o: .s` dependencies. It special-cases `AFS_component_version_number.o`, computes target object lists, creates `TOP_OBJDIR/src/libafs/KDIR`, symlinks source files with `.c` or `.S` names, sets up `h`, `netinet`, and `sys` mappings either as Linux header symlinks or generated wrapper directories, recursively scans includes for shim headers on older layouts, and writes the Kbuild Makefile with per-object flags plus `obj-m`, target objects, and `afspag-objs`.

## State And Persistence
Persistent state is the generated Kbuild directory: symlinked sources, include shims, and `Makefile`. Existing generated source links with matching names are unlinked and recreated. The script does not modify the original makefiles or runtime system state.

## Dependencies And Integration Points
It is invoked by `MakefileProto.LINUX.in` before running `make -C LINUX_KERNEL_BUILD M=... modules`. It depends on Perl `IO::File`, OpenAFS makefile variable ordering, kernel header layout, and complete object dependency rules in `Makefile.common`/`Makefile.afs`.

## Risks And Test Signals
Risks include simplistic makefile parsing, variables used before assignment, one-dependency assumptions, shell conditionals not represented in the parsed text, stale symlinks, crude recursive deletion for remap directories, and missing/unrecognized include syntax. Useful signals are a generated `Makefile` with all expected object lists, no `No source known` failures, successful `libafs.ko` and `afspag.ko` Kbuild builds, and warning-free `.makelog` scanning by the Linux proto makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/make_kbuild_makefile.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafsauthent/Makefile.in -->
# sources/distributed-fs/openafs/src/libafsauthent/Makefile.in

## Purpose
Builds the pthread-safe `libafsauthent` authentication/client support library by combining PIC/static OpenAFS audit, auth, kauth, ubik, sys, protection, volser, vlserver, opr, and util libraries with libafsrpc and crypto/roken/system libraries.

## Important APIs, Types, And Functions
Important make variables are libtool version fields `LT_current`, `LT_revision`, `LT_age`, `LT_objs`, `LT_deps`, `LT_libs`, optional `SHARED_LIBS`, and targets `libafsauthent.la`, `libafsauthent_pic.la`, `libafsauthent.a`, top-libdir archive installs, `install`, `dest`, and `clean`.

## Control Flow
`all` builds shared libraries when enabled, the PIC libtool archive, and static/PIC archives under `TOP_LIBDIR`. Shared linking uses `LT_LDLIB_shlib_only`; PIC and static archives use separate libtool invocations because AIX cannot produce both modes in one call. Install places shared/static artifacts in `${libdir}` and destination staging places the static archive in `${DEST}/lib`.

## State And Persistence
Persistent outputs are libtool archives, `.libs/libafsauthent_pic.a`, `libafsauthent.a`, and installed library files. No runtime authentication state is modified; this is build composition only.

## Dependencies And Integration Points
It includes `Makefile.config` and `Makefile.libtool`, depends on the listed component libraries and `libafsrpc`, and supplies a reusable auth/admin client library for other OpenAFS tools.

## Risks And Test Signals
Risks include libtool versioning mistakes, missing PIC variants, AIX shared/static behavior, dependency ordering, and shared-library install cleanup. Test signals are successful static/PIC/shared builds, correct exported symbols from `libafsauthent.la.sym`, install/dest staging, and downstream tool links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafsauthent/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/Makefile.in -->
# sources/distributed-fs/openafs/src/libafscp/Makefile.in

## Purpose
Builds and installs the static `libafscp.a` client-side AFS protocol helper library and its public header `afs/afscp.h`. The library wraps cell/server discovery, file, directory, volume, ACL, callback, and utility operations for lightweight AFS clients.

## Important APIs, Types, And Functions
The main variables are `LIBOBJS`, `KRB5CPPFLAGS`, object-specific `CFLAGS_afscp_util.o`, `CPPFLAGS_afscp_util.o`, and `CPPFLAGS_afscp_server.o`. Targets include `all`, `${TOP_LIBDIR}/libafscp.a`, `libafscp.a`, `depinstall`, `${TOP_INCDIR}/afs/afscp.h`, `install`, `dest`, and `clean`.

## Control Flow
Object files are archived with `AR` and indexed with `RANLIB`, then installed into the top build library directory. `depinstall` publishes the header and ensures component-version generation. Install/dest targets stage both the archive and public header.

## State And Persistence
Persistent outputs are `libafscp.a`, `AFS_component_version_number.c`, and installed headers/libraries. No runtime cache or callback state is changed by the makefile.

## Dependencies And Integration Points
It includes `Makefile.config`, `Makefile.pthread`, Kerberos CPP flags, `Makefile.version`, and source files in `src/libafscp`. The archive is consumed by utilities needing direct AFS file protocol access.

## Risks And Test Signals
Risks include missing objects from `LIBOBJS`, stale header installation, missing Kerberos flags for server/util code, and non-PIC/static-only assumptions. Test signals are a clean archive rebuild, installed header availability, and downstream links using `afscp_*` APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/afscp.h -->
# sources/distributed-fs/openafs/src/libafscp/afscp.h

## Purpose
Defines the public libafscp client API and shared data structures for cells, servers, volumes, FIDs, directory streams, stat/directory caches, open files, and callback tracking. It is the main consumer-facing header for lightweight OpenAFS file-protocol operations.

## Important APIs, Types, And Functions
Core structs include `afscp_server`, `afscp_cell`, `afscp_volume`, `afscp_venusfid`, `afscp_dirent`, `afscp_dirstream`, `afscp_dircache`, `afscp_statent`, `afscp_openfile`, and `afscp_callback`. The API covers initialization/auth (`afscp_Init`, `afscp_Finalize`, `afscp_Insecure`, `afscp_AnonymousAuth`, `afscp_LocalAuthAs`), cell/server lookup, callback management, FID allocation, stat/read/write, RPC wrappers, ACL fetch/store, directory parsing/path resolution, volume lookup, and directory mode selection.

## Control Flow
Consumers initialize the library and authentication, resolve cells/servers/volumes/FIDs, perform file or directory RPC wrappers, and maintain callbacks/stat caches through the callback helpers. The header documents ownership for FID helpers and uses `afscp_errno` as the library error channel.

## State And Persistence
The header declares no storage except `afscp_errno`, but its structures describe persistent in-process state: Rx security classes, ubik VL clients, server Rx connections, volume caches, stat and directory caches guarded by pthread mutex/condition variables, and callback expiration data. Runtime persistence is memory-only.

## Dependencies And Integration Points
It depends on OpenAFS protocol headers (`afsint`, constants, cell config, directory format, util) and pthreads on Windows. It is installed as `afs/afscp.h` by `libafscp/Makefile.in` and implemented by sibling `afscp_*.c` files.

## Risks And Test Signals
Risks include ABI exposure of internal structs, global `afscp_errno`, thread-safety assumptions around shared caches/callbacks, fixed-size names/address arrays, and API declarations drifting from implementation. Test signals are compile coverage for consumers, initialization/auth smoke tests, path resolution, stat/read/write, ACL, callback invalidation, and multithreaded cache wait behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/afscp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/afscp_acl.c -->
# sources/distributed-fs/openafs/src/libafscp/afscp_acl.c

## Purpose
Implements libafscp ACL fetch and store wrappers for AFS directories. It locates the volume and file servers for a directory FID, tries each server address, calls the RXAFS ACL RPC, updates local stat cache on success, and invalidates stat cache plus sets `afscp_errno` on failure.

## Important APIs, Types, And Functions
The exported functions are `afscp_FetchACL` and `afscp_StoreACL`. Important dependencies are `afscp_VolumeById`, `afscp_ServerByIndex`, `RXAFS_FetchACL`, `RXAFS_StoreACL`, `RXAFS_OldStoreACL`, `_StatStuff`, `_StatInvalidate`, `AFSOpaque`, `AFSFetchStatus`, `AFSVolSync`, and `AFSFid`.

## Control Flow
Both functions resolve the volume from the FID's cell and volume id, then iterate volume server indexes and each server address. Fetch calls `RXAFS_FetchACL`, validates returned ACL data as a NUL-terminated non-empty string, and breaks on the first nonnegative RPC result. Store calls `RXAFS_StoreACL`, falling back to `RXAFS_OldStoreACL` on `RXGEN_OPCODE`. Success updates cached status; failure invalidates the stat cache and returns `-1`.

## State And Persistence
The functions mutate the caller-provided ACL buffer for fetch, remote ACL state for store, local stat cache entries through `_StatStuff` or `_StatInvalidate`, and global `afscp_errno`. They do not allocate persistent local state.

## Dependencies And Integration Points
This file integrates libafscp FID/volume/server lookup with fileserver ACL RPCs and the local stat-cache implementation from `afscp_internal.h`. It is archived into `libafscp.a`.

## Risks And Test Signals
Risks include interpreting negative/nonnegative RPC status incorrectly, partial ACL buffers from failed fetches, malformed ACL validation edge cases, fallback compatibility with old fileservers, and trying stale server connections before valid ones. Useful tests include fetch/store against modern and old fileservers, malformed ACL response handling, multi-address retry, missing volume errors, and stat-cache invalidation/update verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/afscp_acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/afscp_callback.c -->
# sources/distributed-fs/openafs/src/libafscp/afscp_callback.c

## Purpose
Implements libafscp callback tracking and the minimal Cache Manager callback RPC service that fileservers expect from an AFS client. It records callbacks for fetched FIDs, expires and invalidates stat cache entries, returns callbacks to servers, and responds to server callback RPCs such as break-callback, probe, who-are-you, and init-callback-state.

## Important APIs, Types, And Functions
Important globals are `afs_cb_inited`, `afs_cb_interface`, `afscp_maxcallbacks`, `afscp_cballoced`, and `allcallbacks`. Public helpers include `afscp_FindCallBack`, `afscp_AddCallBack`, `afscp_RemoveCallBack`, `afscp_ReturnCallBacks`, and `afscp_ReturnAllCallBacks`. Server-side RPC handlers include `SRXAFSCB_CallBack`, `SRXAFSCB_InitCallBackState`, `SRXAFSCB_Probe`, `SRXAFSCB_GetLock`, `SRXAFSCB_GetCE`, `SRXAFSCB_GetCE64`, `SRXAFSCB_XStatsVersion`, `SRXAFSCB_GetXStats`, `SRXAFSCB_InitCallBackState2`, `SRXAFSCB_TellMeAboutYourself`, `SRXAFSCB_WhoAreYou`, `SRXAFSCB_InitCallBackState3`, `SRXAFSCB_ProbeUuid`, `SRXAFSCB_GetServerPrefs`, `SRXAFSCB_GetCellServDB`, `SRXAFSCB_GetLocalCell`, `SRXAFSCB_GetCacheConfig`, and `SRXAFSCB_GetCellByNum`.

## Control Flow
`init_afs_cb` creates a client UUID and records interface addresses using Windows `syscfg_GetIFInfo` or Unix `rx_getAllAddr`. Callback lookup scans the global array for matching FID/server, expires old entries, and invalidates stats if necessary. Add scans for expired/free or matching slots, grows the array by doubling from four entries, stores callback metadata, and updates stat cache from fetch status. Remove and server break/init callbacks clear validity and invalidate stats. Return paths batch valid callbacks up to `AFSCBMAX`, mark them `CB_DROPPED`, call `RXAFS_GiveUpCallBacks` over server addresses, clear local entries, and free the global list on return-all. Most diagnostic callback RPCs return success with minimal data or `RXGEN_OPCODE` for unsupported queries.

## State And Persistence
State is memory-only: callback records, callback UUID/interface address, validity flags, expiration base times, and stat-cache side effects. `SRXAFSCB_TellMeAboutYourself` allocates capabilities data via `xdr_alloc` for the RPC response. No disk state is persisted.

## Dependencies And Integration Points
The file depends on Rx callback server stubs, fileserver RPCs, `afsutil`, `afscp_internal` stat cache helpers, server lookup by address/index, and platform network-interface discovery. It lets libafscp behave enough like a cache manager for fileservers to grant and revoke callbacks.

## Risks And Test Signals
Risks include unsynchronized global callback arrays in multithreaded callers, subtle expiration arithmetic, invalidation in nested loops, allocation ownership of capabilities buffers, minimal stub responses that may not satisfy newer server diagnostics, UUID/interface handling differences on Windows, and return-callback batching errors. Tests should cover callback add/find/expire/remove, server break callbacks, init-state invalidation, return-all cleanup, probe UUID mismatch, interface reporting, stat-cache invalidation, and concurrent access if libafscp is used from multiple threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/afscp_callback.c -->
