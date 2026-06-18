# sources/distributed-fs/openafs/src/xstat/Makefile.in

## Purpose

`src/xstat/Makefile.in` builds and installs the OpenAFS extended statistics client libraries and test tools for file-server (`xstat_fs`) and cache-manager (`xstat_cm`) statistics collection.

## Important Targets and Variables

- Includes `Makefile.config`, `Makefile.pthread`, and `Makefile.libtool`, so the module uses configured compiler, pthread, install, and libtool rules.
- `LT_deps` links against rxkad, fsint, cmd, util, and opr libtool libraries.
- `all` builds shared/static xstat libraries, installs generated public headers into `${TOP_INCDIR}/afs`, installs static archives into `${TOP_LIBDIR}`, and builds `xstat_fs_test` and `xstat_cm_test`.
- File-server targets build `liboafs_xstat_fs.la`, `libxstat_fs.a`, generated callback server stubs `afscbint.ss.c/.h`, and `xstat_fs_test`.
- Cache-manager targets build `liboafs_xstat_cm.la`, `libxstat_cm.a`, and `xstat_cm_test`.
- `install` and `dest` copy headers, static libraries, and test programs to configured or legacy destination trees.
- `clean` removes libtool outputs, generated callback stubs, archives, tests, core files, and component-version source.

## Control Flow

The build first ensures exported headers and libraries are available under top-level include/library directories. FS library builds include `xstat_fs.lo`, `xstat_fs_callback.lo`, generated `afscbint.ss.lo`, and component version metadata. CM library builds include `xstat_cm.lo` and component version metadata. Test binaries statically link their respective libtool libraries plus shared dependencies and roken/platform libraries.

## State and Persistence Behavior

Build outputs are local artifacts: `.lo`, `.o`, `.la`, `.a`, generated `afscbint.*`, `AFS_component_version_number.c`, installed headers/libraries, and test binaries. No runtime state is managed here.

## Dependencies and Integration Points

This makefile integrates the xstat sources with the OpenAFS top-level build, libtool abstraction, generated fsint callback stubs, Rx/RxKAD, command parsing, util, opr, roken, and platform `XLIBS`. Public consumers get `afs/xstat_fs.h`, `afs/xstat_cm.h`, `libxstat_fs.a`, and `libxstat_cm.a`.

## Risks and Test Signals

Risks include stale generated `afscbint` stubs, missing dependency libraries, divergence between libtool shared/static rules, and install/dest path differences. Signals are successful `make all`, `make install DESTDIR=...`, `make clean && make`, and execution/linking of `xstat_fs_test`/`xstat_cm_test` in a configured tree.
