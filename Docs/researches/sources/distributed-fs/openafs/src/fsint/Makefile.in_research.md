# sources/distributed-fs/openafs/src/fsint/Makefile.in

## Purpose
Generates and builds the AFS file server and callback RPC interface code from rxgen `.xg` specifications.

## Important APIs, Types, And Functions
Targets include `depinstall`, `generated`, `liboafs_fsint.la`, `libfsint_pic.la`, `libafsint.a`, install/dest, and clean. Generated files include `Kcallback.*`, `Kvice.*`, `Kpagcb.*`, `afsint.*`, `afscbint.*`, and `pagcb.h`.

## Control Flow
The default target installs generated headers, regenerates all rxgen outputs, and builds shared/PIC/static libraries. Rxgen invocations select client stubs (`-C`), server stubs (`-S`), XDR (`-c`/`-y -c`), headers (`-h`), kernel variants (`-k`), and AFS options (`-A -x`). Install targets copy the static library and public headers into AFS lib/include destinations.

## State And Persistence
Build outputs are generated C/header files, libtool objects, static libraries, shared-library artifacts, and installed headers. Clean removes generated interface files and objects.

## Dependencies And Integration Points
This makefile is central to the OpenAFS RPC ABI. `fsprobe`, cache managers, file servers, kernel code, and callback listeners depend on the generated interfaces and libraries.

## Risks And Test Signals
Any rxgen rule or dependency drift can desynchronize headers and stubs. Test signals are clean-tree regeneration, successful library builds, no stale generated files after source `.xg` changes, install header consistency, and downstream compile coverage for users such as `fsprobe`.
