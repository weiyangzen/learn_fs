<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/viced/Makefile.in -->
# sources/distributed-fs/openafs/src/viced/Makefile.in

## Purpose
Builds the OpenAFS fileserver and related diagnostic utilities from `src/viced`, while pulling in directory, volume, fsint, synchronization, crypto, Rx, and utility libraries.

## Important APIs, Types, And Functions
Important targets are `all`, `${TOP_INCDIR}/afs/fs_stats.h`, `check_sysid`, `fsprobe`, `cbd`, `fileserver`, `install`, `dest`, and `clean`. Object groups are `VICEDOBJS`, `DIROBJS`, `VOLOBJS`, `FSINTOBJS`, and aggregate `objects`. `MODULE_CFLAGS` enables `RXDEBUG`, `FSSYNC_BUILD_SERVER`, and `SALVSYNC_BUILD_CLIENT`.

## Control Flow
The makefile includes configured build rules and pthread settings, defines source directories for `../dir` and `../vol`, compiles local files plus selected directory and volume sources into local objects, generates/uses `AFS_component_version_number.c`, links helper tools (`check_sysid`, `fsprobe`, `cbd`), links the static `fileserver`, and installs it under server libexec/sbin or dest tree paths. The clean target removes libtool artifacts, objects, generated version file, tools, and `fileserver`.

## State And Persistence
Build outputs include object files, `fileserver`, `cbd`, `check_sysid`, `fsprobe`, generated component version source, and installed binaries/headers. The makefile does not manage runtime fileserver state.

## Dependencies And Integration Points
It integrates `viced` with `src/dir`, `src/vol`, `src/fsint`, VLDB, RxKAD, RxStat, LWP compatibility, ACL, cmd, opr, util, hcrypto, roken, pthread, and platform linker exports for AIX. It installs `fs_stats.h` into the top include directory for consumers.

## Risks And Test Signals
Risks include object list drift when source files change, mismatched compile flags for shared volume/dir sources, static link order sensitivity, generated version-file dependencies, and platform-specific linker flags. Test signals are clean rebuilds, `make install DESTDIR=...`, AIX link coverage, helper tool execution, and fileserver startup against fssync/salvsync-enabled volume code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/viced/Makefile.in -->
