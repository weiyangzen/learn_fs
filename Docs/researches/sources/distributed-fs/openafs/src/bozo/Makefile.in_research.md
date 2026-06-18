# sources/distributed-fs/openafs/src/bozo/Makefile.in

## Purpose
Builds the OpenAFS bosserver, bos client utilities, generated BOS RPC files, error tables, headers, and `libbos.a`.

## Important APIs, Types, and Functions
Defines generated targets from `bosint.xg` via `RXGEN`, error/header generation from `boserr.et` via `COMPILE_ET_*`, core object list `OBJS`, library dependency ordering `LIBS`, and install/dest/test/clean targets.

## Control Flow
`all` builds `bosserver`, generated headers, `bos`, `libbos.a`, and `bos_util`. Generated RPC C/header files feed object dependencies. Install/dest copy binaries, headers, and libraries, but skip installing server binaries when pthreaded BOS is enabled.

## State and Persistence
Build outputs include generated `.c`/`.h`, objects, binaries, static library, and component version files. Install targets write into configured DESTDIR/DEST trees.

## Dependencies and Integration Points
Includes OpenAFS config and LWP make fragments. Links many subsystem libraries: rx, lwp, cmd, kauth, volser, vldb, auth, rxkad, ubik, audit, util, opr, sys, procmgmt, RFC3961, and hcrypto.

## Risks and Test Signals
Library ordering is significant, including repeated rx/lwp entries. Generated-file dependencies must remain accurate or parallel builds can race. Test signal is successful generation/build/install across LWP and pthread BOS configurations plus `make test` delegation to the test subdirectory.
