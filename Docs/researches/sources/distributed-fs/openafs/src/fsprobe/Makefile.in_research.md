# sources/distributed-fs/openafs/src/fsprobe/Makefile.in

## Purpose
Builds the file-server probe library and test program, including callback server stubs needed for FileServer callback traffic.

## Important APIs, Types, And Functions
Targets include `liboafs_fsprobe.la`, `libfsprobe.a`, installed `fsprobe.h`, generated/copy targets for `afscbint.h` and `afscbint.ss.c`, `fsprobe_test`, install/dest, and clean. Objects are `fsprobe.lo`, `fsprobe_callback.lo`, `afscbint.ss.lo`, and `AFS_component_version_number.lo`.

## Control Flow
The default target builds the shared library, installs the public header into `TOP_INCDIR`, creates the static library, and links `fsprobe_test`. The makefile copies generated callback server files from `src/fsint` because `RXAFSCB_ExecuteRequest` is required by the probe's callback listener.

## State And Persistence
Build artifacts include libtool objects, `libfsprobe.a`, `liboafs_fsprobe.la`, copied generated callback files, `fsprobe_test`, and version files.

## Dependencies And Integration Points
Depends on rxkad, fsint, cmd, util, opr, volser, roken, pthread config, and libtool. Provides the library consumed by monitoring/probe tools.

## Risks And Test Signals
The library is sensitive to fsint generated-stub changes and rx/volser ABI changes. Tests should verify clean builds, copied callback stub freshness, static and shared link success, and `fsprobe_test` link against current dependency libraries.
