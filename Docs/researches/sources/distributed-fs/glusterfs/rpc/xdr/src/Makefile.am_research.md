# sources/distributed-fs/glusterfs/rpc/xdr/src/Makefile.am

## Purpose

`sources/distributed-fs/glusterfs/rpc/xdr/src/Makefile.am` builds GlusterFS's RPC XDR support library `libgfxdr.la`. It combines rpcgen-generated C/header files from `.x` protocol descriptions with handwritten helper sources such as `xdr-generic.c`, `xdr-custom.c`, and optional GNFS/NFSv3 wrappers. The source was read as a complete 85-line file for this report.

## Important APIs, Types, and Functions

Important build variables are `NFS_XDRS`, `NFS_SRCS`, `NFS_HDRS`, `XDRGENFILES`, `XDRHEADERS`, `XDRSOURCES`, `libgfxdr_la_SOURCES`, `nodist_libgfxdr_la_SOURCES`, `libgfxdr_la_HEADERS`, and `nodist_libgfxdr_la_HEADERS`. It exports headers under `$(includedir)/glusterfs/rpc`, links against `libglusterfs.la`, applies `LIBGFXDR_LT_VERSION`, and restricts exported symbols through `libgfxdr.sym`.

## Control Flow

Automake builds generated headers and sources from `.x` files via explicit `rpcgen` rules. Header generation runs `rpcgen -h`, then uses `sed` to normalize include guards for hyphenated `.x` names. Source generation runs `rpcgen -c` only when the generated output is missing or stale. A `.PHONY` rule links `.x` files into the build directory for out-of-tree builds so rpcgen emits clean local include directives.

## State and Persistence Behavior

Generated `.c`, `.h`, and out-of-tree symlinked `.x` files are build artifacts. `CLEANFILES` removes generated sources/headers, and `clean-local` removes linked `.x` files in out-of-tree builds. The file itself has no runtime state.

## Dependencies and Integration Points

The build depends on rpcgen, sed, Automake/libtool, generated protocol descriptions (`glusterfs4-xdr.x`, `cli1-xdr.x`, `rpc-common-xdr.x`, `glusterd1-xdr.x`, `changelog-xdr.x`, `portmap-xdr.x`, and optional NFS `.x` files), `libglusterfs.la`, and include paths for `libglusterfs`, `rpc-lib`, and builddir XDR outputs. `BUILD_GNFS` controls whether NFSv3/NLM/ACL XDRs and helper sources are part of `libgfxdr`.

## Risks and Edge Cases

The custom rpcgen rules avoid noisy failures when make tries to regenerate existing files unnecessarily; changes can reintroduce flaky builds. Out-of-tree symlink handling is fragile because rpcgen include paths depend on current working directory. `BUILD_GNFS` must keep generated NFS headers and handwritten `msg-nfs3`/`xdr-nfs3` sources in sync. Header guard `sed` expressions are portability-sensitive.

## Test Signals

Signals include in-tree and out-of-tree builds, `make clean` followed by rebuild, builds with and without `BUILD_GNFS`, generated header include guard inspection, symbol export checks for `libgfxdr.la`, and platforms with different sed/rpcgen behavior.
