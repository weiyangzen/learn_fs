<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxstat/Makefile.in -->
# sources/distributed-fs/openafs/src/rxstat/Makefile.in

## Purpose

This makefile builds the Rx statistics RPC support library. It generates client, server, and XDR stubs from `rxstat.xg`, compiles the handwritten `rxstat.c` service wrapper, and produces static, PIC, and libtool shared-library forms for consumers that expose or call RX RPC statistics services.

## Important Targets and Variables

`LT_objs` lists the libtool objects: `rxstat.cs.lo`, `rxstat.ss.lo`, `rxstat.xdr.lo`, and `rxstat.lo`. `LT_deps` points to `src/rx/liboafs_rx.la`, and the makefile includes OpenAFS config plus LWP/LWP-tool build rules.

The default `all` target runs `depinstall`, builds `liboafs_rxstat.la`, builds `librxstat_pic.la`, and installs `${TOP_LIBDIR}/librxstat.a`. The `generated` target creates both normal and kernel-style generated stubs:

- normal: `rxstat.cs.c`, `rxstat.ss.c`, `rxstat.xdr.c`, `rxstat.h`
- kernel-style: `Krxstat.cs.c`, `Krxstat.ss.c`, `Krxstat.xdr.c`

`depinstall` installs `${TOP_INCDIR}/rx/rxstat.h` and ensures kernel-style generated sources exist. `install` and `dest` place `rxstat.h` and `librxstat.a` into staged include/lib directories.

## Control Flow

`RXGEN` creates generated sources from `rxstat.xg`. The normal rules use `-A -x` for RXGEN output and choose client (`-C`), server (`-S`), XDR (`-c`), or header (`-h`) generation. Kernel variants use `-x -k`. The generated `.c` files depend on `rxstat.h`, ensuring the header is created first when building stubs.

`librxstat.a` is linked from libtool objects using `$(LT_LDLIB_lwp)`. Shared and PIC libraries use the OpenAFS libtool helper macros and, for `liboafs_rxstat.la`, an explicit symbol file and the Rx library dependency.

## State and Persistence Behavior

Build state consists of generated `rxstat.*` and `Krxstat.*` files, libtool object files, static/PIC/shared libraries, and installed header/library outputs. The makefile has no runtime state. `clean` invokes `$(LT_CLEAN)` and removes generated RPC files, object archives, core files, and component version output.

## Dependencies and Integration Points

The makefile ties together `rxstat.xg`, generated Rx RPC stubs, the handwritten `rxstat.c` RPC manager implementation, the core Rx library, LWP build machinery, and top-level include/library install locations. Consumers depend on `${TOP_INCDIR}/rx/rxstat.h` and `${TOP_LIBDIR}/librxstat.a` or the libtool libraries.

## Risks and Edge Cases

Generated files must stay synchronized with `rxstat.xg`; stale generated headers can cause mismatched RPC signatures. The kernel-style generated files are created in `depinstall` but are not part of `LT_objs`, so build scripts that need kernel stubs must depend on `generated` or `depinstall` explicitly. Symbol export coverage depends on `liboafs_rxstat.la.sym`; missing symbols there would affect shared-library consumers even if static builds pass.

## Test Signals

Run `make generated`, `make all`, `make install DESTDIR=/tmp/stage`, and `make clean`. Confirm that `rxstat.h` installs under both top include and staged include paths, and that static/PIC/shared library variants contain the generated client/server/XDR objects plus `rxstat.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxstat/Makefile.in -->
