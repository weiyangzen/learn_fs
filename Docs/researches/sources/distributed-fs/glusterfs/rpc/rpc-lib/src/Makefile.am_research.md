## sources/distributed-fs/glusterfs/rpc/rpc-lib/src/Makefile.am

Purpose: this file builds and installs the core GlusterFS RPC library, `libgfrpc.la`.

Important build definitions: `libgfrpc_la_SOURCES` includes authentication modules, `rpcsvc.c`, `rpc-transport.c`, XDR glue, `rpc-clnt.c`, DRC, ping, autoscaling, and management portmap signout. `libgfrpc_la_HEADERS` installs public RPC headers such as `rpcsvc.h`, `rpc-transport.h`, `rpc-clnt.h`, `rpcsvc-common.h`, protocol headers, DRC, ping, and message IDs. `libgfrpc_la_LIBADD` links against `libglusterfs.la` and `libgfxdr.la`. `libgfrpc_la_LDFLAGS` applies version info, GlusterFS link flags, and exported symbols from `libgfrpc.sym`.

Control flow: Automake compiles the listed C files into one libtool library and installs headers under `$(includedir)/glusterfs/rpc`. `AM_CPPFLAGS` injects source/build XDR include paths, libglusterfs includes, the runtime `RPC_TRANSPORTDIR` string used by `rpc_transport_load`, and the rbtree contrib include.

State and persistence: build-time only. Its installed headers and library define the ABI consumed by translators and daemons.

Dependencies and integration: strongly coupled to XDR generated sources, libglusterfs, transport plugin directory layout, and symbol export control.

Risks: omitting a source can produce missing runtime features while still compiling if symbols are not referenced in a given build. Changing installed headers or export symbols affects downstream ABI. The literal `RPC_TRANSPORTDIR` must match install layout for dynamic transport loading.

Test signals: full build/link, installed-header compile tests, symbol export checks, and runtime transport load tests.
