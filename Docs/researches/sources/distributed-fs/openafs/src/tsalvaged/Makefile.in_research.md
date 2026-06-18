# sources/distributed-fs/openafs/src/tsalvaged/Makefile.in

## Purpose
Builds demand-attach fileserver salvage tools in a pthreaded layout: `salvageserver`, `dasalvager`, `dafssync-debug`, and `salvsync-debug`. It reuses volume and directory sources with normal and salvage-specific compile flags.

## Important APIs, Types, And Functions
Major object groups are `SALVAGEDOBJS`, `SALVAGEROBJS`, `DIROBJS`, `SDIROBJS`, `VLIBOBJS`, `SVLIBOBJS`, `FSSDEBUG_OBJS`, and `SSSDEBUG_OBJS`. `MODULE_CFLAGS` and `SCFLAGS` enable `RXDEBUG`, FSSYNC/SALVSYNC client/server support, and `AFS_DEMAND_ATTACH_FS`. Targets include all objects mapped from `../vol` and `../dir`, plus install/dest/clean.

## Control Flow
Normal salvageserver/debug objects use `AFS_CCRULE`; salvage-specific `s_*` objects use `SCCRULE` with pthread and demand-attach flags. The four binaries link statically with sys, Rx, util, cmd, lwpcompat, opr, crypto, roken, and crypt libraries. Install and dest targets place the salvage binaries into configured server libexec/sbin or legacy root.server paths.

## State And Persistence
The makefile produces build artifacts and installs server-side binaries. Runtime state such as volume partitions, salvage queues, and FSSYNC/SALVSYNC sockets is only affected when the built programs run.

## Dependencies And Integration Points
This wrapper integrates volume subsystem sources, directory package sources, daemon communication, fssync/salvsync client/server code, and pthread build settings. It is tied to demand-attach fileserver support through compile defines and the `salvsync-debug.c` command.

## Risks And Test Signals
Risks include duplicated object builds with different flags, missing demand-attach defines causing unsupported binaries, and link-order sensitivity across volume/dir/lwp/rx libraries. Signals include a full `make all`, install path checks, `salvsync-debug` build only with demand-attach flags, and clean removal of generated objects/binaries.
